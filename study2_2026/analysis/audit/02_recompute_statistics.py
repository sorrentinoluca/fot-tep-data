"""Independent recomputation of the statistics reported in the manuscript.
Uses only the pickle written by 01_parse_raw_responses.py (own parser), NumPy and SciPy;
no code from the package. Usage: python3 02_recompute_statistics.py <pickle>"""
import pickle, sys, json
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
cases,num,D=pickle.load(open(sys.argv[1],'rb'))
ARMS=['A0','B0','FULL','SELF','AGG','S0','PL0']; FAULTS=['F1','F2','F3','F8','F10','F13','F14','F15']
RX=['C_'+f for f in FAULTS]
def truth(c): return cases[c]['true_label']
def rxs(c,dom):
    t=truth(c)
    if dom=='normal': return RX
    if dom=='own': return ['C_'+t]
    return [r for r in RX if r!='C_'+t]
def sc(model,c,r,arm):
    if arm=='PROTO': return int((not num[c]['protoAbstain']) and num[c]['protoLabel']==truth(c))
    if arm=='FedAvg': return int(num[c]['fedavgLabel']==truth(c))
    v=D[model][f'{c}|{r}|{arm}']; return int(v['state']=='valid' and v['label']==truth(c))
def runval(model,c,dom,coef):
    rs=rxs(c,dom); return sum(w*sum(sc(model,c,r,a) for r in rs)/len(rs) for a,w in coef.items())
def sel(faults,dom):
    if dom=='normal': return sorted(c for c in cases if truth(c)=='Normal')
    return sorted(c for c in cases if truth(c) in faults)
def est(model,faults,dom,coef,drop=()):
    cs=[c for c in sel(faults,dom) if c not in drop]
    if dom=='normal': return 100*np.mean([runval(model,c,dom,coef) for c in cs])
    return 100*np.mean([np.mean([runval(model,c,dom,coef) for c in cs if truth(c)==f]) for f in faults])
def acc(model,faults,dom,arm): return est(model,faults,dom,{arm:1})
P={'all':FAULTS,'noF1F8':[f for f in FAULTS if f not in('F1','F8')],'F1F8':['F1','F8']}
print('=== Table arms (Qwen): own / LU / Normal ; states')
for a in ARMS+['PROTO','FedAvg']:
    line=f"{a:6s} own {acc('qwen',FAULTS,'own',a):6.2f}  LU {acc('qwen',FAULTS,'lu',a):6.2f}  Normal {acc('qwen',FAULTS,'normal',a):6.2f}"
    if a in ARMS:
        st=Counter(v['state'] for k,v in D['qwen'].items() if k.endswith('|'+a)); line+=f"  {dict(st)}"
        own_correct=sum(sc('qwen',c,r,a) for c in sel(FAULTS,'own') for r in rxs(c,'own')); line+=f" ownCorrect={own_correct}/192"
    print(line)
print('=== Table supplement (gpt-oss)')
for a in ARMS:
    st=Counter(v['state'] for k,v in D['gptoss'].items() if k.endswith('|'+a))
    print(f"{a:6s} own {acc('gptoss',FAULTS,'own',a):6.2f}  LU {acc('gptoss',FAULTS,'lu',a):6.2f}  Normal {acc('gptoss',FAULTS,'normal',a):6.2f} abstain {st['abstain']}")
# Family A
def famA(model):
    cs=sel(FAULTS,'own'); d={c:runval(model,c,'own',{'FULL':1,'B0':-1}) for c in cs}
    means=[];terms=[];ns=[]
    for f in FAULTS:
        v=np.array([d[c] for c in cs if truth(c)==f]); means.append(v.mean()); terms.append(v.var(ddof=1)/len(v)); ns.append(len(v))
    e=np.mean(means); se=np.sqrt(sum(terms))/len(FAULTS); df=sum(terms)**2/sum(t*t/(n-1) for t,n in zip(terms,ns))
    tc=stats.t.ppf(0.975,df); p=2*stats.t.sf(abs(e/se),df)
    g=sum(v>0 for v in d.values()); l=sum(v<0 for v in d.values())
    return e*100,(e-tc*se)*100,(e+tc*se)*100,p,df,g,l,len(d)-g-l,d
