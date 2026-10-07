#!/usr/bin/env python3
"""Verify package digests and request/response joins without external services."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = 14336
manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
errors = []

def rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)

def raw_sha(row):
    raw = base64.b64decode(row["response_raw_base64"], validate=True)
    if hashlib.sha256(raw).hexdigest() != row["response_sha256"]:
        errors.append(f"raw response hash mismatch: {row['key']}")

for item in manifest["artifacts"]:
    path = ROOT / item["path"]
    if not path.is_file():
        errors.append(f"missing: {item['path']}")
        continue
    content = path.read_bytes()
    if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
        errors.append(f"artifact integrity mismatch: {item['path']}")

for path, label in [(ROOT / "data/case_manifest.jsonl", "case manifest"),
                    (ROOT / "data/numerical_predictions.jsonl", "numerical predictions")]:
    if not path.is_file():
        errors.append(f"missing: {label}")
    elif sum(1 for line in path.open(encoding="utf-8") if line.strip()) != 256:
        errors.append(f"{label} does not contain 256 rows")

qreq = {r["key"]: r for r in rows(ROOT / "requests/qwen_requests.jsonl.gz")}
qnorm = {r["key"]: r for r in rows(ROOT / "responses/qwen_normalized_responses.jsonl.gz")}
qraw = {r["key"]: r for r in rows(ROOT / "responses/qwen_responses.jsonl.gz")}
if not (len(qreq) == len(qnorm) == len(qraw) == EXPECTED and set(qreq) == set(qnorm) == set(qraw)):
    errors.append("Qwen requests, normalized rows, and raw responses do not form a 14,336-key join")
else:
    for key, response in qraw.items():
        raw_sha(response)
        if response["response_sha256"] != qnorm[key]["raw_sha256"]:
            errors.append(f"Qwen raw/normalized digest mismatch: {key}")
        request = qreq[key]
        if request["arm"] != response["arm"]:
            errors.append(f"Qwen request/response arm mismatch: {key}")
        if response["http_status"] != 200 or response["state"] != "completed":
            errors.append(f"Qwen response is not terminal HTTP 200: {key}")

greq = {r["key"]: r for r in rows(ROOT / "requests/gpt_oss_requests.jsonl.gz")}
graw = {r["key"]: r for r in rows(ROOT / "responses/gpt_oss_responses.jsonl.gz")}
if not (len(greq) == len(graw) == EXPECTED and set(greq) == set(graw)):
    errors.append("gpt-oss requests and raw responses do not form a 14,336-key join")
else:
    for key, response in graw.items():
        raw_sha(response)
        request = greq[key]
        expected_key = request["pair_id"] + "|" + request["arm"]
        if response["scientific_key"] != expected_key or response["arm"] != request["arm"]:
            errors.append(f"gpt-oss request/response scientific-key mismatch: {key}")
        if response["http_status"] != 200 or response["state"] != "completed":
            errors.append(f"gpt-oss response is not terminal HTTP 200: {key}")

combined_path = ROOT / "responses/normalized_model_outputs.jsonl.gz"
combined = list(rows(combined_path))
if len(combined) != 2 * EXPECTED:
    errors.append("combined normalized response file does not contain 28,672 rows")
else:
    qkeys = [r["key"] for r in combined if r["model"] == "qwen"]
    gkeys = [r["key"] for r in combined if r["model"] == "gptoss"]
    expected_gkeys = {r["pair_id"] + "|" + r["arm"] for r in greq.values()}
    if len(qkeys) != EXPECTED or len(set(qkeys)) != EXPECTED or set(qkeys) != set(qnorm):
        errors.append("combined Qwen predictions do not match normalized Qwen keys")
    if len(gkeys) != EXPECTED or len(set(gkeys)) != EXPECTED or set(gkeys) != expected_gkeys:
        errors.append("combined gpt-oss predictions do not match request scientific keys")
    if sum(r["model"] == "qwen" for r in combined) != EXPECTED or sum(r["model"] == "gptoss" for r in combined) != EXPECTED:
        errors.append("combined normalized response file has incorrect model coverage")
    digest = hashlib.sha256()
    with gzip.open(combined_path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != "d269cdfc82a67566ae5b55c5a1d05c76fe0d96dc9360e976cb2252b1f2b94d5e":
        errors.append("combined normalized response content digest differs from the analysis input")

if errors:
    raise SystemExit("Package verification failed:\n- " + "\n- ".join(errors))
print(f"Verified {len(manifest['artifacts'])} artifacts, 256 cases, and 14,336 raw/normalized requests per model.")
