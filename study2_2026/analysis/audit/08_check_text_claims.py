"""Check current-snapshot quantitative statements against values recomputed from the archived response and prediction records.
Usage: python3 08_check_text_claims.py <study2_2026 dir> <pickle from 01> <manuscript .tex> <qwen_analysis.json> <combined_analysis.json>

Each claim is a sentence fragment copied from the manuscript in which every number has been
replaced by a value recomputed here (NumPy/SciPy, own parser). The check passes when the
fragment, with the recomputed numbers, occurs in the manuscript. "NOT FOUND" therefore means
that either the number or the wording differs: look at the fragment that is printed.
Taken from the two regenerated analysis JSON files instead of being recomputed: the seeded
bootstrap intervals and the two duplicate-input drop sensitivities (+20.9 on 189 runs, +85.7)."""
import sys, re, json, gzip, base64, pickle, hashlib
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
R=sys.argv[1]; cases,num,D=pickle.load(open(sys.argv[2],'rb')); TEX=open(sys.argv[3],encoding='utf-8').read()
EXPECTED_MANUSCRIPT_SHA256='a2818be4b66b684e73367acb0ec7e8ac98c7f6ca01aded3ef11824d3e181b0e4'
if hashlib.sha256(TEX.encode('utf-8')).hexdigest() != EXPECTED_MANUSCRIPT_SHA256:
    raise SystemExit('Manuscript SHA-256 differs from the audited snapshot; update the claim checker after reviewing the changed text.')
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
CLAIMS=[
 ('abstract',r'<luB0>\% accuracy on local-unseen faults vs.\ <luA0>\% with local examples alone; own-fault accuracy was <ownB0>\% vs.\ <ownA0>\%'),
 ('abstract',r'was associated with <A> percentage points (pp) higher own-fault accuracy'),
 ('abstract',r'were <olF> vs.\ <olB> of 512 decisions'),
 ('abstract',r'<B1>~pp higher on fault 1 and <B8>~pp lower on fault 8'),
 ('abstract',r'FedAvg reached <luF>\% pooled accuracy'),
 ('results',r'<valid> valid labeled answers, <abst> abstentions, <rej> parser rejections and <trunc> truncations'),
 ('results',r'Own-fault accuracy was lower, <nownB>/192 vs.\ <nownA>/192 ($<BA>$~pp'),
 ('family A',r'The Family~A difference is $<As>$~pp (95\% $t$ CI $[<los>,<his>]$, $p=<pA>$): <gain> runs gained, <loss> lost and <tie> tied'),
 ('family A',r'Normal false alarms numbered <faF> vs.\ <faB>'),
 ('family A',r'numbered <olF> vs.\ <olB>'),
 ('family A',r'F3/F15 contribute <net315> of the <nettot> net gains'),
 ('family A',r'Excluding F3/F15 gives $<six>$~pp (<cf>/144 vs.\ <cb>/144)'),
 ('family A',r'gives $<dropA>$~pp on <dropN> runs'),
 ('family A',r'recovers <extra> correct answers'),
 ('family B',r'exceeds \PROTO{} on F1 local-unseen pairs by $<B1s>$~pp (Holm $p=<h1>$), but falls below it on F8 by $<B8s>$~pp (Holm $p=<h8>$)'),
 ('family B',r'dropping one member gives $<dropB>$~pp on <dropBn> runs'),
 ('references',r'FedAvg exceeds every primary-LLM condition on pooled local-unseen accuracy (<luF>\% vs.\ at most <lumax>\%); \cond{B0}$-$FedAvg is $<BF>$~pp'),
 ('references',r'\PROTO{} scores <norP>\%, FedAvg <norF>\%'),
 ('controls',r'Own-fault \cond{SELF}$-$\cond{A0} is $<SA>$~pp'),
 ('controls',r'The $2\times2$ interaction is $<inter>$~pp'),
 ('controls',r'\cond{PL0}$-$\cond{B0} is $<PLB>$~pp'),
 ('controls',r'\cond{AGG}$-$\cond{FULL} is $<AFo>$~pp own-fault'),
 ('controls',r'Structured \cond{S0}$-$\cond{B0} is zero own-fault overall'),
 ('errors',r'\cond{SELF} abstains on <abSELF> (<abpSELF>\%) and \cond{PL0} on <abPL0> (<abpPL0>\%)'),
 ('errors',r'labels <f8f1B>/168 pairs as F1, compared with <f8f1F>/168 in \cond{FULL}'),
 ('errors',r'makes <eBn> Normal and <eBw> wrong-fault predictions; \cond{FULL} makes <eFn> and <eFw>'),
 ('errors',r'finds <idf> of <idt> cited insight-ID occurrences'),
 ('supplement',r'gpt-oss completed <gtotal> requests: <gvalid> valid answers and <gabst> abstentions'),
 ('supplement',r'Its own-fault \cond{FULL}$-$\cond{B0} is $<gFB>$~pp'),
 ('cost',r'occupy <natb> UTF-8 bytes joined by blank lines, or <strb> bytes as structured records'),
 ('cost',r'records <tin> input and <tout> output tokens'),
 ('limitations',r'<ndup> pairs of cases have identical model-facing inputs'),
 ('limitations',r'four duplicate input pairs generated <npairs> byte-identical request pairs across eight receivers and seven conditions. Response state and label agreed in <same> (<samep>\%)'),
 ('limitations',r'<sl> of <bv> pairs with two valid labels agreed (<slp>\%)'),
 ('limitations',r'<nsig> distinct signatures among 256 cases (maximum multiplicity <sigmax>)'),
 ('conclusion',r'False own-label assignments on Normal were <olF> vs.\ <olB> of 512 decisions'),
]
norm=lambda s: re.sub(r'\s+',' ',s)
T=norm(TEX); ok=0; bad=[]
for sec,tpl in CLAIMS:
    frag=norm(re.sub(r'<(\w+)>',lambda m: V[m.group(1)],tpl))
    if frag in T: ok+=1
    else: bad.append((sec,frag))
print(f'identity of the two extra correct answers and of the A0 rejections as stated: {"ok" if extra_ok else "DIFFERENT"}')
for sec,frag in bad: print(f'NOT FOUND [{sec}]: {frag}')
print(f'current-snapshot claims checked: {len(CLAIMS)}, found with recomputed numbers: {ok}, not found: {len(bad)}')
