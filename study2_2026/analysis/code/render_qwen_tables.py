"""Render the S09 result tables from the pinned analysis output and the supplemental accounting.

Presentation only: every number is read from S09_QWEN_T2_ANALYSIS.json (produced by the
pinned analyze_qwen.py at SHA-256 53bf18a2...) or from S09_SUPPLEMENTAL_ACCOUNTING.json.
No estimate, denominator, test or partition is recomputed, reweighted or filtered here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ARMS = ('A0', 'B0', 'FULL', 'SELF', 'AGG', 'S0', 'PL0')
FAULTS = ('F1', 'F2', 'F3', 'F8', 'F10', 'F13', 'F14', 'F15')
PARTITIONS = ('all_faults', 'excluding_F1_F8', 'F1_F8')
CONTRASTS = ('B0-A0', 'SELF-A0', 'FULL-SELF', 'interaction', 'AGG-FULL', 'S0-B0', 'PL0-B0',
             'FULL-B0', 'B0-PROTO', 'B0-FedAvg')
STATES = ('valid', 'abstain', 'invalid', 'truncated', 'missing', 'uncertain')


def pct(x, signed=False):
    if x is None:
        return 'n/a'
    return f'{100 * x:+.3f}' if signed else f'{100 * x:.3f}'


def ci(pair):
    return 'n/a' if not pair else f'[{100 * pair[0]:+.3f}, {100 * pair[1]:+.3f}]'


def pval(x):
    if x is None:
        return 'unavailable (SE=0)'
    return f'{x:.3e}' if x < 1e-4 else f'{x:.6f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('analysis', type=Path)
    ap.add_argument('supplemental', type=Path)
    ap.add_argument('out', type=Path)
    args = ap.parse_args()
    a = json.loads(args.analysis.read_text())
    s = json.loads(args.supplemental.read_text())
    sec = {(r['partition'], r['domain'], r['contrast']): r for r in a['secondary']}
    cnt = {(r['partition'], r['domain'], r['arm']): r for r in a['counts']}
    gl = {(r['partition'], r['domain'], r['contrast']): r for r in a['gainLoss']}
    conf = {(r['sourceClass'], r['domain'], r['arm']): r['destinations'] for r in a['confusion']}
    L = []
    w = L.append

    w('# S09 Qwen T2 fixed-denominator result tables')
    w('')
    w('All cells are rendered from the pinned analysis output '
      f"`S09_QWEN_T2_ANALYSIS.json` (analysis code SHA-256 `{a['analysisCodeSha256']}`) and from "
      '`S09_SUPPLEMENTAL_ACCOUNTING.json`. Percentages are fixed-denominator operational '
      'correctness: invalid, abstained, truncated and missing outputs are scored zero and are '
      'listed separately. A missing or rejected response is never described as a wrong diagnosis.')
    w('')
    w('## 1. Per-arm transport, format and correctness by domain (all eight faults)')
    w('')
    w('`correct` is the exact-top-one match count taken from the confusion destinations; '
      '`valid fraction` is terminal contract-valid keys over planned keys. Equal-weight fault '
      'means are in Table 2, and differ from correct/planned because each fault is weighted '
      'equally rather than by key count.')
    w('')
    for dom, label in (('own', 'Own-fault'), ('local_unseen', 'Local-unseen'), ('Normal', 'Normal')):
        part = 'Normal' if dom == 'Normal' else 'all_faults'
        classes = ('Normal',) if dom == 'Normal' else FAULTS
        w(f'### 1.{"abc"[("own", "local_unseen", "Normal").index(dom)]} {label} domain')
        w('')
        w('| Arm | Tier | Planned | Attempted | Transport attempts | Valid | Abstain | Invalid '
          '| Truncated | Missing | Uncertain | Correct | Correct/planned % | Valid fraction % '
          '| Input tokens | Output tokens | Reasoning tokens | Latency |')
        w('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|')
        for arm in ARMS:
            c = cnt[(part, dom, arm)]
            st = c['states']
            correct = sum(conf[(k, dom, arm)].get(k, 0) for k in classes)
            w(f"| {arm} | {s['perArm'][arm]['tier']} | {c['planned']} | {c['attempted']} "
              f"| {c['transportAttempts']} | " + ' | '.join(str(st[x]) for x in STATES) +
              f" | {correct} | {100 * correct / c['planned']:.3f} "
              f"| {100 * st['valid'] / c['planned']:.3f} | {c['inputTokens']} | {c['outputTokens']} "
              f"| {c['reasoningTokens']} (unobserved) | unavailable |")
        w('')
    w('Reasoning-token cells are zero only because `completion_tokens_details` is absent from all '
      '14,336 stored responses, so the 1,024-token thinking budget is unobservable from this '
      'evidence; they are not measured zeros. Latency is unrecorded in the ledger; see Table 11 '
      'for the reservation-to-finish proxy.')
    w('')

    w('## 2. Family A (primary) and Family B (selected confirmatory)')
    w('')
    fa = a['families']['A_FULL_minus_B0']
    w('| Family | Prespecified domain and independent unit | Estimate (pp) | Interval | Raw p '
      '| Adjusted p | Direction / limit |')
    w('|---|---|---:|---|---:|---:|---|')
    w(f"| A: FULL-B0 | Eight equal-weight fault means; {fa['plannedIndependentRuns'] // 8} own-fault "
      f"runs each, {fa['plannedIndependentRuns']} runs | {pct(fa['estimate'], True)} "
      f"| Welch-Satterthwaite 95%: {ci(fa['pointwise95'])}, SE {100 * fa['se']:.3f} pp, "
      f"df {fa['df']:.2f} | {pval(fa['pTwoSided'])} | N/A (single primary test at alpha 0.05) "
      '| Positive; rejects at alpha 0.05; model-conditional, assumes within-fault run '
      'independence and approximate t |')
    for fault in ('F1', 'F8'):
        fb = a['families']['B_' + fault]
        w(f"| B: {fault} B0-PROTO | {fb['plannedIndependentRuns']} {fault} runs; seven local-unseen "
          f"receivers averaged per run | {pct(fb['estimate'], True)} | N/A (exact sign-flip) "
          f"| {pval(fb['rawP'])} | Holm: {pval(fb['holmAdjustedP'])} "
          f"| {'Positive' if fb['estimate'] > 0 else 'Negative (adverse for B0)'}; rejects at "
          'alpha 0.05; sign-flip null requires run-wise sign invariance |')
    w('')
    w('Per-fault decomposition of the Family A paired difference (own-fault keys, 24 runs each):')
    w('')
    w('| Fault | Mean FULL-B0 (pp) | Runs | Runs with gain | Runs with loss | Runs tied |')
    w('|---|---:|---:|---:|---:|---:|')
    for fault in FAULTS:
        r = fa['perFault'][fault]
        w(f"| {fault} | {pct(r['mean'], True)} | {r['runs']} | {r['gains']} | {r['losses']} "
          f"| {r['runs'] - r['gains'] - r['losses']} |")
    w('')

    w('## 3. Prespecified descriptive sensitivity over the three fixed partitions')
    w('')
    w('| Partition | FULL-B0 own-fault (pp) | 20,000-resample pointwise 95% | B0-PROTO '
      'local-unseen (pp) | 20,000-resample pointwise 95% | Runs |')
    w('|---|---:|---|---:|---|---:|')
    for part in PARTITIONS:
        f1 = sec[(part, 'own', 'FULL-B0')]
        f2 = sec[(part, 'local_unseen', 'B0-PROTO')]
        w(f"| {part} | {pct(f1['estimate'], True)} | {ci(f1.get('pointwiseBootstrap95'))} "
          f"| {pct(f2['estimate'], True)} | {ci(f2.get('pointwiseBootstrap95'))} "
          f"| {f1['plannedIndependentRuns']} |")
    w('')
    w(f"Resampling: {a['resamples']} within-fault run resamples with replacement, PCG64 seed "
      f"{a['seed']}, included classes enumerated in the fixed order. These intervals are "
      'pointwise, unadjusted and descriptive; they are outside the Family B Holm family and a '
      'pointwise interval excluding zero is not an additional rejection.')
    w('')

    w('## 4. All prespecified secondary arm means, by partition and domain (%)')
    w('')
    w('| Partition | Domain | ' + ' | '.join(ARMS) + ' | PROTO | FedAvg | Runs |')
    w('|---|---|' + '---:|' * (len(ARMS) + 3))
    for part in PARTITIONS + FAULTS + ('Normal',):
        for dom in (('Normal',) if part == 'Normal' else ('own', 'local_unseen')):
            row = [pct(sec[(part, dom, 'mean_' + arm)]['estimate']) for arm in ARMS]
            b0 = sec[(part, dom, 'mean_B0')]['estimate']
            proto = b0 - sec[(part, dom, 'B0-PROTO')]['estimate']
            fed = b0 - sec[(part, dom, 'B0-FedAvg')]['estimate']
            w(f'| {part} | {dom} | ' + ' | '.join(row) + f' | {pct(proto)} | {pct(fed)} '
              f"| {sec[(part, dom, 'mean_B0')]['plannedIndependentRuns']} |")
    w('')
    w('PROTO and FedAvg columns are reconstructed exactly as `mean_B0 - (B0-PROTO)` and '
      '`mean_B0 - (B0-FedAvg)` from the pinned output. Their per-run label is receiver-invariant '
      'and copied across receiver keys; copies are not independent decisions.')
    w('')

    w('## 5. All prespecified secondary contrasts with descriptive summaries and gain/loss')
    w('')
    w('| Partition | Domain | Contrast | Estimate (pp) | Descriptive stratified-t 95% | '
      'Runs | Run gain | Run loss | Run tie | Pair gain | Pair loss | Pair tie |')
    w('|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|')
    for part in PARTITIONS + FAULTS + ('Normal',):
        for dom in (('Normal',) if part == 'Normal' else ('own', 'local_unseen')):
            for con in CONTRASTS:
                r = sec.get((part, dom, con))
                if r is None:
                    continue
                st = r.get('stratifiedTDescriptive') or {}
                g = gl.get((part, dom, con), {})
                w(f"| {part} | {dom} | {con} | {pct(r['estimate'], True)} "
                  f"| {ci(st.get('pointwise95')) if st else 'not prespecified'} "
                  f"| {r['plannedIndependentRuns']} | {g.get('runGain', '-')} "
                  f"| {g.get('runLoss', '-')} | {g.get('runTie', '-')} | {g.get('pairGain', '-')} "
                  f"| {g.get('pairLoss', '-')} | {g.get('pairTie', '-')} |")
    w('')
    w('No secondary p-value column is rendered. S05 section 5 prespecifies no secondary '
      'hypothesis test and no secondary p-value, so none is offered to readers here. The pinned '
      'pre-open analysis output `S09_QWEN_T2_ANALYSIS.json` does carry a descriptive '
      'stratified-t summary on 201 of its 371 prespecified secondary rows, all 201 of them rows '
      'of this table, of which 163 returned a non-null unadjusted two-sided value and 38 hit '
      'the zero-SE unavailable rule; that frozen file is '
      'retained unchanged at SHA-256 '
      '`df8ea84c4930e6439b5c8b40fc3615f4539370c279a16f7ddcea83dc4307673a` for audit only. None '
      'of those 163 values is used as a test, a rejection, a discovery or a familywise result '
      'anywhere in S09, and none may be cited as one. The interval column that remains is the '
      'descriptive stratified-t interval; it is unadjusted, is outside the Family B Holm family, '
      'and an interval excluding zero is not an additional rejection.')
    w('')

    w('## 6. Per-fault destination tables, all eight faults, every arm')
    w('')
    for fault in FAULTS:
        w(f'### 6.{FAULTS.index(fault) + 1} {fault}')
        w('')
        for dom in ('own', 'local_unseen'):
            planned = cnt[(fault, dom, 'A0')]['planned']
            w(f'{dom} domain, {planned} planned keys per arm:')
            w('')
            keys = sorted({k for arm in ARMS for k in conf[(fault, dom, arm)]})
            w('| Arm | correct (=' + fault + ') | ' + ' | '.join(k for k in keys if k != fault) + ' |')
            w('|---|---:|' + '---:|' * (len(keys) - (1 if fault in keys else 0)))
            for arm in ARMS:
                dest = conf[(fault, dom, arm)]
                w(f"| {arm} | {dest.get(fault, 0)} | " +
                  ' | '.join(str(dest.get(k, 0)) for k in keys if k != fault) + ' |')
            w('')
    w('Destination cells labelled `valid`-state labels are model answers; `abstain`, `invalid` '
      'and `truncated` cells are non-answers scored zero, not misdiagnoses.')
    w('')

    w('## 7. Normal domain: correctness, false alarms and false own-label assignments')
    w('')
    w('| Arm | Correct / 512 | False alarms / 512 | False own-label assignments / 512 | Abstain '
      '| Invalid | Truncated | Planned pairs |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|')
    fa_rows = {r['arm']: r for r in a['normalFalseAlarmsAndOwnLabels']}
    for arm in ARMS:
        r = fa_rows[arm]
        st = cnt[('Normal', 'Normal', arm)]['states']
        dest = conf[('Normal', 'Normal', arm)]
        w(f"| {arm} | {dest.get('Normal', 0)} | {r['falseAlarms']} | "
          f"{r['falseOwnLabelAssignments']} | {st['abstain']} | {st['invalid']} | "
          f"{st['truncated']} | {r['plannedPairs']} |")
    w('')
    w('Normal has 64 independent physical runs, each reused across eight receivers; 512 is a '
      'planned key count, not 512 independent observations.')
    w('')

    w('## 8. Labelled-example / target collision (seven flagged C_F2 keys)')
    w('')
    w(f"Flagged case `{a['collisionFlaggedKeys'][0]['caseId']}`, receiver C_F2, one key per arm. "
      f"The flagged case's evaluator label is F2: **{a['collisionVisibleF2ExampleMatchesTruth']}**, "
      'so the visible labelled example does reveal the correct label for those seven keys.')
    w('')
    w('| Arm | Terminal state of the flagged key |')
    w('|---|---|')
    for r in a['collisionFlaggedKeys']:
        w(f"| {r['arm']} | {r['state']} |")
    w('')
    w('Full-denominator results above are retained as primary. The prespecified whole-physical-run '
      'point-only sensitivity (dropping the one flagged case from every display containing it) is:')
    w('')
    w('| Partition | Domain | Contrast | Point estimate without the flagged run (pp) | Runs '
      '| Receiver keys |')
    w('|---|---|---|---:|---:|---:|')
    for r in a['collisionWholeRunSensitivityPointOnly']:
        w(f"| {r['partition']} | {r['domain']} | {r['contrast']} | {pct(r['estimate'], True)} "
          f"| {r['plannedIndependentRuns']} | {r['plannedReceiverKeys']} |")
    w('')
    w('No interval, p-value, rejection or denominator change is attached to any row in this table.')
    w('')

    w('## 9. Four duplicate model-facing inputs: point-only whole-run sensitivity')
    w('')
    w('Retained / dropped-in-sensitivity-only case pairs, fixed truth-blind on 2026-10-07 07:33 '
      'UTC and verified again in S09 on the frozen request grid:')
    w('')
    w('| Retain | Drop in sensitivity only |')
    w('|---|---|')
    for keep, drop in (('case_0617f84123844834bbb8da2aa42ca582', 'case_bf19dbac638643edb2eb333532df1b09'),
                       ('case_0e79c55689df4f5f966352afd33f3adc', 'case_47e998f732e548c88076ed9da43223f5'),
                       ('case_10f4beae3ddf46f191b52d43236563fe', 'case_cbb9bbea62584e34818f951019fd4886'),
                       ('case_15de141b3fce4de09e4dde88473d9b0f', 'case_e3b4f18cded74e768ec9aa331cd0dc5d')):
        w(f'| `{keep}` | `{drop}` |')
    w('')
    w('| Partition | Domain | Contrast | Point estimate with duplicates dropped (pp) | Runs '
      '| Receiver keys | Dropped case IDs |')
    w('|---|---|---|---:|---:|---:|---|')
    for r in a['duplicateInputWholeRunSensitivityPointOnly']:
        w(f"| {r['partition']} | {r['domain']} | {r['contrast']} | {pct(r['estimate'], True)} "
          f"| {r['plannedIndependentRuns']} | {r['plannedReceiverKeys']} "
          f"| {', '.join(c[5:13] for c in r['droppedCaseIds'])} |")
    w('')
    w('Point estimates only, across all receivers and arms. No replacement case, no alternative '
      'pair member chosen after labels, no new interval, p-value or rejection. This sensitivity '
      'describes possible dependence; it does not make the primary independence assumption true.')
    w('')

    w('## 10. Missingness, format and transport accounting')
    w('')
    w('| Quantity | Value |')
    w('|---|---:|')
    tot = {k: sum(cnt[(p, d, arm)][k] for arm in ARMS for p, d in
                  (('all_faults', 'own'), ('all_faults', 'local_unseen'), ('Normal', 'Normal')))
           for k in ('planned', 'attempted', 'transportAttempts')}
    w(f"| Planned semantic keys | {tot['planned']} |")
    w(f"| Keys with at least one transport attempt | {tot['attempted']} |")
    w(f"| Total transport attempts (ceiling 28,672) | {tot['transportAttempts']} |")
    w(f"| Adjudications required | {s['adjudications']} |")
    for state in STATES:
        n = sum(cnt[(p, d, arm)]['states'][state] for arm in ARMS for p, d in
                (('all_faults', 'own'), ('all_faults', 'local_unseen'), ('Normal', 'Normal')))
        w(f'| Terminal state `{state}` | {n} |')
    rej = s['contractRejectedResponses']
    w(f"| Contract-rejected responses (deployed-parser-only) | {rej['count']} |")
    w(f"| ... all rejected solely by the 1,200-character summary cap | "
      f"{rej['reasonOccurrences'].get('reasoning_summary_over_1200_chars', 0)} |")
    w(f"| ... rejected-response summary length range (chars) | "
      f"{rej['summaryCharsMin']}-{rej['summaryCharsMax']} |")
    w('')

    w('## 11. Supplemental cost and duration accounting (separately named, not a primary score)')
    w('')
    w('| Arm | Tier | Full input tokens | Full output tokens | Reasoning tokens | Input tokens '
      'omitted by the pinned normalizer | Output tokens omitted | Reservation-to-finish median s '
      '| p90 s | Total s | First finish UTC | Last finish UTC |')
    w('|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|')
    for arm in ARMS:
        v = s['perArm'][arm]
        o = v['tokensOmittedByPinnedNormalizer']
        r = v['reservationToFinishSeconds']
        w(f"| {arm} | {v['tier']} | {v['fullInputTokens']} | {v['fullOutputTokens']} "
          f"| unobserved | {o['inputTokens']} | {o['outputTokens']} | {r['median']} | {r['p90']} "
          f"| {r['total']:.0f} | {v['firstFinishUtc']} | {v['lastFinishUtc']} |")
    w('')
    w(f"Total tokens the pinned primary accounting omits: "
      f"{rej['tokensNotCountedByPinnedNormalizer']['inputTokens']} input and "
      f"{rej['tokensNotCountedByPinnedNormalizer']['outputTokens']} output, all from the "
      f"{rej['count']} contract-rejected responses. The reservation-to-finish column includes "
      'scheduler reservation overhead and is not server-side request latency; no latency field '
      'exists in the ledger, so the Latency column of the prepared displays stays unfillable.')
    w('')
    w('Per-tier serving identity:')
    w('')
    w('| Event kind | Events | Distinct fingerprints (timestamps ignored) | First UTC | Last UTC |')
    w('|---|---:|---:|---|---|')
    for kind, v in sorted(s['servingIdentityByKind'].items()):
        w(f"| {kind} | {v['events']} | {v['distinctFingerprintsIgnoringTimestamps']} "
          f"| {v['firstAtUtc']} | {v['lastAtUtc']} |")
    w('')
    fp = next(iter(s['servingIdentityByKind'].values()))['fingerprint']
    w(f"Observed fingerprint, identical for the interleaved primary pass and the later tier-4 "
      f"pass: model `{fp['modelId']}`, root `{fp['root']}`, vLLM `{fp['vllmVersion']}`, "
      f"maxModelLen {fp['maxModelLen']}, checkpointRevision {fp['checkpointRevision']}, "
      f"tokenizer fixture response SHA-256 `{fp['tokenizerFixtureResponseSha256']}`.")
    w('')

    w('## 12. Backend nondeterminism on byte-identical requests')
    w('')
    b = s['byteIdenticalRequestAgreement']
    w('| Quantity | Value |')
    w('|---|---:|')
    w(f"| Distinct wire digests sent more than once | {b['distinctRepeatedWireDigests']} |")
    w(f"| Keys inside those groups | {b['keysInRepeatedGroups']} |")
    w(f"| Comparable key pairs | {b['comparableKeyPairs']} |")
    w(f"| Pairs whose stored response bytes are identical | {b['pairsWithIdenticalStoredBytes']} |")
    w('')
    w('Under temperature 0, top_p 1 and seed 20260927, no byte-identical request pair returned '
      'byte-identical stored output. The campaign cannot be reproduced by re-sending; the '
      'immutable backup is the sole evidentiary record.')
    w('')

    w('## 13. Length-only baseline check')
    w('')
    w('| Length-only baseline check | Definition frozen before opening | Result | Limit |')
    w('|---|---|---|---|')
    w('| Scored comparator using response or prompt length without diagnostic text | **none** '
      '| not computed | No such comparator was defined or hashed before the opening, so any '
      'definition chosen now would be post-hoc. S09 declines to fill this cell rather than '
      'invent a comparator after truth access. |')
    w('')
    w('The only length-related evidence S09 can report without post-hoc definition is the '
      'truth-blind summary-length distribution measured before the first truth access:')
    w('')
    bins = sorted({b for arm in ARMS for b in s['perArm'][arm]['summaryCharBins']},
                  key=lambda x: int(x.split('-')[0].rstrip('+')))
    w('| Arm | Mean summary chars | ' + ' | '.join(bins) + ' |')
    w('|---|---:|' + '---:|' * len(bins))
    for arm in ARMS:
        v = s['perArm'][arm]
        w(f"| {arm} | {v['meanSummaryChars']:.1f} | " +
          ' | '.join(str(v['summaryCharBins'].get(b, 0)) for b in bins) + ' |')
    w('')
    w('Bins at or above 1200 characters are the region the deployed parser rejects outright.')
    w('')
    args.out.write_text('\n'.join(L).rstrip('\n') + '\n', encoding='utf-8')
    print(json.dumps({'tables': str(args.out), 'lines': len(L)}))


if __name__ == '__main__':
    main()
