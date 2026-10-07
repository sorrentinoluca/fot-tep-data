"""Render fixed R08 exploratory descriptive results from the frozen R07 analysis JSON."""

import json
from pathlib import Path
import sys

ARMS=('A0','B0','FULL','SELF','AGG','S0','PL0')
FAULTS=('F1','F2','F3','F8','F10','F13','F14','F15')


def main(source,out):
    x=json.loads(Path(source).read_text())
    rows=x['contrasts']
    def get(domain,visibility,contrast,model):
        found=[r for r in rows if r['domain']==domain and r['visibility']==visibility and r['contrast']==contrast and r.get('model')==model]
        if len(found)!=1 or 'estimate' not in found[0]:
            raise ValueError((domain,visibility,contrast,model,len(found)))
        return found[0]
    def pct(x):return f'{100*x:+.3f}'
    def ci(r):
        v=r.get('pointwise95')
        return 'unavailable' if v is None else f'[{100*v[0]:+.3f}, {100*v[1]:+.3f}]'
    lines=['# R08 exploratory descriptive result tables','',
           'All values are fixed-denominator operational correctness or run-paired contrasts from the frozen R07 analysis. Intervals are pointwise descriptive, not confirmatory tests. Configured-model comparisons do not isolate model weights.','']
    lines+=['## Seven-arm means by domain','',
            '| Model | Domain | '+' | '.join(ARMS)+' |',
            '| --- | --- | '+' | '.join('---:' for _ in ARMS)+' |']
    for model in ('gptoss','qwen'):
        for domain,vis,label in (('all_faults','own','Own fault'),('all_faults','local_unseen','Local unseen'),('Normal','Normal','Normal')):
            values=[pct(get(domain,vis,'mean_'+arm,model)['estimate']) for arm in ARMS]
            lines.append('| '+model+' | '+label+' | '+' | '.join(values)+' |')
    lines+=['','## Main descriptive contrasts and fixed partitions','',
            '| Partition | Domain | Contrast | gpt-oss estimate (pp) | gpt-oss pointwise 95% | Qwen estimate (pp) | Matched gpt-oss minus Qwen effect (pp) | Matched pointwise 95% |',
            '| --- | --- | --- | ---: | --- | ---: | ---: | --- |']
    for domain in ('all_faults','excluding_F1_F8','F1_F8'):
        for vis in ('own','local_unseen'):
            for contrast in ('FULL-B0','B0-PROTO'):
                g=get(domain,vis,contrast,'gptoss')
                q=get(domain,vis,contrast,'qwen') if contrast!='B0-PROTO' else None
                m=get(domain,vis,contrast,'gptoss_minus_qwen_effect') if contrast!='B0-PROTO' else None
                lines.append('| '+' | '.join((domain,vis,contrast,pct(g['estimate']),ci(g),
                                             pct(q['estimate']) if q else 'not defined',
                                             pct(m['estimate']) if m else 'not defined',
                                             ci(m) if m else 'not defined'))+' |')
    lines+=['','B0−PROTO is defined for gpt-oss only in the frozen R07 analysis; Qwen B0−PROTO is reported in S09.','',
            '## gpt-oss means by fault and domain','',
            '| Fault | Domain | '+' | '.join(ARMS)+' |',
            '| --- | --- | '+' | '.join('---:' for _ in ARMS)+' |']
    for fault in FAULTS:
        for vis in ('own','local_unseen'):
            values=[pct(get(fault,vis,'mean_'+arm,'gptoss')['estimate']) for arm in ARMS]
            lines.append('| '+fault+' | '+vis+' | '+' | '.join(values)+' |')
    lines+=['','## gpt-oss response states by arm, all 2,048 planned keys each','',
            '| Arm | Planned | Attempted | Valid | Abstain | Invalid | Truncated | Missing |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for arm in ARMS:
        entries=[r for r in x['counts'] if r['model']=='gptoss' and r['arm']==arm and
                 (r['domain'],r['visibility']) in (('all_faults','own'),('all_faults','local_unseen'),('Normal','Normal'))]
        if len(entries)!=3:raise ValueError('count domain missing')
        def total(field):return sum(r[field] for r in entries)
        lines.append(f'| {arm} | {total("planned")} | {total("attempted")} | {total("valid")} | {total("abstain")} | {total("invalid")} | {total("truncated")} | {total("missing")} |')
    lines+=['','The complete machine-readable output contains every prespecified contrast, count and collision sensitivity. No arm or fault is selected by result direction.','']
    Path(out).write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: render_tables.py ANALYSIS.json TABLES.md')
    main(*sys.argv[1:])