e,lo,hi,p,df,g,l,t,d=famA('qwen')
print(f'=== Family A qwen FULL-B0 own: {e:.3f} CI [{lo:.3f},{hi:.3f}] p={p:.4e} df={df:.2f} gain {g} loss {l} tie {t}')
for f in FAULTS:
    v=[d[c] for c in d if truth(c)==f]; print(f'   {f}: {100*np.mean(v):+.1f} gain {sum(x>0 for x in v)} loss {sum(x<0 for x in v)} tie {sum(x==0 for x in v)}')
# Family B: full enumeration of 2^24 sign assignments (meet in the middle over exact integer sums)
def signflip(ints):
    a=np.array(ints[:12]); b=np.array(ints[12:])
    signs=np.array(np.meshgrid(*[[-1,1]]*12)).reshape(12,-1).T
    sa=signs@a; sb=signs@b
    tot=(sa[:,None]+sb[None,:]).ravel(); obs=abs(sum(ints))
    return np.count_nonzero(np.abs(tot)>=obs)/tot.size, tot.size
raw={}
for f in ('F1','F8'):
    cs=sel([f],'lu'); ints=[round(7*runval('qwen',c,'lu',{'B0':1,'PROTO':-1})) for c in cs]
    pv,n=signflip(ints); raw[f]=pv
    print(f'=== Family B {f}: est {100*np.mean(ints)/7:+.3f} rawP {pv:.4e} (assignments {n}) B0 {acc("qwen",[f],"lu","B0"):.3f} PROTO {acc("qwen",[f],"lu","PROTO"):.3f}')
o=sorted(raw,key=raw.get); holm={o[0]:min(1,2*raw[o[0]])}; holm[o[1]]=max(holm[o[0]],raw[o[1]]); print('   Holm',{k:f'{v:.4e}' for k,v in holm.items()})
print('=== contrasts (qwen) by partition: own / lu / normal')
C={'B0-A0':{'B0':1,'A0':-1},'SELF-A0':{'SELF':1,'A0':-1},'FULL-SELF':{'FULL':1,'SELF':-1},'FULL-B0':{'FULL':1,'B0':-1},'FULL-A0':{'FULL':1,'A0':-1},
   'interaction':{'FULL':1,'SELF':-1,'B0':-1,'A0':1},'AGG-FULL':{'AGG':1,'FULL':-1},'S0-B0':{'S0':1,'B0':-1},'PL0-B0':{'PL0':1,'B0':-1},
   'B0-PROTO':{'B0':1,'PROTO':-1},'B0-FedAvg':{'B0':1,'FedAvg':-1}}
for m in ('qwen','gptoss'):
  print('  model',m)
  for name,co in C.items():
    s=f'  {name:12s}'
    for pn,pf in P.items(): s+=f' | {pn}: own {est(m,pf,"own",co):+7.3f} lu {est(m,pf,"lu",co):+7.3f}'
    s+=f' | normal {est(m,FAULTS,"normal",co):+7.3f}'; print(s)
# independent bootstrap (different seed/generator) as a ballpark check of pointwise intervals
def boot(model,faults,dom,co,B=20000,seed=12345):
    rng=np.random.default_rng(seed); cs=sel(faults,dom); draws=[]
    for f in faults:
        v=np.array([runval(model,c,dom,co) for c in cs if truth(c)==f]); idx=rng.integers(0,len(v),size=(B,len(v))); draws.append(v[idx].mean(axis=1))
    s=np.mean(draws,axis=0); return [round(float(100*x),2) for x in np.quantile(s,[.025,.975])]
print('=== ballpark bootstrap (independent seed)')
for pn,pf in P.items():
    print(f'  {pn}: FULL-B0 own {boot("qwen",pf,"own",C["FULL-B0"])}  B0-PROTO lu {boot("qwen",pf,"lu",C["B0-PROTO"])}  gptoss FULL-B0 own {boot("gptoss",pf,"own",C["FULL-B0"])} gptoss B0-PROTO lu {boot("gptoss",pf,"lu",C["B0-PROTO"])}')
