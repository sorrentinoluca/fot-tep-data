"""Truth-free R08 adapter from the two immutable response stores to frozen R07 rows.

The four-field classifier is the S08-pinned deployed-parser normalization rule.
This adapter neither opens evaluator labels nor computes correctness.
"""

from collections import Counter
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3
import sys

GPTOSS_BACKUP_SHA = '32d2817b37e213670407ed5f97a9f90e95c07625755c8ee47fe4f6b08dceeb1a'
QWEN_NORMALIZED_SHA = 'bbfae74804a7ee6cddbfd4c0d3cd167b2ba18d68b1d14703af353a3d6664ed17'
QWEN_CLASSIFIER_SHA = '04925e99598cf80996e93f7cfdfe50cb66beaff0a82a046da35e637e5b281139'
GPTOSS_REQUESTS_SHA = 'f78c96b12f6fb52aade6f8d52de0c5a4a5a34a5f832be8dbd7b14b99aa6e18f6'
ARMS = {'A0','B0','FULL','SELF','AGG','S0','PL0'}


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):
            digest.update(block)
    return digest.hexdigest()


def main(gptoss_backup, qwen_normalized, classifier_path, request_grid, output):
    if Path(output).exists():
        raise FileExistsError(output)
    for path,expected in ((gptoss_backup,GPTOSS_BACKUP_SHA),(qwen_normalized,QWEN_NORMALIZED_SHA),
                          (classifier_path,QWEN_CLASSIFIER_SHA),(request_grid,GPTOSS_REQUESTS_SHA)):
        if sha(path)!=expected:
            raise ValueError(f'pinned input digest differs: {path}')
    spec=spec_from_file_location('pinned_qwen_classifier',classifier_path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    rows={}
    qcounts=Counter()
    with Path(qwen_normalized).open(encoding='utf-8') as stream:
        for line in stream:
            source=json.loads(line)
            key=source['key']
            if key in rows or source['attempts']!=1 or key.split('|')[2] not in ARMS:
                raise ValueError('Qwen normalized grid/attempt differs')
            if source['state'] not in {'valid','abstain','invalid','truncated'}:
                raise ValueError('Qwen terminal state differs')
            rows[key]={'model':'qwen','key':key,'state':source['state'],'predicted_label':source['predicted_label'],
                       'attempts':source['attempts'],'recoverable_transport_attempts':0}
            qcounts[source['state']]+=1
    if len(rows)!=14336:
        raise ValueError('Qwen key count differs')
    ledger_to_scientific={}
    with Path(request_grid).open(encoding='utf-8') as stream:
        for line in stream:
            request=json.loads(line)
            ledger_key=request['key']
            scientific_key=request['pair_id']+'|'+request['arm']
            if ledger_key in ledger_to_scientific or scientific_key not in rows:
                raise ValueError('gpt-oss request identity differs')
            ledger_to_scientific[ledger_key]=scientific_key
    if len(ledger_to_scientific)!=14336 or set(ledger_to_scientific.values())!=set(rows):
        raise ValueError('gpt-oss request grid differs')
    gcounts=Counter()
    gkeys=set()
    db=sqlite3.connect(f'file:{gptoss_backup}?mode=ro&immutable=1',uri=True)
    with Path(output).open('w',encoding='utf-8') as stream:
        for key in sorted(rows):
            stream.write(json.dumps(rows[key],sort_keys=True)+'\n')
        for ledger_key,number,state,http,raw,raw_hash in db.execute('SELECT key,number,state,http_status,raw,raw_sha256 FROM attempts ORDER BY key'):
            key=ledger_to_scientific.get(ledger_key)
            if (ledger_key in gkeys or key is None or key.split('|')[2] not in ARMS or number!=1 or
                state!='completed' or http!=200 or raw is None or hashlib.sha256(raw).hexdigest()!=raw_hash):
                raise ValueError('gpt-oss ledger/raw identity differs')
            gkeys.add(ledger_key)
            category,label,_=module.classify(raw)
            if category not in {'valid','abstain','invalid','truncated'}:
                raise ValueError('gpt-oss classification differs')
            gcounts[category]+=1
            stream.write(json.dumps({'model':'gptoss','key':key,'state':category,'predicted_label':label,
                                     'attempts':1,'recoverable_transport_attempts':0},sort_keys=True)+'\n')
    db.close()
    if gkeys!=set(ledger_to_scientific):
        raise ValueError('gpt-oss key grid differs')
    receipt={'truthRead':False,'scoresComputed':False,'gptossBackupSha256':sha(gptoss_backup),
             'qwenNormalizedSha256':sha(qwen_normalized),'classifierSha256':sha(classifier_path),
             'gptossRequestsSha256':sha(request_grid),
             'combinedSha256':sha(output),'models':['qwen','gptoss'],'keysPerModel':14336,
             'qwenStates':dict(sorted(qcounts.items())),'gptossStates':dict(sorted(gcounts.items()))}
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    if len(sys.argv)!=6:
        raise SystemExit('usage: build_outputs.py GPTOSS_BACKUP QWEN_NORMALIZED PINNED_CLASSIFIER GPTOSS_REQUESTS COMBINED_JSONL')
    main(*map(Path,sys.argv[1:]))
