"""Parse every archived raw response with an independent reader of the answer contract,
compare with the package's normalized rows, and total the token usage.
Usage: python3 01_parse_raw_responses.py <study2_2026 dir> <output pickle>"""
import json, gzip, base64, sys, hashlib, itertools, pickle
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
R=sys.argv[1]; OUT=sys.argv[2]
ARMS=['A0','B0','FULL','SELF','AGG','S0','PL0']; FAULTS=['F1','F2','F3','F8','F10','F13','F14','F15']
RX=['C_'+f for f in FAULTS]; LABELS=set(FAULTS)|{'Normal'}
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
cases={}
for l in open(R+'/data/case_manifest.jsonl'):
    r=json.loads(l); cases[r['case_id']]=r
num={}
for l in open(R+'/data/numerical_predictions.jsonl'):
    r=json.loads(l); num[r['case_id']]=r
def parse(raw):
    """my own reading of the answer contract; returns state,label,reason,usage,fingerprint"""
    env=json.loads(raw); ch=env['choices'][0]; usage=env.get('usage') or {}
    fp=env.get('system_fingerprint'); fin=ch.get('finish_reason')
    if fin=='length': return 'truncated',None,'length',usage,fp
    if fin!='stop': return 'invalid',None,'finish:'+str(fin),usage,fp
    try: ans=json.loads(ch['message']['content'])
    except Exception as e: return 'invalid',None,'content-not-json',usage,fp
    if not isinstance(ans,dict) or set(ans)!={'predicted_label','abstain','used_insight_ids','reasoning_summary'}:
        return 'invalid',None,'fields',usage,fp
    lab,ab,ids,summ=ans['predicted_label'],ans['abstain'],ans['used_insight_ids'],ans['reasoning_summary']
    reasons=[]
    if not isinstance(ab,bool): reasons.append('abstain-type')
    if not isinstance(summ,str) or not summ.strip(): reasons.append('summary-empty')
    elif len(summ)>1200: reasons.append('summary>1200')
    if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids): reasons.append('ids-type')
    elif len(ids)>14 or len(ids)!=len(set(ids)) or any((not x) or len(x)>128 for x in ids): reasons.append('ids-content')
    if ab is True and lab is not None: reasons.append('abstain-with-label')
    if ab is False and lab not in LABELS: reasons.append('label-not-allowed')
    if reasons: return 'invalid',None,'+'.join(reasons),usage,fp
    return ('abstain',None,'',usage,fp) if ab else ('valid',lab,'',usage,fp)
D={}
for model,fn,keyf in (('qwen','qwen_responses.jsonl.gz',lambda r:r['key']),('gptoss','gpt_oss_responses.jsonl.gz',lambda r:r['scientific_key'])):
    rows={}
    for r in gz(R+'/responses/'+fn):
        raw=base64.b64decode(r['response_raw_base64'])
        assert hashlib.sha256(raw).hexdigest()==r['response_sha256']
        st,lab,why,us,fp=parse(raw)
        k=keyf(r); assert k not in rows
        rows[k]=dict(state=st,label=lab,why=why,pt=us.get('prompt_tokens'),ct=us.get('completion_tokens'),
                     details=us.get('completion_tokens_details'),fp=fp,rawsha=r['response_sha256'],
                     t0=r['reserved_utc'],t1=r['finished_utc'],http=r['http_status'],attempt=r['attempt'],tier=r.get('tier'))
    assert len(rows)==14336, len(rows)
    D[model]=rows
pickle.dump((cases,num,D),open(OUT,'wb'))
for m in D:
    print(m,'states',dict(Counter(v['state'] for v in D[m].values())),'http',dict(Counter(v['http'] for v in D[m].values())),'attempt',dict(Counter(v['attempt'] for v in D[m].values())))
    print('  invalid reasons',dict(Counter(v['why'] for v in D[m].values() if v['state']=='invalid')))
    print('  fingerprints',dict(Counter(v['fp'] for v in D[m].values())))
    print('  usage details non-null',sum(v['details'] is not None for v in D[m].values()))
    print('  tokens: prompt',sum(v['pt'] or 0 for v in D[m].values()),'completion',sum(v['ct'] or 0 for v in D[m].values()))
    print('  time span',min(v['t0'] for v in D[m].values()),max(v['t1'] for v in D[m].values()))
inv=[v for v in D['qwen'].values() if v['state']=='invalid']
print('qwen invalid tokens: prompt',sum(v['pt'] for v in inv),'completion',sum(v['ct'] for v in inv))
# compare with packaged normalized rows
mism=0; tokm=0
for r in gz(R+'/responses/qwen_normalized_responses.jsonl.gz'):
    v=D['qwen'][r['key']]
    if (v['state'],v['label'])!=(r['state'],r['predicted_label']): mism+=1
    if r['state']!='invalid' and (r['input_tokens'],r['output_tokens'])!=(v['pt'],v['ct']): tokm+=1
print('qwen my-parser vs packaged normalized: state/label mismatches',mism,'token mismatches (non-invalid)',tokm)
mm=Counter()
for r in gz(R+'/responses/normalized_model_outputs.jsonl.gz'):
    v=D[r['model']][r['key']]
    if (v['state'],v['label'])!=(r['state'],r['predicted_label']): mm[r['model']]+=1
print('my-parser vs packaged combined rows mismatches',dict(mm))
