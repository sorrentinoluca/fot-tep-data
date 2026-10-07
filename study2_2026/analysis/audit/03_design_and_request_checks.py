"""Window-selection rule, run coverage, request settings, tiers and timing, duplicate requests.
Usage: python3 03_design_and_request_checks.py <study2_2026 dir> <pickle from 01>"""
import json, gzip, sys, pickle, hashlib, re, base64
from collections import Counter, defaultdict
R=sys.argv[1]; cases,num,D=pickle.load(open(sys.argv[2],'rb'))
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
FAULTS=['F1','F2','F3','F8','F10','F13','F14','F15']
# --- case manifest design checks
off={f:i for i,f in enumerate(FAULTS)}; off['Normal']=0
bad=0; cov=defaultdict(Counter)
for c in cases.values():
    j=1+((c['class_position_k']-1+off[c['true_label']])%8)
    if j!=c['window_ordinal'] or c['window_start_h']!=25+5*(j-1) or c['window_end_h']!=30+5*(j-1): bad+=1
    cov[c['true_label']][c['window_ordinal']]+=1
print('window rule violations',bad,'| coverage per window: fault',sorted(set(tuple(sorted(cov[f].values())) for f in FAULTS)),'normal',sorted(cov['Normal'].values()))
print('replacements',sum(c['replacement_reason'] is not None for c in cases.values()),'status',Counter(c['simulation_status'] for c in cases.values()),'unique streams',len({c['stream_id'] for c in cases.values()}),'unique runs',len({c['run_id'] for c in cases.values()}))
# --- requests
q={r['key']:r for r in gz(R+'/requests/qwen_requests.jsonl.gz')}
g={r['pair_id']+'|'+r['arm']:r for r in gz(R+'/requests/gpt_oss_requests.jsonl.gz')}
print('qwen wire keys',Counter(tuple(sorted(r['wire'])) for r in q.values()).most_common(3))
print('gpt wire keys',Counter(tuple(sorted(r['wire'])) for r in g.values()).most_common(3))
for name,d in (('qwen',q),('gpt',g)):
    print(name,{k:Counter(json.dumps(r['wire'].get(k),sort_keys=True)[:60] for r in d.values()).most_common(2) for k in ('model','temperature','seed','top_p','top_k','max_tokens','thinking_token_budget','reasoning_effort','repetition_penalty')})
    print(name,'distinct system prompts',len({r['wire']['messages'][0]['content'] for r in d.values()}),'n messages',Counter(len(r['wire']['messages']) for r in d.values()),'schema variants',len({json.dumps(r['wire']['response_format'],sort_keys=True) for r in d.values()}))
same=sum(q[k]['wire']['messages']==g[k]['wire']['messages'] for k in q); print('messages identical qwen vs gpt-oss:',same,'of',len(q))
print('wireSha256 verified:',sum(hashlib.sha256(json.dumps(r['wire'],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()==r['wireSha256'] for r in q.values()),'(compact sorted utf8) ',sum(hashlib.sha256(json.dumps(r['wire'],sort_keys=True,separators=(",",":")).encode()).hexdigest()==r['wireSha256'] for r in q.values()),'(compact sorted ascii)')
sp=next(iter(q.values()))['wire']['messages'][0]['content']; print('SYSTEM PROMPT:',sp)
print('schema enum:',next(iter(q.values()))['wire']['response_format']['json_schema']['schema']['properties']['predicted_label'])
# tiers & timing by arm
for model in ('qwen','gptoss'):
    by=defaultdict(list)
    for k,v in D[model].items(): by[k.rsplit('|',1)[1]].append(v)
    print(model,{a:(Counter(x['tier'] for x in vs).most_common(3),min(x['t0'] for x in vs)[5:16],max(x['t1'] for x in vs)[5:16]) for a,vs in by.items()})
# duplicate wires
grp=defaultdict(list)
for k,r in q.items(): grp[r['wireSha256']].append(k)
pairs=[v for v in grp.values() if len(v)>1]; print('qwen byte-identical wire groups',len(pairs),'sizes',Counter(len(v) for v in pairs))
rawq={}
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    rawq[r['key']]=base64.b64decode(r['response_raw_base64'])
idb=idc=idl=ids=idr=0
for a,b in [v for v in pairs if len(v)==2]:
    ea,eb=json.loads(rawq[a]),json.loads(rawq[b])
    idb+=rawq[a]==rawq[b]
    ma,mb=ea['choices'][0]['message'],eb['choices'][0]['message']
    idc+=ma.get('content')==mb.get('content'); idr+=(ma.get('reasoning')==mb.get('reasoning'))
    idl+=(D['qwen'][a]['state'],D['qwen'][a]['label'])==(D['qwen'][b]['state'],D['qwen'][b]['label'])
    ea2={k:v for k,v in ea.items() if k not in('id','created')}; eb2={k:v for k,v in eb.items() if k not in('id','created')}
    ids+=ea2==eb2
print(f'of {len(pairs)} pairs: identical stored bytes {idb}; identical except id/created {ids}; identical answer content {idc}; identical reasoning {idr}; identical state+label {idl}')
ex=json.loads(rawq[pairs[0][0]]); print('envelope keys',list(ex.keys()))
# gpt-oss duplicates
gk=defaultdict(list)
for k,r in g.items(): gk[json.dumps(r['wire'],sort_keys=True)].append(k)
gp=[v for v in gk.values() if len(v)==2]
print('gpt-oss identical wire pairs',len(gp),'identical state+label',sum((D['gptoss'][a]['state'],D['gptoss'][a]['label'])==(D['gptoss'][b]['state'],D['gptoss'][b]['label']) for a,b in gp))
# collision case
cc='case_208de85d389949569608a5a94d4dd19a'; print('collision case truth',cases[cc]['true_label'],cases[cc]['run_id'])
