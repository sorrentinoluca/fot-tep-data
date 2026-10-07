"""Truth-free gpt-oss token accounting from the immutable R07 backup and request grid."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

BACKUP_SHA='32d2817b37e213670407ed5f97a9f90e95c07625755c8ee47fe4f6b08dceeb1a'
REQUEST_SHA='f78c96b12f6fb52aade6f8d52de0c5a4a5a34a5f832be8dbd7b14b99aa6e18f6'


def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()


def main(backup,requests,output):
 if sha(backup)!=BACKUP_SHA or sha(requests)!=REQUEST_SHA:raise ValueError('source hash differs')
 arms={}
 for line in Path(requests).open(encoding='utf-8'):
  row=json.loads(line)
  if row['key'] in arms:raise ValueError('duplicate request key')
  arms[row['key']]=row['arm']
 if len(arms)!=14336:raise ValueError('request count differs')
 totals={arm:Counter() for arm in ('A0','B0','FULL','SELF','AGG','S0','PL0')}
 db=sqlite3.connect(f'file:{backup}?mode=ro&immutable=1',uri=True)
 seen=set()
 for key,raw,raw_hash in db.execute('SELECT key,raw,raw_sha256 FROM attempts'):
  if key in seen or key not in arms or hashlib.sha256(raw).hexdigest()!=raw_hash:raise ValueError('raw identity differs')
  seen.add(key)
  usage=json.loads(raw).get('usage') or {}
  arm=arms[key]
  totals[arm]['keys']+=1
  for field in ('prompt_tokens','completion_tokens','total_tokens'):
   v=usage.get(field)
   if type(v) is not int or v<0:raise ValueError('usage field absent/invalid')
   totals[arm][field]+=v
  details=usage.get('completion_tokens_details') or {}
  reasoning=details.get('reasoning_tokens') if isinstance(details,dict) else None
  if reasoning is None:totals[arm]['reasoning_unobserved_keys']+=1
  else:totals[arm]['reasoning_tokens']+=reasoning
 db.close()
 if seen!=set(arms):raise ValueError('ledger coverage differs')
 result={'truthRead':False,'scoresComputed':False,'backupSha256':BACKUP_SHA,'requestsSha256':REQUEST_SHA,
         'byArm':{arm:dict(sorted(counter.items())) for arm,counter in totals.items()},
         'total':{field:sum(totals[arm][field] for arm in totals) for field in ('keys','prompt_tokens','completion_tokens','total_tokens','reasoning_unobserved_keys')}}
 Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result['total'],sort_keys=True))

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('usage: usage_accounting.py BACKUP REQUESTS OUTPUT')
 main(*map(Path,sys.argv[1:]))
