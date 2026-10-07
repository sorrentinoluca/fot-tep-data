"""Extended check of the numbers in the manuscript text (pinned to manuscript SHA-256 ed992921593c9c5be6a6eab0a26eb094b26bd6b4a21a8e2a947c82e0a5813109.).

Usage: python3 08b_check_text_claims_extended.py <study2_2026 dir> <pickle from 01> <manuscript .tex>
       <qwen_analysis.json> <combined_analysis.json> [uncovered.tsv]

WHAT IT DOES
  1. Fragments. Each claim is a sentence fragment copied from the manuscript in which every number is
     replaced by a value computed here from the package. A fragment passes when it occurs verbatim in
     the .tex. Sources: raw responses and case manifest (results), archived requests (generation
     settings, prompt contents), configuration/ (development pool, FedAvg recipe), analysis JSON.
  2. Conditions. Statements that are not one number in one sentence ("both p < 0.001", the
     window-selection rule, "every rejected summary exceeds 1,200 characters") are evaluated as true/false.
  3. Inventory. Every numeric token of the manuscript body, from the abstract to the end of the
     availability section, captions included, is counted as inside or outside a checked fragment.
     With a sixth argument the tokens outside are written to a file, one per line with section and
     context. The curated version of that list is uncovered_numeric_statements.md.

WHAT IT DOES NOT SHOW
  - It does not show that every number in the manuscript is verified. A number outside the fragments
    is simply not checked by this script; see the inventory.
  - Table cells are not checked here (script 07 does that). The figure, the bibliography and numbers
    written as words outside a fragment ("eight clients") are not inventoried.
  - Excluded from the inventory as names rather than quantities: condition names, fault and variable
    names, labels, citations, the model identifiers, LaTeX lengths.
  - Taken from the regenerated analysis JSON files, not recomputed: percentile-bootstrap intervals and
    the three point-only drop sensitivities. The stratified-t intervals are recomputed with SciPy.
  - A fragment is tied to the wording: after any edit of a sentence it reports NOT FOUND, which means
    "re-check this sentence", not "the number is wrong"."""
