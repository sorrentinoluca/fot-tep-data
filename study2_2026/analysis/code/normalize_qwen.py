"""Normalize immutable Qwen S07 responses without evaluator access.

This emits prediction labels and format states, but performs no truth join or
correctness calculation. The four-field parser mirrors src/inference/runner.py
at SHA-256 0cc2967b85b7a218f1f9c01e1454f2ccfbbe9c4ee11a5723fa4b55be09fcb983.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3


BACKUP_SHA = 'd6dbbc6224fd5d6a4cdd980d859706ed789f7b76bf67fbd4dea418d9b8336455'
ARMS = {'A0', 'B0', 'FULL', 'SELF', 'AGG', 'S0', 'PL0'}
LABELS = {'F1', 'F2', 'F3', 'F8', 'F10', 'F13', 'F14', 'F15', 'Normal'}


def strict_json(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique_pairs)


def classify(raw):
    try:
        envelope = strict_json(raw)
        choice = envelope['choices'][0]
        usage = envelope.get('usage') or {}
        if not isinstance(usage, dict):
            raise ValueError('usage not an object')
        details = usage.get('completion_tokens_details') or {}
        if not isinstance(details, dict):
            raise ValueError('completion details not an object')
        tokens = (usage.get('prompt_tokens'), usage.get('completion_tokens'),
                  details.get('reasoning_tokens'))
        finish = choice.get('finish_reason')
        if finish != 'stop':
            return ('truncated' if finish == 'length' else 'invalid', None, tokens)
        content = choice['message']['content']
        if not isinstance(content, str):
            raise ValueError('content not text')
        answer = strict_json(content)
        if not isinstance(answer, dict) or set(answer) != {
            'predicted_label', 'abstain', 'used_insight_ids', 'reasoning_summary'
        }:
            raise ValueError('four-field schema differs')
        label, abstain = answer['predicted_label'], answer['abstain']
        ids, summary = answer['used_insight_ids'], answer['reasoning_summary']
        if (type(abstain) is not bool or not isinstance(ids, list) or
                any(not isinstance(x, str) for x in ids) or len(ids) > 14 or
                len(ids) != len(set(ids)) or any(not x or len(x) > 128 for x in ids) or
                not isinstance(summary, str) or not summary.strip() or len(summary) > 1200 or
                (abstain and label is not None) or (not abstain and label not in LABELS)):
            raise ValueError('four-field content contract differs')
        return ('abstain' if abstain else 'valid', None if abstain else label, tokens)
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return ('invalid', None, (None, None, None))


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(backup: Path, output: Path):
    if output.exists():
        raise FileExistsError(output)
    digest = sha(backup)
    if digest != BACKUP_SHA:
        raise ValueError('S07 immutable backup digest differs')
    db = sqlite3.connect(f'file:{backup}?mode=ro&immutable=1', uri=True)
    seen, counts = set(), Counter()
    rows = []
    for key, arm, number, state, status, raw, raw_hash in db.execute(
        'SELECT a.key,r.arm,a.number,a.state,a.http_status,a.raw,a.raw_sha256 '
        'FROM attempts a JOIN registry r ON r.key=a.key ORDER BY r.ordinal'
    ):
        if (key in seen or arm not in ARMS or number != 1 or state != 'completed' or
                status != 200 or raw is None or hashlib.sha256(raw).hexdigest() != raw_hash):
            raise ValueError('S07 attempt/identity/raw-hash mismatch')
        seen.add(key)
        category, label, tokens = classify(raw)
        counts[category] += 1
        rows.append({'key': key, 'state': category, 'predicted_label': label,
                     'attempts': 1, 'input_tokens': tokens[0],
                     'output_tokens': tokens[1], 'reasoning_tokens': tokens[2],
                     'latency_ms': None, 'raw_sha256': raw_hash})
    db.close()
    if len(rows) != 14336 or any(sum(1 for row in rows if row['key'].endswith('|' + arm)) != 2048 for arm in ARMS):
        raise ValueError('fixed 14,336-key coverage differs')
    output.write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows), encoding='utf-8')
    return {'backupSha256': digest, 'normalizedSha256': sha(output),
            'plannedKeys': len(rows), 'formatCounts': dict(sorted(counts.items())),
            'truthRead': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('immutable_backup', type=Path)
    parser.add_argument('normalized_output', type=Path)
    args = parser.parse_args()
    print(json.dumps(normalize(args.immutable_backup, args.normalized_output), sort_keys=True))
