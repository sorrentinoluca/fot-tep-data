"""Prespecified Qwen T2 analysis. Never run before the reviewed S08 open event.

The input rows are a one-to-one normalization of the immutable S07 backup. This
module makes the first prediction/truth join, so invocation is an access event.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ARMS = ('A0', 'B0', 'FULL', 'SELF', 'AGG', 'S0', 'PL0')
FAULTS = ('F1', 'F2', 'F3', 'F8', 'F10', 'F13', 'F14', 'F15')
RECEIVERS = tuple('C_' + fault for fault in FAULTS)
LABELS = set(FAULTS) | {'Normal'}
STATES = {'valid', 'abstain', 'invalid', 'truncated', 'missing', 'uncertain'}
TRUTH_SHA = 'd8b5f379815c3fb5c3ddc1a7ef4c84fcb19efc8ff15e462a1576e082622993a4'
NUMERICAL_SHA = '55c125a1b09091a45c7a149970129d8b363c839f5121d436ba738e37d970eea3'
SEED = 20261006
RESAMPLES = 20000
COLLISION_CASE = 'case_208de85d389949569608a5a94d4dd19a'
DUPLICATE_INPUT_PAIRS = (
    ('case_0617f84123844834bbb8da2aa42ca582', 'case_bf19dbac638643edb2eb333532df1b09'),
    ('case_0e79c55689df4f5f966352afd33f3adc', 'case_47e998f732e548c88076ed9da43223f5'),
    ('case_10f4beae3ddf46f191b52d43236563fe', 'case_cbb9bbea62584e34818f951019fd4886'),
    ('case_15de141b3fce4de09e4dde88473d9b0f', 'case_e3b4f18cded74e768ec9aa331cd0dc5d'),
)
DUPLICATE_INPUT_DROP = frozenset(pair[1] for pair in DUPLICATE_INPUT_PAIRS)
CONTRASTS = {
    'B0-A0': {'B0': 1, 'A0': -1},
    'SELF-A0': {'SELF': 1, 'A0': -1},
    'FULL-SELF': {'FULL': 1, 'SELF': -1},
    'interaction': {'FULL': 1, 'SELF': -1, 'B0': -1, 'A0': 1},
    'AGG-FULL': {'AGG': 1, 'FULL': -1},
    'S0-B0': {'S0': 1, 'B0': -1},
    'PL0-B0': {'PL0': 1, 'B0': -1},
    'B0-PROTO': {'B0': 1, 'PROTO': -1},
    'B0-FedAvg': {'B0': 1, 'FedAvg': -1},
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl(path: Path):
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def load(truth_path: Path, outputs_path: Path, numerical_path: Path):
    if sha(truth_path) != TRUTH_SHA or sha(numerical_path) != NUMERICAL_SHA:
        raise ValueError('sealed evaluator or numerical prediction digest differs')
    cases = {}
    for row in jsonl(truth_path):
        cid, label = row['case_id'], row['true_label']
        owner = None if label == 'Normal' else 'C_' + label
        if cid in cases or label not in LABELS or row['owner_client_id'] != owner:
            raise ValueError('case/owner/label mismatch')
        cases[cid] = {'label': label, 'run': row['run_id'], 'owner': owner}
    if len(cases) != 256 or len({c['run'] for c in cases.values()}) != 256:
        raise ValueError('expected 256 independent physical runs')
    if COLLISION_CASE not in cases:
        raise ValueError('prespecified target/example collision case absent')
    if Counter(c['label'] for c in cases.values()) != Counter({**{f: 24 for f in FAULTS}, 'Normal': 64}):
        raise ValueError('fixed allocation differs')
    outputs = {}
    for row in jsonl(outputs_path):
        if set(row) != {'key', 'state', 'predicted_label', 'attempts', 'input_tokens',
                        'output_tokens', 'reasoning_tokens', 'latency_ms', 'raw_sha256'}:
            raise ValueError('normalized row schema differs')
        key = row['key']
        cid, receiver, arm = key.split('|')
        if key in outputs or cid not in cases or receiver not in RECEIVERS or arm not in ARMS:
            raise ValueError('duplicate or unknown output key')
        state, predicted = row['state'], row['predicted_label']
        if state not in STATES or (state == 'valid' and predicted not in LABELS) or (state != 'valid' and predicted is not None):
            raise ValueError('invalid output state/prediction')
        if type(row['attempts']) is not int or not 0 <= row['attempts'] <= 2:
            raise ValueError('transport attempt count differs')
        if (row['state'] in ('valid', 'abstain', 'invalid', 'truncated') and row['attempts'] == 0):
            raise ValueError('terminal response has no transport attempt')
        if (not isinstance(row['raw_sha256'], (str, type(None))) or
                (row['raw_sha256'] is not None and
                 (len(row['raw_sha256']) != 64 or any(ch not in '0123456789abcdef' for ch in row['raw_sha256'])))):
            raise ValueError('raw provenance digest differs')
        for field in ('input_tokens', 'output_tokens', 'reasoning_tokens'):
            value = row[field]
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError('token count differs')
        if row['latency_ms'] is not None and (not isinstance(row['latency_ms'], (int, float)) or row['latency_ms'] < 0):
            raise ValueError('latency value differs')
        outputs[key] = row
    expected = {f'{cid}|{receiver}|{arm}' for cid in cases for receiver in RECEIVERS for arm in ARMS}
    if set(outputs) != expected:
        raise ValueError('14,336-key Qwen grid differs')
    if sum(key.startswith(COLLISION_CASE + '|C_F2|') for key in outputs) != 7:
        raise ValueError('prespecified seven-key collision flag differs')
    numerical = {}
    for row in jsonl(numerical_path):
        cid = row['case_id']
        if cid in numerical or cid not in cases:
            raise ValueError('duplicate or unknown numerical case')
        if type(row['protoAbstain']) is not bool:
            raise ValueError('PROTO abstention flag differs')
        proto = None if row['protoAbstain'] else row['protoLabel']
        fedavg = row['fedavgLabel']
        if proto not in LABELS | {None} or fedavg not in LABELS:
            raise ValueError('invalid numerical prediction')
        numerical[cid] = {'PROTO': proto, 'FedAvg': fedavg}
    if set(numerical) != set(cases):
        raise ValueError('numerical case grid differs')
    return cases, outputs, numerical


def selected_cases(cases, faults, domain):
    if domain == 'Normal':
        return sorted(cid for cid, c in cases.items() if c['label'] == 'Normal')
    return sorted(cid for cid, c in cases.items() if c['label'] in faults)


def receivers(case, domain):
    if domain == 'Normal':
        return RECEIVERS
    if domain == 'own':
        return (case['owner'],)
    return tuple(receiver for receiver in RECEIVERS if receiver != case['owner'])


def score(cases, outputs, numerical, cid, receiver, arm):
    truth = cases[cid]['label']
    if arm in ('PROTO', 'FedAvg'):
        return int(numerical[cid][arm] == truth)
    row = outputs[f'{cid}|{receiver}|{arm}']
    return int(row['state'] == 'valid' and row['predicted_label'] == truth)


def run_values(cases, outputs, numerical, chosen, domain, coefficients):
    values = {}
    for cid in chosen:
        rxs = receivers(cases[cid], domain)
        values[cid] = sum(weight * sum(score(cases, outputs, numerical, cid, rx, arm) for rx in rxs) / len(rxs)
                          for arm, weight in coefficients.items())
    return values


def equal_fault_estimate(cases, values, chosen, faults):
    if not faults:
        return float(np.mean([values[cid] for cid in chosen]))
    return float(np.mean([np.mean([values[cid] for cid in chosen if cases[cid]['label'] == f]) for f in faults]))


def _beta_fraction(a, b, x):
    tiny, epsilon = 1e-300, 3e-14
    c, d, h = 1.0, 1.0 - (a + b) * x / (a + 1.0), 1.0
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
        d = 1 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
        d = 1 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1) < epsilon:
            return h
    raise ArithmeticError('incomplete-beta continued fraction did not converge')


def _regularized_beta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    prefactor = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                         + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return prefactor * _beta_fraction(a, b, x) / a
    return 1 - prefactor * _beta_fraction(b, a, 1 - x) / b


def t_survival(t_value, df):
    if t_value < 0 or df <= 0:
        raise ValueError('positive t and degrees of freedom required')
    return 0.5 * _regularized_beta(df / 2, 0.5, df / (df + t_value * t_value))


def t_critical_95(df):
    low, high = 0.0, 1.0
    while t_survival(high, df) > 0.025:
        high *= 2
    for _ in range(80):
        mid = (low + high) / 2
        if t_survival(mid, df) > 0.025:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def stratified_t(cases, values, chosen, faults):
    means, variances, n = [], [], []
    for fault in faults:
        vector = np.array([values[cid] for cid in chosen if cases[cid]['label'] == fault], dtype=float)
        if len(vector) < 2:
            raise ValueError('fault lacks independent runs')
        means.append(float(vector.mean()))
        variances.append(float(vector.var(ddof=1)))
        n.append(len(vector))
    estimate = float(np.mean(means))
    terms = [v / count for v, count in zip(variances, n, strict=True)]
    se = float(np.sqrt(sum(terms) / len(faults) ** 2))
    if se == 0:
        return {'estimate': estimate, 'se': 0.0, 'df': None, 'pointwise95': None, 'pTwoSided': None}
    df = sum(terms) ** 2 / sum(x * x / (count - 1) for x, count in zip(terms, n, strict=True))
    half_width = float(t_critical_95(df) * se)
    return {'estimate': estimate, 'se': se, 'df': df,
            'pointwise95': [estimate - half_width, estimate + half_width],
            'pTwoSided': float(2 * t_survival(abs(estimate / se), df))}


def sign_flip_exact(seven_times_run_differences):
    values = [int(x) for x in seven_times_run_differences]
    ways = Counter({0: 1})
    for value in values:
        updated = Counter()
        for total, multiplicity in ways.items():
            updated[total + value] += multiplicity
            updated[total - value] += multiplicity
        ways = updated
    observed = abs(sum(values))
    return sum(count for total, count in ways.items() if abs(total) >= observed) / 2 ** len(values)


def bootstrap(cases, values, chosen, faults):
    rng = np.random.Generator(np.random.PCG64(SEED))
    draws = []
    for fault in faults:
        vector = np.array([values[cid] for cid in chosen if cases[cid]['label'] == fault], dtype=float)
        indices = rng.integers(0, len(vector), size=(RESAMPLES, len(vector)))
        draws.append(vector[indices].mean(axis=1))
    sample = np.mean(np.stack(draws), axis=0)
    return [float(x) for x in np.quantile(sample, [0.025, 0.975], method='linear')]


def count_entries(cases, outputs, chosen, domain, arm):
    entries = [outputs[f'{cid}|{rx}|{arm}'] for cid in chosen for rx in receivers(cases[cid], domain)]
    states = Counter(row['state'] for row in entries)
    latencies = [row['latency_ms'] for row in entries if row['latency_ms'] is not None]
    return {'planned': len(entries), 'attempted': sum(row['attempts'] > 0 for row in entries),
            'transportAttempts': sum(row['attempts'] for row in entries),
            'states': {state: states[state] for state in sorted(STATES)},
            'inputTokens': sum(row['input_tokens'] or 0 for row in entries),
            'outputTokens': sum(row['output_tokens'] or 0 for row in entries),
            'reasoningTokens': sum(row['reasoning_tokens'] or 0 for row in entries),
            'latencyMsObservedCount': len(latencies),
            'latencyMsTotal': sum(latencies) if latencies else None}


def analyze(cases, outputs, numerical):
    if any(row['state'] in ('missing', 'uncertain') for row in outputs.values()):
        raise ValueError('incomplete tier: report a factual partial result, no confirmatory analysis')
    partitions = {'all_faults': FAULTS,
                  'excluding_F1_F8': tuple(f for f in FAULTS if f not in ('F1', 'F8')),
                  'F1_F8': ('F1', 'F8')}
    domains = [(name, faults, visibility) for name, faults in partitions.items()
               for visibility in ('own', 'local_unseen')]
    domains += [(fault, (fault,), visibility) for fault in FAULTS for visibility in ('own', 'local_unseen')]
    domains += [('Normal', (), 'Normal')]
    result = {'classification': 'Qwen T2 fixed-denominator analysis', 'seed': SEED,
              'resamples': RESAMPLES, 'families': {}, 'secondary': [], 'counts': [],
              'confusion': [], 'gainLoss': [], 'collisionWholeRunSensitivityPointOnly': [],
              'duplicateInputWholeRunSensitivityPointOnly': []}
    if len({cid for pair in DUPLICATE_INPUT_PAIRS for cid in pair}) != 8:
        raise ValueError('duplicate-input pair IDs overlap')
    if not all(cid in cases for pair in DUPLICATE_INPUT_PAIRS for cid in pair):
        raise ValueError('prespecified duplicate-input case absent')
    def duplicate_sensitivity(partition, domain, contrast, values, chosen, faults):
        retained = [cid for cid in chosen if cid not in DUPLICATE_INPUT_DROP]
        if len(retained) == len(chosen):
            return
        result['duplicateInputWholeRunSensitivityPointOnly'].append({
            'partition': partition, 'domain': domain, 'contrast': contrast,
            'estimate': equal_fault_estimate(cases, values, retained, faults),
            'plannedIndependentRuns': len(retained),
            'droppedCaseIds': sorted(set(chosen) & DUPLICATE_INPUT_DROP),
            'plannedReceiverKeys': sum(len(receivers(cases[cid], domain)) for cid in retained)})
    result['collisionVisibleF2ExampleMatchesTruth'] = cases[COLLISION_CASE]['label'] == 'F2'
    own = selected_cases(cases, FAULTS, 'own')
    full_b0 = run_values(cases, outputs, numerical, own, 'own', {'FULL': 1, 'B0': -1})
    result['families']['A_FULL_minus_B0'] = stratified_t(cases, full_b0, own, FAULTS)
    duplicate_sensitivity('all_faults', 'own', 'FULL-B0', full_b0, own, FAULTS)
    result['families']['A_FULL_minus_B0']['plannedIndependentRuns'] = len(own)
    result['families']['A_FULL_minus_B0']['perFault'] = {
        fault: {'mean': float(np.mean([full_b0[cid] for cid in own if cases[cid]['label'] == fault])),
                'runs': sum(cases[cid]['label'] == fault for cid in own),
                'gains': sum(full_b0[cid] > 0 for cid in own if cases[cid]['label'] == fault),
                'losses': sum(full_b0[cid] < 0 for cid in own if cases[cid]['label'] == fault)}
        for fault in FAULTS}
    raw_p = {}
    for fault in ('F1', 'F8'):
        chosen = selected_cases(cases, (fault,), 'local_unseen')
        differences = run_values(cases, outputs, numerical, chosen, 'local_unseen', CONTRASTS['B0-PROTO'])
        integer_sums = []
        for cid in chosen:
            value = differences[cid] * 7
            rounded = round(value)
            if not np.isclose(value, rounded, atol=1e-9, rtol=0):
                raise ValueError('seven-receiver contrast is not integral')
            integer_sums.append(rounded)
        raw_p[fault] = sign_flip_exact(integer_sums)
        duplicate_sensitivity(fault, 'local_unseen', 'B0-PROTO', differences, chosen, (fault,))
        result['families']['B_' + fault] = {'estimate': float(np.mean(list(differences.values()))),
                                           'plannedIndependentRuns': len(chosen), 'rawP': raw_p[fault]}
    ordered = sorted(raw_p, key=lambda fault: (raw_p[fault], fault))
    adjusted = {ordered[0]: min(1.0, 2 * raw_p[ordered[0]]),
                ordered[1]: max(min(1.0, 2 * raw_p[ordered[0]]), raw_p[ordered[1]])}
    for fault in ('F1', 'F8'):
        result['families']['B_' + fault]['holmAdjustedP'] = adjusted[fault]
    for name, faults, domain in domains:
        chosen = selected_cases(cases, faults, domain)
        for arm in ARMS:
            result['counts'].append({'partition': name, 'domain': domain, 'arm': arm,
                                     **count_entries(cases, outputs, chosen, domain, arm)})
            values = run_values(cases, outputs, numerical, chosen, domain, {arm: 1})
            result['secondary'].append({'partition': name, 'domain': domain, 'contrast': 'mean_' + arm,
                                        'estimate': equal_fault_estimate(cases, values, chosen, faults),
                                        'plannedIndependentRuns': len(chosen)})
            duplicate_sensitivity(name, domain, 'mean_' + arm, values, chosen, faults)
            if COLLISION_CASE in chosen:
                retained = [cid for cid in chosen if cid != COLLISION_CASE]
                result['collisionWholeRunSensitivityPointOnly'].append(
                    {'partition': name, 'domain': domain, 'contrast': 'mean_' + arm,
                     'estimate': equal_fault_estimate(cases, values, retained, faults),
                     'plannedIndependentRuns': len(retained),
                     'plannedReceiverKeys': sum(len(receivers(cases[cid], domain)) for cid in retained)})
        for label, coefficients in CONTRASTS.items():
            values = run_values(cases, outputs, numerical, chosen, domain, coefficients)
            row = {'partition': name, 'domain': domain, 'contrast': label,
                   'estimate': equal_fault_estimate(cases, values, chosen, faults),
                   'plannedIndependentRuns': len(chosen)}
            if faults and label in ('B0-PROTO', 'B0-FedAvg', 'B0-A0', 'SELF-A0',
                                    'FULL-SELF', 'interaction', 'AGG-FULL', 'S0-B0', 'PL0-B0'):
                row['stratifiedTDescriptive'] = stratified_t(cases, values, chosen, faults)
            if name in partitions and label == 'B0-PROTO' and domain == 'local_unseen':
                row['pointwiseBootstrap95'] = bootstrap(cases, values, chosen, faults)
            result['secondary'].append(row)
            duplicate_sensitivity(name, domain, label, values, chosen, faults)
            if COLLISION_CASE in chosen:
                retained = [cid for cid in chosen if cid != COLLISION_CASE]
                result['collisionWholeRunSensitivityPointOnly'].append(
                    {'partition': name, 'domain': domain, 'contrast': label,
                     'estimate': equal_fault_estimate(cases, values, retained, faults),
                     'plannedIndependentRuns': len(retained),
                     'plannedReceiverKeys': sum(len(receivers(cases[cid], domain)) for cid in retained)})
            positive = sum(value > 0 for value in values.values())
            negative = sum(value < 0 for value in values.values())
            companion = {'partition': name, 'domain': domain, 'contrast': label,
                         'runGain': positive, 'runLoss': negative,
                         'runTie': len(values) - positive - negative}
            if len(coefficients) == 2 and set(coefficients.values()) == {1, -1}:
                left = next(arm for arm, weight in coefficients.items() if weight == 1)
                right = next(arm for arm, weight in coefficients.items() if weight == -1)
                differences = [score(cases, outputs, numerical, cid, rx, left) -
                               score(cases, outputs, numerical, cid, rx, right)
                               for cid in chosen for rx in receivers(cases[cid], domain)]
                companion.update({'pairGain': sum(x > 0 for x in differences),
                                  'pairLoss': sum(x < 0 for x in differences),
                                  'pairTie': sum(x == 0 for x in differences)})
            result['gainLoss'].append(companion)
        if name in partitions and domain == 'own':
            row = {'partition': name, 'domain': domain, 'contrast': 'FULL-B0',
                   'estimate': equal_fault_estimate(cases, full_b0, chosen, faults),
                   'plannedIndependentRuns': len(chosen),
                   'stratifiedTDescriptive': stratified_t(cases, full_b0, chosen, faults),
                   'pointwiseBootstrap95': bootstrap(cases, full_b0, chosen, faults)}
            result['secondary'].append(row)
            duplicate_sensitivity(name, domain, 'FULL-B0', full_b0, chosen, faults)
            result['gainLoss'].append({'partition': name, 'domain': domain, 'contrast': 'FULL-B0',
                                       'runGain': sum(full_b0[cid] > 0 for cid in chosen),
                                       'runLoss': sum(full_b0[cid] < 0 for cid in chosen),
                                       'runTie': sum(full_b0[cid] == 0 for cid in chosen)})
            if COLLISION_CASE in chosen:
                retained = [cid for cid in chosen if cid != COLLISION_CASE]
                result['collisionWholeRunSensitivityPointOnly'].append(
                    {'partition': name, 'domain': domain, 'contrast': 'FULL-B0',
                     'estimate': equal_fault_estimate(cases, full_b0, retained, faults),
                     'plannedIndependentRuns': len(retained),
                     'plannedReceiverKeys': sum(len(receivers(cases[cid], domain)) for cid in retained)})
        if name in (*FAULTS, 'Normal'):
            for arm in ARMS:
                destinations = Counter()
                for cid in chosen:
                    for rx in receivers(cases[cid], domain):
                        row = outputs[f'{cid}|{rx}|{arm}']
                        destination = row['predicted_label'] if row['state'] == 'valid' else row['state']
                        destinations[destination] += 1
                result['confusion'].append({'sourceClass': name, 'domain': domain, 'arm': arm,
                                            'destinations': dict(sorted(destinations.items()))})
    result['normalFalseAlarmsAndOwnLabels'] = []
    normal = selected_cases(cases, (), 'Normal')
    for arm in ARMS:
        false_alarms = false_own = 0
        for cid in normal:
            for rx in RECEIVERS:
                row = outputs[f'{cid}|{rx}|{arm}']
                predicted = row['predicted_label'] if row['state'] == 'valid' else None
                false_alarms += predicted in FAULTS
                false_own += predicted == rx[2:]
        result['normalFalseAlarmsAndOwnLabels'].append({'arm': arm, 'falseAlarms': false_alarms,
                                                         'falseOwnLabelAssignments': false_own,
                                                         'plannedPairs': len(normal) * len(RECEIVERS)})
    result['collisionFlaggedKeys'] = [
        {'caseId': COLLISION_CASE, 'receiver': 'C_F2', 'arm': arm,
         'state': outputs[f'{COLLISION_CASE}|C_F2|{arm}']['state']}
        for arm in ARMS
    ]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('truth_manifest', type=Path)
    parser.add_argument('normalized_qwen', type=Path)
    parser.add_argument('numerical_predictions', type=Path)
    parser.add_argument('result', type=Path)
    args = parser.parse_args()
    if args.result.exists():
        raise FileExistsError(args.result)
    cases, outputs, numerical = load(args.truth_manifest, args.normalized_qwen, args.numerical_predictions)
    result = analyze(cases, outputs, numerical)
    result['sourceSha256'] = {'truthManifest': sha(args.truth_manifest),
                              'normalizedQwen': sha(args.normalized_qwen),
                              'numericalPredictions': sha(args.numerical_predictions)}
    result['analysisCodeSha256'] = sha(Path(__file__))
    args.result.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