# cross-model family-A difference
cs=sel(FAULTS,'own'); dd=[runval('gptoss',c,'own',C['FULL-B0'])-runval('qwen',c,'own',C['FULL-B0']) for c in cs]
print('=== cross-model FULL-B0 own diff (gptoss - qwen):', f"{est('gptoss',FAULTS,'own',C['FULL-B0'])-est('qwen',FAULTS,'own',C['FULL-B0']):+.3f}")
rng=np.random.default_rng(7); dr=[]
for f in FAULTS:
    v=np.array([runval('gptoss',c,'own',C['FULL-B0'])-runval('qwen',c,'own',C['FULL-B0']) for c in cs if truth(c)==f]); idx=rng.integers(0,len(v),size=(20000,len(v))); dr.append(v[idx].mean(axis=1))
print('   ballpark interval',[round(float(100*x),2) for x in np.quantile(np.mean(dr,axis=0),[.025,.975])])
# SELF / PL0 local-unseen breakdown
print('=== LU breakdown')
for a in ARMS:
    st=Counter(); corr=0
    for c in sel(FAULTS,'lu'):
        for r in rxs(c,'lu'):
            v=D['qwen'][f'{c}|{r}|{a}']; st[v['state']]+=1; corr+=sc('qwen',c,r,a)
    print(f'  {a}: {dict(st)} total {sum(st.values())} validCorrect {corr} validWrong {st["valid"]-corr}')
# error destinations
print('=== F8 LU destinations and Normal false alarms')
for a in ('B0','FULL'):
    dest=Counter()
    for c in sel(['F8'],'lu'):
        for r in rxs(c,'lu'):
            v=D['qwen'][f'{c}|{r}|{a}']; dest[v['label'] if v['state']=='valid' else v['state']]+=1
    print(f'  {a} F8 LU dest {dict(dest)} n={sum(dest.values())}')
for a in ARMS:
    fa=own=ab=0
    for c in sel([], 'normal'):
        for r in RX:
            v=D['qwen'][f'{c}|{r}|{a}']
            if v['state']=='valid' and v['label'] in FAULTS: fa+=1; own+= v['label']==r[2:]
            ab+= v['state']=='abstain'
    print(f'  {a} Normal: falseAlarms {fa} ownLabel {own} abstain {ab} of 512')
# per-fault all-arm table
print('=== per-fault accuracies (own | LU)')
for dom in ('own','lu'):
    for f in FAULTS: print(' ',dom,f,' '.join(f'{acc("qwen",[f],dom,a):5.1f}' for a in ARMS+['PROTO','FedAvg']))
# token means per arm
print('=== token means per arm (qwen)')
for a in ARMS:
    vs=[v for k,v in D['qwen'].items() if k.endswith('|'+a)]; print(f'  {a}: n={len(vs)} in {np.mean([v["pt"] for v in vs]):.1f} out {np.mean([v["ct"] for v in vs]):.1f} total_in {sum(v["pt"] for v in vs)}')
print('  gptoss per arm in:',{a:round(float(np.mean([v["pt"] for k,v in D["gptoss"].items() if k.endswith("|"+a)])),1) for a in ARMS})
print('=== PROTO abstain count',sum(num[c]['protoAbstain'] for c in num),' distinct signatureSha256',len({num[c]['signatureSha256'] for c in num}),'max mult',max(Counter(num[c]['signatureSha256'] for c in num).values()))
print('   case_manifest distinct signature_sha256',len({cases[c]['signature_sha256'] for c in cases}),' distinct text_sha256',len({cases[c]['text_sha256'] for c in cases}))
tx=defaultdict(list)
for c in cases: tx[cases[c]['text_sha256']].append(c)
for k,v in tx.items():
    if len(v)>1: print('   dup text:',[(x,truth(x),cases[x]['run_id']) for x in v])
