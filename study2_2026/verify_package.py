#!/usr/bin/env python3
"""Verify packaged artifact hashes and the gpt-oss request/response pairing."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
errors = []
for item in manifest["artifacts"]:
    path = ROOT / item["path"]
    if not path.is_file():
        errors.append(f"missing: {item['path']}")
        continue
    content = path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if len(content) != item["bytes"] or digest != item["sha256"]:
        errors.append(f"integrity mismatch: {item['path']}")

qwen_request_path = ROOT / "requests/qwen_requests.jsonl.gz"
if qwen_request_path.exists():
    with gzip.open(qwen_request_path, "rt", encoding="utf-8") as stream:
        qwen_keys = [json.loads(line)["key"] for line in stream]
    if len(qwen_keys) != 14336 or len(set(qwen_keys)) != 14336:
        errors.append("Qwen request archive is not 14,336 unique requests")

case_path = ROOT / "data/case_manifest.jsonl"
prediction_path = ROOT / "data/numerical_predictions.jsonl"
for path, label in [(case_path, "case manifest"), (prediction_path, "numerical predictions")]:
    if path.exists():
        with path.open(encoding="utf-8") as stream:
            rows = sum(1 for line in stream if line.strip())
        if rows != 256:
            errors.append(f"{label} has {rows} rows; expected 256")

request_path = ROOT / "requests/gpt_oss_requests.jsonl.gz"
response_path = ROOT / "responses/gpt_oss_responses.jsonl.gz"
if request_path.exists() and response_path.exists():
    with gzip.open(request_path, "rt", encoding="utf-8") as stream:
        requests = {json.loads(line)["key"] for line in stream}
    response_keys = set()
    with gzip.open(response_path, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            key = row["key"]
            response_keys.add(key)
            raw = base64.b64decode(row["response_raw_base64"], validate=True)
            if hashlib.sha256(raw).hexdigest() != row["response_sha256"]:
                errors.append(f"raw response hash mismatch: {key}")
            if row["http_status"] != 200 or row["state"] != "completed":
                errors.append(f"nonterminal response in public response archive: {key}")
    if len(requests) != 14336 or len(response_keys) != 14336 or requests != response_keys:
        errors.append("gpt-oss request/response keys are not a one-to-one 14,336-row match")

if errors:
    raise SystemExit("Package verification failed:\n- " + "\n- ".join(errors))
print(f"Verified {len(manifest['artifacts'])} artifacts, 14,336 Qwen requests, 256 cases/predictions, and 14,336 paired gpt-oss requests/responses.")