import sys, re, json, gzip, base64, pickle, hashlib
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
R=sys.argv[1]; cases,num,D=pickle.load(open(sys.argv[2],'rb')); TEX=open(sys.argv[3],encoding='utf-8').read()
EXPECTED_TEX_SHA256='ed992921593c9c5be6a6eab0a26eb094b26bd6b4a21a8e2a947c82e0a5813109'
if hashlib.sha256(TEX.encode('utf-8')).hexdigest()!=EXPECTED_TEX_SHA256: raise SystemExit('manuscript SHA-256 differs from pinned snapshot')
QJ=json.load(open(sys.argv[4])); GJ=json.load(open(sys.argv[5]))
ARMS=['A0','B0','FULL','SELF','AGG','S0','PL0']; FAULTS=['F1','F2','F3','F8','F10','F13','F14','F15']; RX=['C_'+f for f in FAULTS]
P={'all':FAULTS,'no':[f for f in FAULTS if f not in('F1','F8')],'f1f8':['F1','F8']}
def gz(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:
        for l in f:
            if l.strip(): yield json.loads(l)
truth=lambda c: cases[c]['true_label']
def role(c,r): return 'normal' if truth(c)=='Normal' else ('own' if r=='C_'+truth(c) else 'lu')
def rxs(c,dom): return RX if dom=='normal' else (['C_'+truth(c)] if dom=='own' else [r for r in RX if r!='C_'+truth(c)])
def sc(m,c,r,a):
    if a=='PROTO': return int((not num[c]['protoAbstain']) and num[c]['protoLabel']==truth(c))
    if a=='FedAvg': return int(num[c]['fedavgLabel']==truth(c))
    v=D[m][f'{c}|{r}|{a}']; return int(v['state']=='valid' and v['label']==truth(c))
def rv(m,c,dom,co): return sum(w*sum(sc(m,c,r,a) for r in rxs(c,dom))/len(rxs(c,dom)) for a,w in co.items())
def est(m,faults,dom,co):
    if dom=='normal': return 100*float(np.mean([rv(m,c,dom,co) for c in cases if truth(c)=='Normal']))
    return 100*float(np.mean([np.mean([rv(m,c,dom,co) for c in cases if truth(c)==f]) for f in faults]))
acc=lambda m,faults,dom,a: est(m,faults,dom,{a:1})
con=lambda m,p,dom,a,b: est(m,P[p],dom,{a:1,b:-1})
Q=D['qwen']; G=D['gptoss']; own=sorted(c for c in cases if truth(c)!='Normal'); normal=sorted(c for c in cases if truth(c)=='Normal')
f1=lambda x: f'{x:.1f}'; s1=lambda x: f'{x:+.1f}'; th=lambda n: f'{n:,}'
def sci(p): m,e=f'{p:.2e}'.split('e'); return m+'\\times10^{'+str(int(e))+'}'
WORD={2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight'}
V={}
# coverage
st=Counter(v['state'] for v in Q.values()); gs=Counter(v['state'] for v in G.values())
V.update(valid=th(st['valid']),abst=th(st['abstain']),rej=str(st['invalid']),trunc=str(st['truncated']),rejtrunc=str(st['invalid']+st['truncated']),gvalid=th(gs['valid']),gabst=th(gs['abstain']),gtotal=th(sum(gs.values())))
# family A
d={c:rv('qwen',c,'own',{'FULL':1,'B0':-1}) for c in own}
terms=[np.var([d[c] for c in own if truth(c)==f],ddof=1)/24 for f in FAULTS]; e=float(np.mean(list(d.values())))
se=np.sqrt(sum(terms))/8; df=sum(terms)**2/sum(t*t/23 for t in terms); tc=stats.t.ppf(.975,df)
gain=sum(x>0 for x in d.values()); loss=sum(x<0 for x in d.values())
V.update(A=f1(100*e),As=s1(100*e),lo=f1(100*(e-tc*se)),hi=f1(100*(e+tc*se)),los=s1(100*(e-tc*se)),his=s1(100*(e+tc*se)),pA=sci(float(2*stats.t.sf(abs(e/se),df))),
         gain=str(gain),loss=WORD.get(loss,str(loss)),tie=str(len(d)-gain-loss))
pf={f:100*float(np.mean([d[c] for c in own if truth(c)==f])) for f in FAULTS}; V.update(dF1=s1(pf['F1']),dF3=s1(pf['F3']),dF8=s1(pf['F8']),dF15=s1(pf['F15']))
net={f:sum(d[c]>0 for c in own if truth(c)==f)-sum(d[c]<0 for c in own if truth(c)==f) for f in FAULTS}
six=[f for f in FAULTS if f not in('F3','F15')]; cf=sum(sc('qwen',c,'C_'+truth(c),'FULL') for c in own if truth(c) in six); cb=sum(sc('qwen',c,'C_'+truth(c),'B0') for c in own if truth(c) in six)
V.update(net315=str(net['F3']+net['F15']),nettot=str(sum(net.values())),six=s1(100*(cf-cb)/144),cf=str(cf),cb=str(cb),share=str(round(100*(net['F3']+net['F15'])/sum(net.values()))))
# family B
def signflip(ints):
    sg=np.array(np.meshgrid(*[[-1,1]]*12)).reshape(12,-1).T; tot=((sg@np.array(ints[:12]))[:,None]+(sg@np.array(ints[12:]))[None,:]).ravel()
    return np.count_nonzero(np.abs(tot)>=abs(sum(ints)))/tot.size
raw={f:signflip([round(7*rv('qwen',c,'lu',{'B0':1,'PROTO':-1})) for c in sorted(cases) if truth(c)==f]) for f in('F1','F8')}
o=sorted(raw,key=raw.get); holm={o[0]:min(1,2*raw[o[0]])}; holm[o[1]]=max(holm[o[0]],raw[o[1]])
b1=est('qwen',['F1'],'lu',{'B0':1,'PROTO':-1}); b8=est('qwen',['F8'],'lu',{'B0':1,'PROTO':-1})
V.update(B1=f1(b1),B1s=s1(b1),B8=f1(-b8),B8s=s1(b8),h1=sci(holm['F1']),h8=sci(holm['F8']))
# accuracies and contrasts
for a in ARMS:
    V['own'+a]=f1(acc('qwen',FAULTS,'own',a)); V['lu'+a]=f1(acc('qwen',FAULTS,'lu',a)); V['nor'+a]=f1(acc('qwen',FAULTS,'normal',a)); V['gown'+a]=f1(acc('gptoss',FAULTS,'own',a))
V.update(nown=str(sum(sc('qwen',c,'C_'+truth(c),'FULL') for c in own)),nownA=str(sum(sc('qwen',c,'C_'+truth(c),'A0') for c in own)),nownB=str(sum(sc('qwen',c,'C_'+truth(c),'B0') for c in own)))
nor={a:acc('qwen',FAULTS,'normal',a) for a in ARMS+['PROTO','FedAvg']}
V.update(norP=f1(nor['PROTO']),norF=f'{nor["FedAvg"]:.0f}',normin=f1(min(nor[a] for a in ARMS)),normax=f1(max(nor[a] for a in ARMS)),
         mPA=f1(nor['PROTO']-max(nor[a] for a in ARMS)),mFA=f1(nor['FedAvg']-min(nor[a] for a in ARMS)),mPB=f1(nor['PROTO']-nor['B0']),mFB=f1(nor['FedAvg']-nor['B0']),
         best=max(ARMS,key=lambda a:nor[a]),worst=min(ARMS,key=lambda a:nor[a]),luF=f1(acc('qwen',FAULTS,'lu','FedAvg')),lumax=f1(max(acc('qwen',FAULTS,'lu',a) for a in ARMS)),
         gnorB0=f1(acc('gptoss',FAULTS,'normal','B0')))
for k,(m,p,dom,a,b) in {'PLB':('qwen','all','own','PL0','B0'),'BA':('qwen','all','own','B0','A0'),'FA':('qwen','all','own','FULL','A0'),'SA':('qwen','all','own','SELF','A0'),
    'BP':('qwen','all','lu','B0','PROTO'),'BPno':('qwen','no','lu','B0','PROTO'),'BP18':('qwen','f1f8','lu','B0','PROTO'),'BF':('qwen','all','lu','B0','FedAvg'),
    'FBno':('qwen','no','own','FULL','B0'),'FB18':('qwen','f1f8','own','FULL','B0'),'AFo':('qwen','all','own','AGG','FULL'),'AFn':('qwen','all','normal','AGG','FULL'),
    'SBno':('qwen','no','own','S0','B0'),'SB18':('qwen','f1f8','own','S0','B0'),'SBl':('qwen','all','lu','S0','B0'),'SBn':('qwen','all','normal','S0','B0'),
    'gFB':('gptoss','all','own','FULL','B0'),'gBP':('gptoss','all','lu','B0','PROTO'),'gFS':('gptoss','all','own','FULL','SELF')}.items(): V[k]=s1(con(m,p,dom,a,b))
V['inter']=s1(est('qwen',FAULTS,'own',{'FULL':1,'SELF':-1,'B0':-1,'A0':1})); V['xm']=s1(con('gptoss','all','own','FULL','B0')-con('qwen','all','own','FULL','B0'))
V['AFl']='exactly zero' if abs(con('qwen','all','lu','AGG','FULL'))<1e-12 else s1(con('qwen','all','lu','AGG','FULL')); V['SBo']='zero' if abs(con('qwen','all','own','S0','B0'))<1e-12 else s1(con('qwen','all','own','S0','B0'))
V['drop16']=f1(-con('qwen','all','own','B0','A0'))
# intervals and drop sensitivities taken from the regenerated analysis JSON files
def qboot(part,dom,cont): return [s1(100*x) for x in next(r for r in QJ['secondary'] if r['partition']==part and r['domain']==dom and r['contrast']==cont and 'pointwiseBootstrap95' in r)['pointwiseBootstrap95']]
V['iBP'],V['iBPno'],V['iBP18'],V['iFBno'],V['iFB18']=[','.join(x) for x in (qboot('all_faults','local_unseen','B0-PROTO'),qboot('excluding_F1_F8','local_unseen','B0-PROTO'),qboot('F1_F8','local_unseen','B0-PROTO'),qboot('excluding_F1_F8','own','FULL-B0'),qboot('F1_F8','own','FULL-B0'))]
V['igFB']=','.join(s1(100*x) for x in next(r for r in GJ['contrasts'] if r['model']=='gptoss' and r['domain']=='all_faults' and r['visibility']=='own' and r['contrast']=='FULL-B0')['pointwise95'])
dd=QJ['duplicateInputWholeRunSensitivityPointOnly']
x=next(r for r in dd if r['partition']=='all_faults' and r['domain']=='own' and r['contrast']=='FULL-B0'); V.update(dropA=s1(100*x['estimate']),dropN=str(x['plannedIndependentRuns']),dropK=WORD[len(x['droppedCaseIds'])].capitalize())
x=next(r for r in dd if r['partition']=='F1' and r['domain']=='local_unseen' and r['contrast']=='B0-PROTO'); V.update(dropB=s1(100*x['estimate']),dropBn=str(x['plannedIndependentRuns']))
# response states on local-unseen decisions, error destinations, own-label assignments
def lu_states(a):
    s=Counter(); cor=0
    for c in own:
        for r in rxs(c,'lu'): v=Q[f'{c}|{r}|{a}']; s[v['state']]+=1; cor+=sc('qwen',c,r,a)
    return s,cor
for a in ('SELF','PL0'):
    s,cor=lu_states(a); V.update({'ab'+a:str(s['abstain']),'abp'+a:f1(100*s['abstain']/1344),'cor'+a:str(cor),'val'+a:str(s['valid']),'wr'+a:str(s['valid']-cor),'rest'+a:WORD.get(s['invalid']+s['truncated'],str(s['invalid']+s['truncated']))})
def dest(a,fault):
    return Counter((Q[f'{c}|{r}|{a}']['label'] if Q[f'{c}|{r}|{a}']['state']=='valid' else Q[f'{c}|{r}|{a}']['state']) for c in own if truth(c)==fault for r in rxs(c,'lu'))
V.update(f8f1B=str(dest('B0','F8')['F1']),f8f1F=str(dest('FULL','F8')['F1']),f8B=f1(acc('qwen',['F8'],'lu','B0')),f8F=f1(acc('qwen',['F8'],'lu','FULL')),f1B=f1(acc('qwen',['F1'],'lu','B0')),f1Fed=f'{acc("qwen",["F1"],"lu","FedAvg"):.0f}')
def normal_counts(a):
    fa=ol=ab=ol315=0
    for c in normal:
        for r in RX:
            v=Q[f'{c}|{r}|{a}']
            if v['state']=='valid' and v['label'] in FAULTS: fa+=1; o_=v['label']==r[2:]; ol+=o_; ol315+=o_ and r in('C_F3','C_F15')
            ab+=v['state']=='abstain'
    return fa,ol,ab,ol315
nc={a:normal_counts(a) for a in ARMS}
V.update(faF=str(nc['FULL'][0]),faB=str(nc['B0'][0]),olF=str(nc['FULL'][1]),olB=str(nc['B0'][1]),faS=str(nc['SELF'][0]),abS=str(nc['SELF'][2]),ol315B=str(nc['B0'][3]),ol315F=str(nc['FULL'][3]),addN=str(nc['FULL'][1]-nc['B0'][1]))
def lu_own_label(a): return sum(1 for c in own for r in rxs(c,'lu') if Q[f'{c}|{r}|{a}']['state']=='valid' and Q[f'{c}|{r}|{a}']['label']==r[2:])
V['addL']=str(lu_own_label('FULL')-lu_own_label('B0'))
def split(a):
    n=w=0
    for c in own:
        for r in rxs(c,'lu'):
            v=Q[f'{c}|{r}|{a}']
            if v['state']=='valid' and v['label']!=truth(c): n+=v['label']=='Normal'; w+=v['label']!='Normal'
    return n,w
def nsplit(get):
    n=w=0
    for c in own:
        p=get(c)
        if p!=truth(c): n+=7*(p=='Normal'); w+=7*(p not in('Normal',None))
    return n,w
(V['eBn'],V['eBw']),(V['eFn'],V['eFw'])=[tuple(map(str,split(a))) for a in('B0','FULL')]
V['ePn'],V['ePw']=map(str,nsplit(lambda c: None if num[c]['protoAbstain'] else num[c]['protoLabel'])); V['eFen'],V['eFew']=map(str,nsplit(lambda c:num[c]['fedavgLabel']))
# relaxed 1,200-character rule, tokens, resends, prompt facts (need the raw archives)
relaxed={}; tot=found=0; nat={}; struct={}; agg=set(); prompt={}
for r in gz(R+'/requests/qwen_requests.jsonl.gz'):
    u=r['wire']['messages'][1]['content']
    if r['arm']=='B0': prompt[r['key']]=u
    if r['arm'] in('B0','SELF'):
        for line in u.split('\n'):
            m=re.match(r'Insight (P05-INS-F\d+) describes',line)
            if m: nat[m.group(1)]=line
    if r['arm']=='S0':
        for line in u.split('\n'):
            if line.startswith('{"insight_id"'): struct[json.loads(line)['insight_id']]=line
    if r['arm']=='AGG': agg.add(re.search(r'COMMON INSIGHT LIBRARY.*?(?=\n\nTARGET OBSERVATION)',u,re.S).group(0))
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    k=r['key']
    if Q[k]['state']=='invalid' or r['arm']=='B0':
        try: ans=json.loads(json.loads(base64.b64decode(r['response_raw_base64']))['choices'][0]['message']['content'])
        except Exception: continue
        if Q[k]['state']=='invalid': relaxed[k]=None if ans['abstain'] else ans['predicted_label']
        if r['arm']=='B0' and isinstance(ans.get('used_insight_ids'),list):
            for i in ans['used_insight_ids']: tot+=1; found+=str(i) in prompt[k]
extra=[(k.split('|')[2],role(*k.split('|')[:2])) for k,l in relaxed.items() if l==truth(k.split('|')[0])]
def own_relaxed(a): return 100*np.mean([np.mean([(sc('qwen',c,'C_'+truth(c),a) or int(relaxed.get(f'{c}|C_{truth(c)}|{a}')==truth(c))) for c in own if truth(c)==f]) for f in FAULTS])
rejA0=[role(*k.split('|')[:2]) for k in relaxed if k.endswith('|A0')]
V.update(extra=WORD.get(len(extra),str(len(extra))),rFB=s1(own_relaxed('FULL')-own_relaxed('B0')),rFA=s1(own_relaxed('FULL')-own_relaxed('A0')),rejA0=str(len(rejA0)),idf=th(found),idt=th(tot))
extra_ok=sorted(extra)==[('FULL','own'),('S0','lu')] and set(rejA0)=={'lu'}
order=['P05-INS-'+f for f in FAULTS]
V.update(natb=th(len('\n\n'.join(nat[k] for k in order).encode())),strb=th(len('\n'.join(struct[k] for k in order).encode())),nobs=str(sum(len(json.loads(struct[k])['facts']) for k in order)))
kinds=Counter(k for _,k in re.findall(r'\[(AGG-INS-\d+)\] entry kind: (\w+)',next(iter(agg)))); V.update(aggn=str(sum(kinds.values())),agg1=WORD.get(kinds['class_observation'],str(kinds['class_observation'])),agg2=WORD.get(kinds['cross_class_relation'],str(kinds['cross_class_relation'])))
tin=lambda D_,a: float(np.mean([v['pt'] for k,v in D_.items() if k.endswith('|'+a)]))
inv=[v for v in Q.values() if v['state']=='invalid']
V.update(tin=th(sum(v['pt'] for v in Q.values())),tout=th(sum(v['ct'] for v in Q.values())),rin=th(sum(v['pt'] for v in inv)),rout=th(sum(v['ct'] for v in inv)),gin=th(sum(v['pt'] for v in G.values())),gout=th(sum(v['ct'] for v in G.values())),
         ratio=f1(tin(Q,'B0')/tin(Q,'A0')),aggmore=str(round(tin(Q,'AGG')-tin(Q,'FULL'))),plin=th(round(tin(Q,'PL0'))),b0in=th(round(tin(Q,'B0'))),shorter=str(round(100*(1-tin(Q,'PL0')/tin(Q,'B0')))))
grp=defaultdict(list)
for r in gz(R+'/requests/qwen_requests.jsonl.gz'): grp[r['wireSha256']].append(r['key'])
pairs=[v for v in grp.values() if len(v)==2]; need={k for p in pairs for k in p}; content={}
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    if r['key'] in need: content[r['key']]=json.loads(base64.b64decode(r['response_raw_base64']))['choices'][0]['message'].get('content')
same=sum((Q[a]['state'],Q[a]['label'])==(Q[b]['state'],Q[b]['label']) for a,b in pairs); bv=[(a,b) for a,b in pairs if Q[a]['state']==Q[b]['state']=='valid']; sl=sum(Q[a]['label']==Q[b]['label'] for a,b in bv)
V.update(npairs=str(len(pairs)),same=str(same),samep=f1(100*same/len(pairs)),bv=str(len(bv)),sl=str(sl),slp=f1(100*sl/len(bv)),sametext=str(sum(content[a]==content[b] for a,b in pairs)))
# signatures and duplicate inputs
sig=Counter(v['signatureSha256'] for v in num.values()); tx=defaultdict(list)
for c in cases: tx[cases[c]['text_sha256']].append(c)
dup=[v for v in tx.values() if len(v)>1]
V.update(nsig=str(len(sig)),sigmax=str(max(sig.values())),ndup=WORD[len(dup)].capitalize(),ncross=WORD[sum(len({truth(c) for c in v})>1 for v in dup)])

# ---------------------------------------------------------------- additional recomputed values
import hashlib
print('manuscript sha256:',hashlib.sha256(TEX.encode('utf-8')).hexdigest()[:12])
def tint(m,part,dom,co):
    faults=P[part]; means=[]; terms=[]
    for f in faults:
        v=np.array([rv(m,c,dom,co) for c in sorted(cases) if truth(c)==f],dtype=float); means.append(v.mean()); terms.append(v.var(ddof=1)/len(v))
    e_=float(np.mean(means)); se_=float(np.sqrt(sum(terms))/len(faults)); df_=sum(terms)**2/sum(t*t/23 for t in terms if t>0); tc_=stats.t.ppf(.975,df_)
    return s1(100*e_),s1(100*(e_-tc_*se_)),s1(100*(e_+tc_*se_))
for name,(part,dom,co) in {'BAlu':('all','lu',{'B0':1,'A0':-1}),'BAo':('all','own',{'B0':1,'A0':-1}),'BFl':('all','lu',{'B0':1,'FedAvg':-1}),
    'SAo':('all','own',{'SELF':1,'A0':-1}),'FSo':('all','own',{'FULL':1,'SELF':-1}),'INo':('all','own',{'FULL':1,'SELF':-1,'B0':-1,'A0':1}),
    'PLBo':('all','own',{'PL0':1,'B0':-1}),'AFo_':('all','own',{'AGG':1,'FULL':-1}),'AFl_':('all','lu',{'AGG':1,'FULL':-1}),
    'SBo_':('all','own',{'S0':1,'B0':-1}),'SBl_':('all','lu',{'S0':1,'B0':-1})}.items():
    V[name],V[name+'_lo'],V[name+'_hi']=tint('qwen',part,dom,co)
ncorr=lambda m,a,dom: sum(sc(m,c,r,a) for c in (normal if dom=='normal' else own) for r in rxs(c,dom))
V.update(tot=th(len(Q)),nluB0=str(ncorr('qwen','B0','lu')),nluA0=str(ncorr('qwen','A0','lu')),nluFULL=str(ncorr('qwen','FULL','lu')),
         nnorFULL=str(ncorr('qwen','FULL','normal')),nnorB0=str(ncorr('qwen','B0','normal')),
         FBlu=s1(con('qwen','all','lu','FULL','B0')),FBnor=s1(est('qwen',FAULTS,'normal',{'FULL':1,'B0':-1})),
         otF=str(nc['FULL'][0]-nc['FULL'][1]),otB=str(nc['B0'][0]-nc['B0'][1]),
         FS=s1(con('qwen','all','own','FULL','SELF')),PLA=s1(con('qwen','all','own','PL0','A0')),
         gnorA0=f1(acc('gptoss',FAULTS,'normal','A0')),dropKw=V['dropK'].lower(),idabs=str(tot-found),npar=th(697*9+9),
         fullmore=str(round(tin(Q,'FULL')-tin(Q,'B0'))),
         abAGG=str(Counter(v['state'] for k,v in Q.items() if k.endswith('|AGG'))['abstain']),abFULL=str(Counter(v['state'] for k,v in Q.items() if k.endswith('|FULL'))['abstain']))
o315=lambda a: sum(sc('qwen',c,'C_'+truth(c),a) for c in own if truth(c) in('F3','F15'))
V.update(o315F=str(o315('FULL')),o315B=str(o315('B0')))
x=next(r for r in QJ['collisionWholeRunSensitivityPointOnly'] if r['partition']=='all_faults' and r['domain']=='own' and r['contrast']=='FULL-B0'); V['collA']=s1(100*x['estimate'])
CLAIMS=[
 ('abstract',r'had <luB0>\% accuracy on local-unseen faults vs.\ <luA0>\% with local examples alone; own-fault accuracy was <ownB0>\% vs.\ <ownA0>\%'),
 ('abstract',r'was associated with <A> percentage points (pp) higher own-fault accuracy (run-paired 95\% CI <lo>--<hi>; $p<0.001$)'),
 ('abstract',r'were <olF> vs.\ <olB> of 512 decisions'),
 ('abstract',r'was <B1>~pp higher on fault 1 and <B8>~pp lower on fault 8 (both Holm-adjusted $p<0.001$)'),
 ('abstract',r'FedAvg reached <luF>\% pooled accuracy on local-unseen faults, above every LLM condition (at most <lumax>\%)'),
 ('results',r'All <tot> primary-LLM requests returned HTTP 200 on the first attempt: <valid> valid labeled answers, <abst> abstentions, <rej> parser rejections and <trunc> truncations'),
 ('results',r'local-unseen accuracy was <nluB0>/1,344 (<luB0>\%) in \cond{B0}, vs.\ <nluA0>/1,344 (<luA0>\%) in local-only \cond{A0}: $<BAlu>$~pp (95\% $t$ interval $[<BAlu_lo>, <BAlu_hi>]$)'),
 ('results',r'Own-fault accuracy was lower, <nownB>/192 vs.\ <nownA>/192 ($<BA>$~pp; $[<BAo_lo>, <BAo_hi>]$)'),
 ('family A',r'\cond{FULL} was correct on <nown>/192 own-fault runs (<ownFULL>\%), vs.\ <nownB>/192 (<ownB0>\%) for \cond{B0}'),
 ('family A',r'The Family~A difference is $<As>$~pp (95\% $t$ CI $[<los>,<his>]$, $p=<pA>$): <gain> runs gained, <loss> lost and <tie> tied'),
 ('family A',r'\cond{FULL}$-$\cond{B0} was $<FBlu>$~pp local-unseen (<nluFULL>/1,344 vs.\ <nluB0>/1,344) and $<FBnor>$~pp Normal (<nnorFULL>/512 vs.\ <nnorB0>/512)'),
 ('family A',r"Normal false alarms numbered <faF> vs.\ <faB>; those assigning the receiver's own label numbered <olF> vs.\ <olB>. Other-label false alarms numbered <otF> vs.\ <otB>"),
 ('family A',r'F1 ($<dF1>$~pp), F3 ($<dF3>$), F8 ($<dF8>$) and F15 ($<dF15>$) account for most'),
 ('family A',r'F3/F15 contribute <net315> of the <nettot> net gains, but their receivers assign their own label to <o315F>/48 own-fault and <ol315F>/128 Normal pairs in \cond{FULL}, vs.\ <o315B>/48 and <ol315B>/128 in \cond{B0}. All <olF> \cond{FULL} false own-label'),
 ('family A',r'Excluding F3/F15 gives $<six>$~pp (<cf>/144 vs.\ <cb>/144)'),
 ('family A',r'Dropping <dropKw> own-fault runs with duplicate target text, as prespecified, gives $<dropA>$~pp on <dropN> runs'),
 ('family A',r'The <rej> parser rejections satisfy'),
 ('family A',r'recovers <extra> correct answers: one own-fault \cond{FULL} and one local-unseen \cond{S0}. Own-fault \cond{FULL}$-$\cond{B0} becomes $<rFB>$~pp and \cond{FULL}$-$\cond{A0} $<rFA>$~pp'),
 ('family A',r'All <rejA0> \cond{A0} rejections remain incorrect local-unseen answers'),
 ('family B',r'by $<B1s>$~pp (Holm $p=<h1>$), but falls below it on F8 by $<B8s>$~pp (Holm $p=<h8>$)'),
 ('family B',r'dropping one member gives $<dropB>$~pp on <dropBn> runs'),
 ('family B',r'On F1, FedAvg scores <f1Fed>\%, vs.\ <f1B>\% for \cond{B0}'),
 ('family B',r'\cond{B0}$-$\PROTO{} is $<BP>$~pp $[<iBP>]$. On the prespecified six faults excluding F1/F8 it is $<BPno>$~pp $[<iBPno>]$, and on F1/F8 alone $<BP18>$~pp $[<iBP18>]$. The corresponding own-fault \cond{FULL}$-$\cond{B0} differences are $<FBno>$~pp $[<iFBno>]$ and $<FB18>$~pp $[<iFB18>]$'),
 ('references',r'(<luF>\% vs.\ at most <lumax>\%); \cond{B0}$-$FedAvg is $<BF>$~pp (95\% $t$ interval $[<BFl_lo>, <BFl_hi>]$)'),
 ('references',r'\PROTO{} scores <norP>\%, FedAvg <norF>\%, and the LLM conditions <normin>--<normax>\%. The smallest margin is \PROTO{} over \cond{<best>} ($+<mPA>$~pp), the largest FedAvg over \cond{<worst>} ($+<mFA>$~pp); their respective margins over \cond{B0} are $+<mPB>$ and $+<mFB>$~pp'),
 ('controls',r'Own-fault \cond{SELF}$-$\cond{A0} is $<SA>$~pp (95\% $t$ interval $[<SAo_lo>, <SAo_hi>]$); adding peers to \cond{SELF} gives \cond{FULL}$-$\cond{SELF} $<FS>$~pp ($[<FSo_lo>, <FSo_hi>]$). The $2\times2$ interaction is $<inter>$~pp ($[<INo_lo>, <INo_hi>]$). Relative to local-only \cond{A0}, \cond{FULL} is $<FA>$~pp higher (<nown>/192 vs.\ <nownA>/192)'),
 ('controls',r'Own-fault accuracy is <ownA0>\% in \cond{A0}, <ownB0>\% in \cond{B0}, <ownPL0>\% in \cond{PL0} and <ownFULL>\% in \cond{FULL}. Thus \cond{PL0}$-$\cond{B0} is $<PLB>$~pp (95\% $t$ interval $[<PLBo_lo>, <PLBo_hi>]$), while \cond{PL0}$-$\cond{A0} is descriptively $<PLA>$~pp'),
 ('controls',r'\cond{AGG}$-$\cond{FULL} is $<AFo>$~pp own-fault (95\% $t$ interval $[<AFo__lo>, <AFo__hi>]$), zero local-unseen ($[<AFl__lo>, <AFl__hi>]$) and $<AFn>$~pp Normal. Structured \cond{S0}$-$\cond{B0} is zero own-fault overall ($[<SBo__lo>, <SBo__hi>]$), but $<SBno>$~pp without F1/F8 and $<SB18>$~pp on F1/F8; local-unseen is $<SBl>$~pp ($[<SBl__lo>, <SBl__hi>]$) and Normal $<SBn>$~pp'),
 ('errors',r'On 1,344 local-unseen pairs, \cond{SELF} abstains on <abSELF> (<abpSELF>\%) and \cond{PL0} on <abPL0> (<abpPL0>\%). Only <corSELF>/<valSELF> and <corPL0>/<valPL0> valid labeled answers are correct, leaving <wrSELF> and <wrPL0> wrong; <restSELF> and <restPL0> further outputs are rejected or truncated'),
 ('errors',r'\cond{SELF} has only <faS> Normal false alarms but <abS> abstentions'),
 ('errors',r'\cond{B0} labels <f8f1B>/168 pairs as F1, compared with <f8f1F>/168 in \cond{FULL}; correctness is <f8B>\% vs.\ <f8F>\%. Across local-unseen faults, \cond{B0} makes <eBn> Normal and <eBw> wrong-fault predictions; \cond{FULL} makes <eFn> and <eFw>. \PROTO{} makes <ePn> and <ePw>, and FedAvg <eFen> and <eFew>'),
 ('errors',r'finds <idf> of <idt> cited insight-ID occurrences in the corresponding prompt text; <idabs> are absent'),
 ('supplement',r'gpt-oss completed <gtotal> requests: <gvalid> valid answers and <gabst> abstentions, with no rejection or truncation'),
 ('supplement',r"Its own-fault \cond{FULL}$-$\cond{B0} is $<gFB>$~pp (pointwise percentile interval $[<igFB>]$), while local-unseen \cond{B0}$-$\PROTO{} is $<gBP>$~pp. Own-fault \cond{FULL}$-$\cond{SELF} is $<gFS>$~pp, opposite the primary LLM's $<FS>$~pp. Normal \cond{B0} accuracy is <gnorB0>\%, vs.\ <norB0>\% for the primary LLM. The between-system own-fault \cond{FULL}$-$\cond{B0} difference is $<xm>$~pp"),
 ('supplement',r'gpt-oss \cond{PL0} (<gownPL0>\%) and \cond{SELF} (<gownSELF>\%) exceed \cond{FULL} (<gownFULL>\%)'),
 ('accounting',r"\cond{B0} uses about <ratio> times \cond{A0}'s input tokens. \cond{FULL} uses <fullmore> more input tokens per request than \cond{B0} and has <A>~pp higher own-fault accuracy"),
 ('accounting',r'\cond{AGG} uses <aggmore> more input tokens than \cond{FULL}'),
 ('accounting',r'and <abAGG> vs.\ <abFULL> abstentions'),
 ('accounting',r'records <tin> input and <tout> output tokens, including <rin> input and <rout> output tokens from <rej> parser-rejected responses'),
 ('accounting',r'The gpt-oss archive records <gin> input and <gout> output tokens'),
 ('accounting',r'occupy <natb> UTF-8 bytes joined by blank lines, or <strb> bytes as structured records joined by single newlines'),
 ('accounting',r'FedAvg trained five <npar>-parameter models for 50 rounds'),
 ('accounting',r'<plin> vs.\ <b0in> input tokens per request for \cond{B0}, about <shorter>\% fewer'),
 ('discussion',r'from <ownA0>\% in \cond{A0} to <ownB0>\% in \cond{B0} ($<BA>$~pp), and higher local-unseen accuracy (<luA0>\% to <luB0>\%). The own-fault drop is absent in \cond{PL0} (<ownPL0>\%)'),
 ('discussion',r'\cond{FULL} has <addN> more false own-label assignments on Normal and <addL> more on local-unseen faults. F3/F15 supply <net315> of <nettot> net own-fault gains, while their receivers make all <olF> \cond{FULL} own-label assignments on Normal'),
 ('discussion',r'retain a descriptive $<six>$~pp own-fault gain'),
 ('discussion',r"\cond{B0} reaches <f1B>\% local-unseen accuracy, above \PROTO{} but below FedAvg's <f1Fed>\%"),
 ('discussion',r'assigns <f8f1B>/168 local-unseen F8 decisions to F1'),
 ('discussion',r'from \cond{A0} to \cond{B0} (<gownA0>\% to <gownB0>\%), but \cond{FULL} (<gownFULL>\%) remains below \cond{A0}; \cond{PL0} reaches <gownPL0>\%. Its Normal accuracy rises from <gnorA0>\% to <gnorB0>\% from \cond{A0} to \cond{B0}, whereas the primary LLM falls from <norA0>\% to <norB0>\%'),
 ('limitations',r'only <nsig> distinct signatures among 256 cases (maximum multiplicity <sigmax>)'),
 ('limitations',r'F3/F15 receivers account for <net315> of <nettot> net \cond{FULL}$-$\cond{B0} own-fault gains and all <olF> \cond{FULL} false own-label assignments on Normal'),
 ('limitations',r'<ndup> pairs of cases have identical model-facing inputs, reducing input diversity; <ncross> pairs cross true labels'),
 ('limitations',r'<dropK> duplicate members fall within the 192 own-fault runs; dropping them yields the separate point-only estimate of $<dropA>$~pp'),
 ('limitations',r'dropping that case alone in the prespecified point-only sensitivity leaves Family~A at $<collA>$~pp'),
 ('limitations',r'the four duplicate input pairs generated <npairs> byte-identical request pairs across eight receivers and seven conditions. Response state and label agreed in <same> (<samep>\%); <sl> of <bv> pairs with two valid labels agreed (<slp>\%)'),
 ('conclusion',r'(<luB0>\% vs.\ <luA0>\%) and lower own-fault accuracy (<ownB0>\% vs.\ <ownA0>\%). The prespecified \cond{FULL}$-$\cond{B0} own-fault contrast was $<As>$~pp; the \cond{FULL}$-$\cond{A0} difference was $<FA>$~pp descriptively. False own-label assignments on Normal were <olF> vs.\ <olB> of 512 decisions'),
 ('conclusion',r'FedAvg reached <f1Fed>\% on F1'),
]

# ---------------------------------------------------------------- setting and design statements
# Numbers of Sections I-IV, of the captions and of the availability section that can be read or
# counted from the package: case manifest, archived requests, configuration files, analysis JSON.
cnt=Counter(truth(c) for c in cases); assert len({cnt[f] for f in FAULTS})==1
npair={dom:sum(len(rxs(c,dom)) for c in (normal if dom=='normal' else own)) for dom in('own','lu','normal')}
qw=[r['wire'] for r in gz(R+'/requests/qwen_requests.jsonl.gz')]; gw=[r['wire'] for r in gz(R+'/requests/gpt_oss_requests.jsonl.gz')]
def one(ws,k):
    vals={json.dumps(w.get(k)) for w in ws}; assert len(vals)==1,(k,vals); return json.loads(next(iter(vals)))
dev=json.load(open(R+'/configuration/development_streams.json'))['runs']; rec=json.load(open(R+'/configuration/fedavg_development_recipe.json'))['algorithm']
recall=json.load(open(R+'/configuration/fedavg_development_recipe.json'))
def find_seeds(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='seeds': return v
            r_=find_seeds(v)
            if r_ is not None: return r_
    return None
seeds=find_seeds(recall)
devw=Counter(); devr=Counter()
for r in dev: devw[r['class']]+=r['windowCount']; devr[r['class']]+=1
assert len({devw[f] for f in FAULTS})==1 and len({devr[f] for f in FAULTS})==1
f0=json.loads(struct['P05-INS-F1'])['facts'][0]
quote=re.search(r'Between 25 and 65 h, the largest above-threshold level shift[^.]*\.',nat['P05-INS-F1']).group(0)
wl={int(float(cases[c]['window_end_h'])-float(cases[c]['window_start_h'])) for c in cases}; assert len(wl)==1
w0=min(int(float(cases[c]['window_start_h'])) for c in cases); w1=max(int(float(cases[c]['window_end_h'])) for c in cases)
V.update(nrun=str(len(cases)),nperf=str(cnt['F1']),nnormrun=str(cnt['Normal']),npo=str(npair['own']),npl=th(npair['lu']),npn=str(npair['normal']),
         npercond=th(len(Q)//len(ARMS)),K=str(len(FAULTS)),n6=str(6*cnt['F1']),n2=str(2*cnt['F1']),
         temp=str(one(qw,'temperature')),seed=str(one(qw,'seed')),think=th(one(qw,'thinking_token_budget')),maxtok=th(one(qw,'max_tokens')),
         gtopp=str(one(gw,'top_p')),gmax=th(one(gw,'max_tokens')),
         ndev=str(len(dev)),devwin=str(devw['F1']),devnormwin=str(devw['Normal']),devruns=WORD[devr['F1']],
         rounds=str(rec['rounds']),elocal=WORD[rec['e_local']],eta=str(rec['eta']),nseeds=WORD[len(seeds)],resamples=th(QJ['resamples']),
         quote=quote,fnw=str(f0['normal_windows']),fnwt=str(f0['normal_windows_total']),wlen=str(next(iter(wl))),w0=str(w0),w1=str(w1),horizon=str(w1-w0))
SETTING=[
 ('abstract',r'In a prespecified test on <nrun> new simulation runs'),
 ('introduction',r'two prespecified test families on <nrun> new runs'),
 ('introduction',r'accuracy on local-unseen faults was <luB0>\% vs.\ <luA0>\% with local examples alone, while own-fault accuracy was lower (<ownB0>\% vs.\ <ownA0>\%). Adding an own-class insight to the peer prompt was associated with <A>~pp higher own-fault accuracy'),
 ('introduction',r"(<olF> vs.\ <olB> of <npn> decisions)"),
 ('introduction',r'the peer-insight LLM was <B1>~pp higher on fault 1 and <B8>~pp lower on fault 8; fixed FedAvg reached <luF>\% pooled local-unseen accuracy'),
 ('setting',r'A \emph{case} is a <wlen>-hour window from one run'),
 ('setting',r'For each fault class, <devwin> development windows from <devruns> runs are scanned'),
 ('setting',r'contain the same <nobs> observations and headers'),
 ('setting',r"``<quote>''"),
 ('setting',r'this occurs in <fnw> of <fnwt> Normal development windows'),
 ('setting',r'Generation uses temperature <temp> and seed <seed>, with a <think>-token thinking budget and up to <maxtok> completion tokens'),
 ('setting',r'wrote <aggn> entries, <agg1> on single classes and <agg2> contrasting two classes'),
 ('setting',r'<devwin> windows for each of eight faults and <devnormwin> pooled Normal windows'),
 ('setting',r'(<rounds> rounds, <elocal> local epochs per round, learning rate <eta>, no regularization, <nseeds> seeds, class probabilities averaged)'),
 ('setting',r'the mean of <devnormwin> pooled Normal windows'),
 ('setting',r'top-$p$ <gtopp>, unrestricted top-$k$, low reasoning effort, a <gmax>-token output cap'),
 ('setting',r'<ndev>-run development pool'),
 ('design',r'The new cohort contains <nrun> disjoint-stream runs (<nperf> per fault, <nnormrun> Normal)'),
 ('design',r'eight half-open <wlen>-hour windows cover $[<w0>,<w1>)$~h'),
 ('design',r'all <nrun> runs passed technical checks without replacement'),
 ('design',r'This produces <npo> own-fault, <npl> local-unseen and <npn> Normal receiver pairs per condition'),
 ('design',r'received <tot> requests in total'),
 ('design',r'Normal averages its <nnormrun> run differences'),
 ('design',r'For Family~A, $K=<K>$, $n_f=<nperf>$'),
 ('design',r'Family~A tests \cond{FULL}$-$\cond{B0} on <npo> own-fault runs'),
 ('design',r"Each fault's <nperf> run differences"),
 ('design',r'Pointwise percentile intervals use <resamples> within-fault run resamples'),
 ('captions',r'Prospectively specified <nrun>-run test'),
 ('captions',r'Family A uses <npo> own-fault physical runs; Family B uses <nperf> runs per fault'),
 ('captions',r'(<npercond> pairs per LLM condition)'),
 ('captions',r'tied runs (<nperf> per fault)'),
 ('captions',r'Each own-fault value has <nperf> physical runs; each local-unseen value has the same <nperf> runs'),
 ('captions',r': <npo>, <n6> and <n2> physical runs'),
 ('captions',r'<npo> own-fault, <npl> local-unseen and <npn> Normal pairs per condition. Abstentions out of <npercond>'),
 ('captions',r'all <npercond> requests per condition'),
 ('family B',r"F1's <nperf> runs contain"),
 ('limitations',r'a fixed <horizon>-hour horizon'),
 ('limitations',r'the <nperf> runs per fault'),
 ('conclusion',r'benchmark of <nrun> new runs'),
 ('availability',r'The materials of the <nrun>-run test'),
 ('availability',r'raw responses of both LLMs (<tot> each)'),
]
# statements checked as conditions; the listed text is marked as covered when the condition holds
order_f={f:i for i,f in enumerate(FAULTS)}
def rule_ok(c):
    v=cases[c]; k=int(v['class_position_k']); j=int(v['window_ordinal']); o=order_f.get(v['true_label'],0)
    return j==1+((k-1+o)%8) and float(v['window_start_h'])==25+5*(j-1) and float(v['window_end_h'])==30+5*(j-1)
cover=Counter((truth(c),int(cases[c]['window_ordinal'])) for c in cases)
spans={(f_['from_h'],f_['to_h']) for k in order for f_ in json.loads(struct[k])['facts']}
maxlen={'accepted':0,'rejected_min':10**9}
for r in gz(R+'/responses/qwen_responses.jsonl.gz'):
    try: sm=json.loads(json.loads(base64.b64decode(r['response_raw_base64']))['choices'][0]['message']['content']).get('reasoning_summary')
    except Exception: continue
    if not isinstance(sm,str): continue
    if Q[r['key']]['state']=='invalid': maxlen['rejected_min']=min(maxlen['rejected_min'],len(sm))
    elif Q[r['key']]['state'] in('valid','abstain'): maxlen['accepted']=max(maxlen['accepted'],len(sm))
qacc=json.load(open(R+'/analysis/qwen_supplemental_accounting.json'))
SETTING_CHECKS=[
 ('window rule j=1+((k-1+o) mod 8), interval [25+5(j-1),30+5(j-1)), offsets 0-7 in fault order and 0 for Normal: all cases',all(rule_ok(c) for c in cases),
  [r'$j=1+((k-1+o_\ell)\bmod 8)$, giving interval $[25+5(j-1),30+5(j-1))$. Offsets are 0--7 in the listed fault order and 0 for Normal']),
 ('each fault covers every window three times and Normal eight times',all(cover[(f,j)]==3 for f in FAULTS for j in range(1,9)) and all(cover[('Normal',j)]==8 for j in range(1,9)),[]),
 ('all simulations complete, no replacement, all stream IDs distinct',all(cases[c]['simulation_status']=='complete' and cases[c]['replacement_reason'] in (None,'','None') and cases[c]['replacement_stream_id'] in (None,'','None') for c in cases) and len({cases[c]['stream_id'] for c in cases})==len(cases),[]),
 ('retained observations use only the spans 25-65, 25-35 and 35-65 h',spans<={(25,65),(25,35),(35,65)},[r'three time spans (25--65, 25--35 and 35--65~h)']),
 ('every rejected summary is longer than 1,200 characters and no accepted one is',maxlen['rejected_min']>1200>=maxlen['accepted'],
  [r'strings longer than 1,200 characters',r'the client-side 1,200-character']),
 ('excerpt fields of the structured F1 record: class_windows 40, positive 40, negative 0',(f0['class_windows'],f0['positive'],f0['negative'],f0['observation'],f0['variable'])==(40,40,0,'largest above-threshold level shift','XMEAS-1'),[]),
 ('development streams: every run has eight windows over 25-65 h',all(r['windowCount']==8 and r['windowStartHours']==25 and r['windowEndHours']==65 for r in dev),[]),
 ('primary service reports vLLM 0.27.1 (accounting file; the gpt-oss half of the sentence is not in the package)','"vllmVersion": "0.27.1"' in json.dumps(qacc),[]),
 ('gpt-oss requests: top_k -1 (unrestricted) and reasoning_effort low',one(gw,'top_k')==-1 and one(gw,'reasoning_effort')=='low',[]),
 ('FedAvg recipe: lambda 0 (no regularization)',rec['lam']==0,[]),
]
CLAIMS+=SETTING
norm=lambda s: re.sub(r'\s+',' ',s)
T=norm(TEX); ok=0; bad=[]; covered=[False]*len(T)
for sec,tpl in CLAIMS:
    frag=norm(re.sub(r'<(\w+)>',lambda m: V[m.group(1)],tpl)); i=T.find(frag)
    if i<0: bad.append((sec,frag)); continue
    ok+=1
    while i>=0:
        covered[i:i+len(frag)]=[True]*len(frag); i=T.find(frag,i+1)
# statements that are not a single number in a sentence
pvalA=float(2*stats.t.sf(abs(e/se),df)); gl={f:(sum(d[c]>0 for c in own if truth(c)==f),sum(d[c]<0 for c in own if truth(c)==f)) for f in FAULTS}
lub0={f:acc('qwen',[f],'lu','B0') for f in FAULTS}; lufed={f:acc('qwen',[f],'lu','FedAvg') for f in FAULTS}; lupro={f:acc('qwen',[f],'lu','PROTO') for f in FAULTS}
xmi=next(r for r in GJ['contrasts'] if r['model']=='gptoss_minus_qwen_effect' and r['domain']=='all_faults' and r['visibility']=='own' and r['contrast']=='FULL-B0')['pointwise95']
gp={p:con('gptoss',p,'own','B0','PROTO') for p in P}; gl_={p:con('gptoss',p,'lu','FULL','B0') for p in P}
checks=[('abstract: Family A p < 0.001',pvalA<0.001),('abstract: both Holm-adjusted p < 0.001',max(holm.values())<0.001),
 ('F2 and F10 at ceiling in B0 and FULL (own-fault)',all(acc('qwen',[f],'own',a)==100 for f in('F2','F10') for a in('B0','FULL'))),
 ('F13 has one gain and one loss',gl['F13']==(1,1)),('four F15 runs are worse in FULL',gl['F15'][1]==4),
 ('relaxed cap: extra correct answers are one own-fault FULL and one local-unseen S0; all A0 rejections local-unseen',extra_ok),
 ('AGG-FULL local-unseen is exactly zero',abs(con('qwen','all','lu','AGG','FULL'))<1e-12),('S0-B0 own-fault is exactly zero',abs(con('qwen','all','own','S0','B0'))<1e-12),
 ('gpt-oss has no rejection or truncation',set(gs)<={'valid','abstain'}),
 ('between-system FULL-B0 interval spans zero',xmi[0]<0<xmi[1]),
 ('gpt-oss own-fault B0-PROTO negative in all three partitions',all(v<0 for v in gp.values())),
 ('on F8 both numerical references outperform B0 (local-unseen)',lupro['F8']>lub0['F8'] and lufed['F8']>lub0['F8']),
 ('B0 exceeds FedAvg (local-unseen, by fault) only on F3 and F15',{f for f in FAULTS if lub0[f]>lufed[f]}=={'F3','F15'}),
 ('FedAvg exceeds every LLM condition on pooled local-unseen accuracy',acc('qwen',FAULTS,'lu','FedAvg')>max(acc('qwen',FAULTS,'lu',a) for a in ARMS)),
 ('both numerical references exceed every LLM condition on Normal',min(nor['PROTO'],nor['FedAvg'])>max(nor[a] for a in ARMS)),
 ('FULL remains below A0 on own-fault for gpt-oss',acc('gptoss',FAULTS,'own','FULL')<acc('gptoss',FAULTS,'own','A0'))]
for label,okk,frs in SETTING_CHECKS:
    checks.append((label,okk))
    if okk:
        for fr in frs:
            fr=norm(fr); i=T.find(fr); assert i>=0,fr
            while i>=0:
                covered[i:i+len(fr)]=[True]*len(fr); i=T.find(fr,i+1)
print('gpt-oss local-unseen FULL-B0 by partition (text: "near zero in each"):',{p:round(v,2) for p,v in gl_.items()})
for label,okk in checks: print(('ok      ' if okk else 'DIFFERS ')+label)
for sec,frag in bad: print(f'NOT FOUND [{sec}]: {frag}')
print(f'fragments checked: {len(CLAIMS)}, found with recomputed numbers: {ok}, not found: {len(bad)}; statements checked as conditions: {len(checks)}, differing: {sum(not o for _,o in checks)}')
# ---------------------------------------------------------------- inventory of what is NOT covered
# Every numeric token of the manuscript body (title to the end of the reproducibility section,
# captions included) that lies outside the matched fragments. Excluded as non-numeric statements:
# condition names (\cond{A0}...), fault and variable names (F1, XMEAS-1), labels, references,
# citations, LaTeX lengths and the figure code. The list is written to <output file> when a sixth
# argument is given, so that uncovered statements can be tracked one by one.
body_a=T.find(r'\begin{abstract}'); body_b=T.find(r'\bibliographystyle')
if body_b<0: body_b=len(T)
mask=list(T)
def blank(pattern,flags=0):
    for m in re.finditer(pattern,T,flags):
        for k in range(m.start(),m.end()): mask[k]=' '
blank(r'\\begin\{figure\}.*?\\end\{figure\}'); blank(r'\\begin\{equation\}.*?\\end\{equation\}')
blank(r'\\cond\{[^}]*\}'); blank(r'\\(?:ref|label|cite|input|setlength|IEEEtriggeratref|texttt|url)\{[^}]*\}(?:\{[^}]*\})?'); blank(r'\\begin\{table\*?\}\[[^\]]*\]')
blank(r'XMEAS-?\d*'); blank(r'\bfault \d+\b'); blank(r'\$F_1\$'); blank(r'HTTP 200'); blank(r's_f\^2'); blank(r'\$\\alpha=0\.05\$'); blank(r'\bF\d+(?:/F\d+)*\b'); blank(r'IDV\(?\d+\)?'); blank(r'N1-N5|P05-INS-F\d+|Qwen3\.5-122B-A10B-FP8|qwen3\.5-122b|gpt-oss-120b|\$2\\times2\$|\$10\^\{-12\}\$|2\^\{24\}')
M=''.join(mask)
secs=[(m.start(),re.sub(r'\\[A-Za-z]+\{?|[{}]','',m.group(1))) for m in re.finditer(r'\\(?:sub)?section\{([^}]*)\}',T)]
def section_of(pos):
    name='Abstract'
    for a,n in secs:
        if a<=pos: name=n
    return name
numre=re.compile(r'(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?')
rows=[]; total=0
for m in numre.finditer(M,body_a,body_b):
    s_=m.group(0).rstrip(','); pos=m.start(); total+=1
    if all(covered[pos:pos+len(s_)]): continue
    rows.append((section_of(pos),s_,T[max(body_a,pos-60):pos+len(s_)+40].strip()))
print(f'\nnumeric tokens in the manuscript body: {total}; inside a checked fragment: {total-len(rows)}; outside: {len(rows)}')
by=Counter(r[0] for r in rows)
for k,v in by.items(): print(f'   {v:4d}  {k}')
if len(sys.argv)>6:
    with open(sys.argv[6],'w',encoding='utf-8') as f:
        f.write('section\tnumber\tcontext\n')
        for r in rows: f.write('\t'.join(x.replace('\t',' ') for x in r)+'\n')
    print('list written to',sys.argv[6])
