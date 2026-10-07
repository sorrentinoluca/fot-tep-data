"""S09 supplemental cost/format accounting. Separate from the pinned primary analysis.

Truth-blind: reads only the immutable S07 backup and its own ledger metadata. It
never reads the evaluator manifest, performs no truth join, computes no score and
does not alter any primary estimate. It exists to disclose what the pinned
normalizer cannot carry: token usage for contract-failing responses, the reason
each rejected response failed, a reservation-to-finish duration proxy in place of
the unrecorded per-request latency, per-tier serving identity, and stored-byte
agreement for requests that were byte-identical on the wire.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics

BACKUP_SHA = 'd6dbbc6224fd5d6a4cdd980d859706ed789f7b76bf67fbd4dea418d9b8336455'
ARMS = ('A0', 'B0', 'FULL', 'SELF', 'AGG', 'S0', 'PL0')
LABELS = {'F1', 'F2', 'F3', 'F8', 'F10', 'F13', 'F14', 'F15', 'Normal'}
SUMMARY_CAP = 1200
LENGTH_BINS = (0, 200, 400, 600, 800, 1000, 1200, 1600, 2400, 10 ** 9)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def strict_json(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique_pairs)


def deployed_parser_reasons(answer):
    """Every deployed-parser-only constraint the four-field content contract applies."""
    reasons = []
    label, abstain = answer['predicted_label'], answer['abstain']
    ids, summary = answer['used_insight_ids'], answer['reasoning_summary']
    if type(abstain) is not bool:
        reasons.append('abstain_not_bool')
    if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
        reasons.append('used_insight_ids_not_string_list')
    else:
        if len(ids) > 14:
            reasons.append('used_insight_ids_over_14')
        if len(ids) != len(set(ids)):
            reasons.append('used_insight_ids_not_unique')
        if any(not x for x in ids):
            reasons.append('used_insight_id_empty')
        if any(len(x) > 128 for x in ids):
            reasons.append('used_insight_id_over_128_chars')
    if not isinstance(summary, str):
        reasons.append('reasoning_summary_not_string')
    else:
        if not summary.strip():
            reasons.append('reasoning_summary_blank_after_strip')
        if len(summary) > SUMMARY_CAP:
            reasons.append('reasoning_summary_over_1200_chars')
    if type(abstain) is bool:
        if abstain and label is not None:
            reasons.append('abstain_true_with_label')
        if not abstain and label not in LABELS:
            reasons.append('unsupported_or_missing_label')
    return reasons


def inspect_raw(raw):
    """Return (bucket, detail) describing where the deployed parser stopped."""
    try:
        envelope = strict_json(raw)
    except ValueError:
        return 'envelope_not_strict_json', {}
    try:
        choice = envelope['choices'][0]
    except (KeyError, IndexError, TypeError):
        return 'envelope_shape', {}
    usage = envelope.get('usage') or {}
    details = usage.get('completion_tokens_details') or {}
    tokens = {'prompt_tokens': usage.get('prompt_tokens') if isinstance(usage, dict) else None,
              'completion_tokens': usage.get('completion_tokens') if isinstance(usage, dict) else None,
              'reasoning_tokens': details.get('reasoning_tokens') if isinstance(details, dict) else None}
    finish = choice.get('finish_reason')
    out = {'finish_reason': finish, 'tokens': tokens}
    if finish != 'stop':
        return ('truncated_length' if finish == 'length' else 'non_stop_finish'), out
    content = choice.get('message', {}).get('content')
    if not isinstance(content, str):
        return 'content_not_text', out
    try:
        answer = strict_json(content)
    except ValueError:
        return 'content_not_strict_json', out
    if not isinstance(answer, dict) or set(answer) != {
            'predicted_label', 'abstain', 'used_insight_ids', 'reasoning_summary'}:
        return 'four_field_key_set', out
    reasons = deployed_parser_reasons(answer)
    summary = answer['reasoning_summary']
    out['summaryChars'] = len(summary) if isinstance(summary, str) else None
    out['usedInsightIdCount'] = len(answer['used_insight_ids']) if isinstance(answer['used_insight_ids'], list) else None
    if reasons:
        out['parserRejectionReasons'] = reasons
        return 'contract_rejected', out
    out['abstain'] = answer['abstain']
    return ('abstain' if answer['abstain'] is True else 'valid'), out


def bin_label(n):
    for lo, hi in zip(LENGTH_BINS, LENGTH_BINS[1:]):
        if lo <= n < hi:
            return f'{lo}-{hi - 1}' if hi < 10 ** 9 else f'{lo}+'
    return 'unbinned'


def parse_utc(text):
    return datetime.fromisoformat(text)


def run(backup: Path):
    digest = sha(backup)
    if digest != BACKUP_SHA:
        raise ValueError('S07 immutable backup digest differs')
    db = sqlite3.connect(f'file:{backup}?mode=ro&immutable=1', uri=True)
    per_arm = {arm: {'keys': 0, 'tier': None,
                     'fullInputTokens': 0, 'fullOutputTokens': 0, 'fullReasoningTokens': 0,
                     'primaryCountedInputTokens': 0, 'primaryCountedOutputTokens': 0,
                     'primaryCountedReasoningTokens': 0,
                     'buckets': Counter(), 'summaryCharBins': Counter(),
                     'summaryCharsTotal': 0, 'summaryCharsObserved': 0,
                     'durations': [], 'firstFinishUtc': None, 'lastFinishUtc': None}
               for arm in ARMS}
    rejection_reasons = Counter()
    rejection_by_arm = Counter()
    rejected_tokens = {'inputTokens': 0, 'outputTokens': 0, 'reasoningTokens': 0}
    rejected_summary_chars = []
    truncated_tokens = {'inputTokens': 0, 'outputTokens': 0, 'reasoningTokens': 0}
    wire_groups = defaultdict(list)
    for key, arm, tier, wire, state, reserved, finished, raw, raw_hash in db.execute(
            'SELECT a.key,r.arm,r.tier,r.wire_sha256,a.state,a.reserved_utc,a.finished_utc,a.raw,a.raw_sha256 '
            'FROM attempts a JOIN registry r ON r.key=a.key ORDER BY r.ordinal'):
        if hashlib.sha256(raw).hexdigest() != raw_hash:
            raise ValueError('raw provenance digest differs')
        slot = per_arm[arm]
        slot['keys'] += 1
        slot['tier'] = tier
        bucket, detail = inspect_raw(raw)
        slot['buckets'][bucket] += 1
        tokens = detail.get('tokens') or {}
        pin = tokens.get('prompt_tokens') or 0
        pout = tokens.get('completion_tokens') or 0
        pre = tokens.get('reasoning_tokens') or 0
        slot['fullInputTokens'] += pin
        slot['fullOutputTokens'] += pout
        slot['fullReasoningTokens'] += pre
        # the pinned normalizer discards usage whenever the content contract fails
        if bucket in ('valid', 'abstain', 'truncated_length', 'non_stop_finish'):
            slot['primaryCountedInputTokens'] += pin
            slot['primaryCountedOutputTokens'] += pout
            slot['primaryCountedReasoningTokens'] += pre
        if bucket == 'truncated_length':
            truncated_tokens['inputTokens'] += pin
            truncated_tokens['outputTokens'] += pout
            truncated_tokens['reasoningTokens'] += pre
        if bucket == 'contract_rejected':
            rejected_tokens['inputTokens'] += pin
            rejected_tokens['outputTokens'] += pout
            rejected_tokens['reasoningTokens'] += pre
            rejection_by_arm[arm] += 1
            for reason in detail['parserRejectionReasons']:
                rejection_reasons[reason] += 1
            if detail.get('summaryChars') is not None:
                rejected_summary_chars.append(detail['summaryChars'])
        if detail.get('summaryChars') is not None:
            slot['summaryCharBins'][bin_label(detail['summaryChars'])] += 1
            slot['summaryCharsTotal'] += detail['summaryChars']
            slot['summaryCharsObserved'] += 1
        if finished and reserved:
            slot['durations'].append((parse_utc(finished) - parse_utc(reserved)).total_seconds())
            slot['firstFinishUtc'] = min(slot['firstFinishUtc'] or finished, finished)
            slot['lastFinishUtc'] = max(slot['lastFinishUtc'] or finished, finished)
        wire_groups[wire].append((key, raw_hash))
    identity = defaultdict(list)
    for kind, at, detail in db.execute(
            "SELECT kind,at_utc,detail FROM events WHERE kind LIKE '%serving_identity' ORDER BY id"):
        payload = json.loads(detail)
        payload.pop('observedAtUtc', None)
        payload.pop('modelCardCreated', None)
        identity[kind].append((at, json.dumps(payload, sort_keys=True)))
    attempts_total, = db.execute('SELECT COUNT(*) FROM attempts').fetchone()
    adjudications, = db.execute('SELECT COUNT(*) FROM adjudications').fetchone()
    db.close()
    repeated = {wire: items for wire, items in wire_groups.items() if len(items) > 1}
    repeated_keys = sum(len(items) for items in repeated.values())
    identical_bytes = sum(1 for items in repeated.values()
                          for i in range(len(items)) for j in range(i + 1, len(items))
                          if items[i][1] == items[j][1])
    comparable_pairs = sum(len(items) * (len(items) - 1) // 2 for items in repeated.values())
    arms_out = {}
    for arm in ARMS:
        slot = per_arm[arm]
        durations = sorted(slot['durations'])
        arms_out[arm] = {
            'tier': slot['tier'], 'keys': slot['keys'],
            'buckets': dict(sorted(slot['buckets'].items())),
            'fullInputTokens': slot['fullInputTokens'],
            'fullOutputTokens': slot['fullOutputTokens'],
            'fullReasoningTokens': slot['fullReasoningTokens'],
            'primaryCountedInputTokens': slot['primaryCountedInputTokens'],
            'primaryCountedOutputTokens': slot['primaryCountedOutputTokens'],
            'primaryCountedReasoningTokens': slot['primaryCountedReasoningTokens'],
            'tokensOmittedByPinnedNormalizer': {
                'inputTokens': slot['fullInputTokens'] - slot['primaryCountedInputTokens'],
                'outputTokens': slot['fullOutputTokens'] - slot['primaryCountedOutputTokens'],
                'reasoningTokens': slot['fullReasoningTokens'] - slot['primaryCountedReasoningTokens']},
            'summaryCharBins': dict(sorted(slot['summaryCharBins'].items(),
                                           key=lambda kv: int(kv[0].split('-')[0].rstrip('+')))),
            'meanSummaryChars': (slot['summaryCharsTotal'] / slot['summaryCharsObserved']
                                 if slot['summaryCharsObserved'] else None),
            'reservationToFinishSeconds': {
                'observed': len(durations),
                'total': round(sum(durations), 3),
                'median': round(statistics.median(durations), 3) if durations else None,
                'p90': round(durations[int(0.9 * (len(durations) - 1))], 3) if durations else None,
                'max': round(max(durations), 3) if durations else None},
            'firstFinishUtc': slot['firstFinishUtc'], 'lastFinishUtc': slot['lastFinishUtc']}
    return {
        'analysisName': 'S09 supplemental cost/format accounting',
        'truthRead': False, 'scoresComputed': False, 'primaryEstimatesAffected': False,
        'backupSha256': digest,
        'attemptsTotal': attempts_total, 'adjudications': adjudications,
        'perArm': arms_out,
        'contractRejectedResponses': {
            'count': sum(rejection_by_arm.values()),
            'byArm': dict(sorted(rejection_by_arm.items())),
            'reasonOccurrences': dict(sorted(rejection_reasons.items())),
            'tokensNotCountedByPinnedNormalizer': rejected_tokens,
            'summaryCharsMin': min(rejected_summary_chars) if rejected_summary_chars else None,
            'summaryCharsMax': max(rejected_summary_chars) if rejected_summary_chars else None,
            'note': 'These responses are strict-schema-conformant on the transmitted wire schema '
                    'and are rejected only by deployed-parser-local constraints.'},
        'truncatedResponses': {'tokensCounted': truncated_tokens},
        'latency': {'perRequestLatencyRecorded': False,
                    'proxy': 'reserved_utc to finished_utc per attempt',
                    'proxyLimitation': 'Includes scheduler reservation overhead and is not server-side '
                                       'request latency; no latency field exists in the ledger.'},
        'servingIdentityByKind': {kind: {'events': len(items),
                                         'distinctFingerprintsIgnoringTimestamps': len({p for _, p in items}),
                                         'firstAtUtc': items[0][0], 'lastAtUtc': items[-1][0],
                                         'fingerprint': json.loads(items[0][1])}
                                  for kind, items in identity.items()},
        'byteIdenticalRequestAgreement': {
            'distinctRepeatedWireDigests': len(repeated), 'keysInRepeatedGroups': repeated_keys,
            'comparableKeyPairs': comparable_pairs, 'pairsWithIdenticalStoredBytes': identical_bytes,
            'note': 'Compares stored response SHA-256 only; request-linked raw response bodies are published in responses/qwen_responses.jsonl.gz.'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('immutable_backup', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    payload = run(args.immutable_backup)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'analysisName': payload['analysisName'],
                      'contractRejected': payload['contractRejectedResponses']['count'],
                      'byteIdenticalPairsAgreeing': payload['byteIdenticalRequestAgreement'],
                      'output': str(args.output)}, sort_keys=True))
