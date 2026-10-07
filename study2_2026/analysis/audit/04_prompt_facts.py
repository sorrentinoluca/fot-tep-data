"""Facts read from the archived prompts: AGG library entries, number of observations,
all-quiet insights for F3/F15, the flagged F2 case, local examples per receiver.
Usage: python3 04_prompt_facts.py <study2_2026 dir>"""
import json, gzip, sys, re, pickle
from collections import Counter
R=sys.argv[1]
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
agg=set(); facts={}; ins_text={}; coll=[]; loc=Counter()
cc='case_208de85d389949569608a5a94d4dd19a'
for r in gz(R+'/requests/qwen_requests.jsonl.gz'):
    u=r['wire']['messages'][1]['content']; c,rx,arm=r['key'].split('|')
    if arm=='AGG':
        m=re.search(r'COMMON INSIGHT LIBRARY.*?(?=\n\nTARGET OBSERVATION)',u,re.S); agg.add(m.group(0))
    if arm=='S0':
        for line in u.split('\n'):
            if line.startswith('{"insight_id"'):
                j=json.loads(line); facts[j['insight_id']]=j
    if arm in('B0','SELF'):
        for m in re.finditer(r'Insight (P05-INS-F\d+) describes.*',u): ins_text[m.group(1)]=m.group(0)
    if c==cc and rx=='C_F2':
        tgt=u.split('TARGET OBSERVATION (unlabelled):\n\n',1)[1].strip(); locb=u.split('TARGET OBSERVATION')[0]
        coll.append((arm, tgt in locb))
    if arm=='A0' and c==cc: loc[(rx,len(re.findall(r'Local example \d+ \(label ([A-Za-z0-9]+)\)',u)),tuple(re.findall(r'Local example \d+ \(label ([A-Za-z0-9]+)\)',u)))]+=1
print('AGG library variants',len(agg)); a=next(iter(agg))
ents=re.findall(r'\[(AGG-INS-\d+)\] entry kind: (\w+) \| classes: ([^|]+)\|',a); print(len(ents),Counter(k for _,k,_ in ents)); print([ (e,k,c.strip()) for e,k,c in ents])
print('structured insights',sorted(facts),'facts per insight',{k:len(v['facts']) for k,v in facts.items()},'total',sum(len(v['facts']) for v in facts.values()))
print('natural-language insights found',sorted(ins_text))
for k in ('P05-INS-F3','P05-INS-F15'): print(k,':',ins_text.get(k,'')[:600])
print('collision target-in-local-examples by arm',coll)
print('local example labels by receiver',sorted(loc))
