"""Agreement between responses to byte-identical requests (re-sends), for both models.
Usage: python3 resend_agreement.py <study2_2026 dir>
Definitions, per pair of requests whose 'wire' payload is identical:
  stored bytes   = the raw response body as archived (includes 'id' and 'created')
  envelope       = parsed response with the top-level 'id' and 'created' fields removed
  answer text    = choices[0].message.content (the JSON answer string)
  outcome        = (state, label) after applying the answer contract of the package
                   (valid label / abstain / rejected / truncated)."""
import json, gzip, base64, sys
from collections import defaultdict, Counter
R=sys.argv[1]; LABELS={'F1','F2','F3','F8','F10','F13','F14','F15','Normal'}
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
def outcome(raw):
    env=json.loads(raw); ch=env['choices'][0]; fin=ch.get('finish_reason')
    if fin!='stop': return ('truncated' if fin=='length' else 'rejected',None)
    try: a=json.loads(ch['message']['content'])
    except Exception: return ('rejected',None)
    if not isinstance(a,dict) or set(a)!={'predicted_label','abstain','used_insight_ids','reasoning_summary'}: return ('rejected',None)
    lab,ab,ids,s=a['predicted_label'],a['abstain'],a['used_insight_ids'],a['reasoning_summary']
    ok=(isinstance(ab,bool) and isinstance(ids,list) and all(isinstance(x,str) and x and len(x)<=128 for x in ids)
        and len(ids)<=14 and len(ids)==len(set(ids)) and isinstance(s,str) and s.strip() and len(s)<=1200
        and not (ab and lab is not None) and (ab or lab in LABELS))
    if not ok: return ('rejected',None)
    return ('abstain',None) if ab else ('valid',lab)
for model,req,resp,reqkey,respkey in (
    ('qwen','qwen_requests.jsonl.gz','qwen_responses.jsonl.gz',lambda r:r['key'],lambda r:r['key']),
    ('gpt-oss','gpt_oss_requests.jsonl.gz','gpt_oss_responses.jsonl.gz',lambda r:r['pair_id']+'|'+r['arm'],lambda r:r['scientific_key'])):
    groups=defaultdict(list)
    for r in gz(R+'/requests/'+req): groups[json.dumps(r['wire'],sort_keys=True)].append(reqkey(r))
    pairs=[v for v in groups.values() if len(v)==2]; assert all(len(v)<=2 for v in groups.values())
    need={k for p in pairs for k in p}; raw={}
    for r in gz(R+'/responses/'+resp):
        if respkey(r) in need: raw[respkey(r)]=base64.b64decode(r['response_raw_base64'])
    c=Counter()
    for a,b in pairs:
        ea,eb=json.loads(raw[a]),json.loads(raw[b]); oa,ob=outcome(raw[a]),outcome(raw[b])
        c['identical stored bytes']+=raw[a]==raw[b]
        c['identical envelope (id/created removed)']+=({k:v for k,v in ea.items() if k not in('id','created')}=={k:v for k,v in eb.items() if k not in('id','created')})
        c['identical answer text']+=ea['choices'][0]['message'].get('content')==eb['choices'][0]['message'].get('content')
        c['identical outcome (state and label)']+=oa==ob
        both=oa[0]=='valid' and ob[0]=='valid'; c['both valid']+=both; c['both valid, same label']+=both and oa==ob
    print(model,'| pairs of identical requests:',len(pairs))
    for k in ('identical stored bytes','identical envelope (id/created removed)','identical answer text','identical outcome (state and label)','both valid','both valid, same label'): print(f'   {k}: {c[k]}')
