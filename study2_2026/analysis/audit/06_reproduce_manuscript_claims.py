"""Recomputes additional quantitative claims in the current manuscript snapshot.
Usage: python3 newclaims.py <study2_2026 dir> <pickle written by indep.py>"""
import json, gzip, base64, sys, pickle, re
from collections import Counter, defaultdict
R=sys.argv[1]; cases,num,D=pickle.load(open(sys.argv[2],'rb'))
ARMS=['A0','B0','FULL','SELF','AGG','S0','PL0']; FAULTS=['F1','F2','F3','F8','F10','F13','F14','F15']
RX=['C_'+f for f in FAULTS]; LABELS=set(FAULTS)|{'Normal'}
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
truth=lambda c: cases[c]['true_label']
def role(c,r):
    t=truth(c)
    return 'normal' if t=='Normal' else ('own' if r=='C_'+t else 'lu')
Q=D['qwen']
# ---- 1. relaxed scoring for the 43 responses rejected only by the 1,200-character cap
relaxed={}
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    if Q[r['key']]['state']!='invalid': continue
    ans=json.loads(json.loads(base64.b64decode(r['response_raw_base64']))['choices'][0]['message']['content'])
    relaxed[r['key']]=None if ans['abstain'] else ans['predicted_label']
print('1. rejected responses:',len(relaxed),'| by condition',dict(Counter(k.split('|')[2] for k in relaxed)))
print('   by condition and role',dict(Counter((k.split('|')[2],role(*k.split('|')[:2])) for k in relaxed)))
newc=[(k.split('|')[2],role(*k.split('|')[:2])) for k,l in relaxed.items() if l==truth(k.split('|')[0])]
print('   additional correct answers under the relaxed rule:',len(newc),newc)
def correct(c,r,a,relax=False):
    v=Q[f'{c}|{r}|{a}']
    if v['state']=='valid': return int(v['label']==truth(c))
    if relax and v['state']=='invalid': return int(relaxed[f'{c}|{r}|{a}']==truth(c))
    return 0
own=[c for c in cases if truth(c)!='Normal']
def ownacc(a,relax=False,faults=FAULTS):
    return sum(sum(correct(c,'C_'+truth(c),a,relax) for c in own if truth(c)==f)/24 for f in faults)/len(faults)*100
for relax in (False,True):
    print(f'   relaxed={relax}: own FULL-B0 {ownacc("FULL",relax)-ownacc("B0",relax):+.3f}  FULL-A0 {ownacc("FULL",relax)-ownacc("A0",relax):+.3f}  B0-A0 {ownacc("B0",relax)-ownacc("A0",relax):+.3f}  SELF-A0 {ownacc("SELF",relax)-ownacc("A0",relax):+.3f}')
# ---- 2. F3/F15 share of the Family A gain
g=Counter(); l=Counter()
for c in own:
    d=correct(c,'C_'+truth(c),'FULL')-correct(c,'C_'+truth(c),'B0'); g[truth(c)]+=d>0; l[truth(c)]+=d<0
net={f:g[f]-l[f] for f in FAULTS}; print('2. net gains by fault',net,'total',sum(net.values()),'F3+F15',net['F3']+net['F15'])
six=[f for f in FAULTS if f not in('F3','F15')]
cf=sum(correct(c,'C_'+truth(c),'FULL') for c in own if truth(c) in six); cb=sum(correct(c,'C_'+truth(c),'B0') for c in own if truth(c) in six)
print(f'   excluding F3/F15: FULL {cf}/144 vs B0 {cb}/144 -> {100*(cf-cb)/144:+.3f} pp')
# ---- 3. own-label assignments (table tab_t2_ownlabels) and Normal split by receiver
print('3. own-label assignments: correct on own-fault /192, false on local-unseen /1344, false on Normal /512')
for a in ARMS:
    cnt=Counter(); f3f15=0
    for k,v in Q.items():
        c,r,arm=k.split('|')
        if arm!=a or v['state']!='valid' or v['label']!=r[2:]: continue
        cnt[role(c,r)]+=1
        if role(c,r)=='normal' and r in('C_F3','C_F15'): f3f15+=1
    print(f'   {a:5s} own {cnt["own"]:4d}  local-unseen {cnt["lu"]:4d}  Normal {cnt["normal"]:4d}  (Normal at F3/F15 receivers: {f3f15} of 128)')
# ---- 4. error split on local-unseen decisions
print('4. local-unseen wrong answers: predicted Normal / wrong fault')
for a in ('B0','FULL'):
    n=w=0
    for k,v in Q.items():
        c,r,arm=k.split('|')
        if arm==a and role(c,r)=='lu' and v['state']=='valid' and v['label']!=truth(c):
            n+=v['label']=='Normal'; w+=v['label']!='Normal'
    print(f'   {a}: Normal {n}, wrong fault {w}')
for name,get in (('PROTO',lambda c: None if num[c]['protoAbstain'] else num[c]['protoLabel']),('FedAvg',lambda c: num[c]['fedavgLabel'])):
    n=w=0
    for c in own:
        p=get(c)
        if p!=truth(c): n+=7*(p=='Normal'); w+=7*(p not in('Normal',None))
    print(f'   {name}: Normal {n}, wrong fault {w}')
# ---- 5. byte sizes of the reusable insight texts
nat={}; struct={}
for r in gz(R+'/requests/qwen_requests.jsonl.gz'):
    u=r['wire']['messages'][1]['content']; arm=r['arm']
    if arm in('B0','SELF'):
        for line in u.split('\n'):
            m=re.match(r'Insight (P05-INS-F\d+) describes',line)
            if m: nat.setdefault(m.group(1),set()).add(line)
    if arm=='S0':
        for line in u.split('\n'):
            if line.startswith('{"insight_id"'): struct.setdefault(json.loads(line)['insight_id'],set()).add(line)
assert all(len(v)==1 for v in nat.values()) and all(len(v)==1 for v in struct.values())
order=['P05-INS-'+f for f in FAULTS]
print('5. natural-language insights joined by blank lines:',len('\n\n'.join(next(iter(nat[k])) for k in order).encode()),'bytes;',
      'structured records joined by newlines:',len('\n'.join(next(iter(struct[k])) for k in order).encode()),'bytes')
# ---- 6. syntactic traceability of cited insight IDs in B0 answers
prompt={r['key']:r['wire']['messages'][1]['content'] for r in gz(R+'/requests/qwen_requests.jsonl.gz') if r['arm']=='B0'}
tot=found=parsed=0; unparse=0
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    if r['arm']!='B0': continue
    ch=json.loads(base64.b64decode(r['response_raw_base64']))['choices'][0]
    try:
        ans=json.loads(ch['message']['content']); ids=ans['used_insight_ids']; assert isinstance(ids,list)
    except Exception: unparse+=1; continue
    parsed+=1
    for i in ids: tot+=1; found+=str(i) in prompt[r['key']]
print(f'6. B0 answers parseable as JSON: {parsed} (not parseable: {unparse}); cited insight-ID occurrences: {tot}; found in the prompt text: {found}')
