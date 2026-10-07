"""Compare two analysis JSON files: largest numeric difference and any non-numeric difference.
Usage: python3 compare_json.py <a.json> <b.json>"""
import json, sys, math
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
mx=[0.0,None]; nn=[]; cnt=[0]
def walk(x,y,p):
    if isinstance(x,dict) and isinstance(y,dict):
        for k in set(x)|set(y):
            if k not in x or k not in y: nn.append((p+'/'+k,'missing key')); continue
            walk(x[k],y[k],p+'/'+k)
    elif isinstance(x,list) and isinstance(y,list):
        if len(x)!=len(y): nn.append((p,'len')); return
        for i,(u,v) in enumerate(zip(x,y)): walk(u,v,p+'/%d'%i)
    elif isinstance(x,float) or isinstance(y,float):
        if isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool):
            cnt[0]+=1
            d=abs(x-y)
            if d>mx[0]: mx[0]=d; mx[1]=p
        else: nn.append((p,repr(x)[:60],repr(y)[:60]))
    else:
        if x!=y: nn.append((p,repr(x)[:80],repr(y)[:80]))
walk(a,b,'')
print('floats compared',cnt[0],'max abs diff',mx); print('non-numeric diffs',len(nn)); [print(' ',n) for n in nn[:30]]
