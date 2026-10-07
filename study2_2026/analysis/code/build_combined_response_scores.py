#!/usr/bin/env python3
"""Create normalized per-request model rows from the public response archives."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

from normalize_qwen import classify

QWEN_REQUESTS_SHA = "fe5942b960609864d0973fc8a989ba7346159ed32c1184b26e6785d92776690a"
GPT_OSS_REQUESTS_SHA = "f78c96b12f6fb52aade6f8d52de0c5a4a5a34a5f832be8dbd7b14b99aa6e18f6"
QWEN_NORMALIZED_SHA = "bbfae74804a7ee6cddbfd4c0d3cd167b2ba18d68b1d14703af353a3d6664ed17"
EXPECTED_KEYS = 14336
VALID_STATES = {"valid", "abstain", "invalid", "truncated"}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_gzip_jsonl(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def gzip_payload_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with gzip.open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(qwen_requests: Path, qwen_normalized: Path, qwen_raw: Path,
          gpt_requests: Path, gpt_raw: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    if gzip_payload_sha(qwen_requests) != QWEN_REQUESTS_SHA:
        raise ValueError("Qwen request grid digest differs")
    if gzip_payload_sha(gpt_requests) != GPT_OSS_REQUESTS_SHA:
        raise ValueError("gpt-oss request grid digest differs")
    if gzip_payload_sha(qwen_normalized) != QWEN_NORMALIZED_SHA:
        raise ValueError("Qwen normalized export digest differs")

    qreq = {r["key"]: r for r in read_gzip_jsonl(qwen_requests)}
    qnorm = {r["key"]: r for r in read_gzip_jsonl(qwen_normalized)}
    qraw = {r["key"]: r for r in read_gzip_jsonl(qwen_raw)}
    if len(qreq) != EXPECTED_KEYS or set(qreq) != set(qnorm) or set(qreq) != set(qraw):
        raise ValueError("Qwen requests, normalized rows, and raw responses do not match")
    for key, row in qnorm.items():
        raw = base64.b64decode(qraw[key]["response_raw_base64"], validate=True)
        if sha_bytes(raw) != row["raw_sha256"] or row["raw_sha256"] != qraw[key]["response_sha256"]:
            raise ValueError(f"Qwen response digest mismatch: {key}")
        state, label, _ = classify(raw)
        if state != row["state"] or label != row["predicted_label"]:
            raise ValueError(f"Qwen raw/normalized scoring mismatch: {key}")
        if row["state"] not in VALID_STATES:
            raise ValueError(f"Qwen response state is unknown: {key}")

    greq = {r["key"]: r for r in read_gzip_jsonl(gpt_requests)}
    graw = {r["key"]: r for r in read_gzip_jsonl(gpt_raw)}
    if len(greq) != EXPECTED_KEYS or set(greq) != set(graw):
        raise ValueError("gpt-oss request and raw-response keys do not match")

    with output.open("x", encoding="utf-8") as stream:
        for key in sorted(qnorm):
            row = qnorm[key]
            stream.write(json.dumps({"model": "qwen", "key": key,
                "state": row["state"], "predicted_label": row["predicted_label"],
                "attempts": row["attempts"], "recoverable_transport_attempts": 0},
                sort_keys=True) + "\n")

        gcounts = Counter()
        for request_key in sorted(greq):
            request, row = greq[request_key], graw[request_key]
            scientific_key = request["pair_id"] + "|" + request["arm"]
            if row["scientific_key"] != scientific_key or row["pair_id"] != request["pair_id"]:
                raise ValueError(f"gpt-oss scientific key mismatch: {request_key}")
            raw = base64.b64decode(row["response_raw_base64"], validate=True)
            if sha_bytes(raw) != row["response_sha256"]:
                raise ValueError(f"gpt-oss response digest mismatch: {request_key}")
            if row["state"] != "completed" or row["http_status"] != 200:
                raise ValueError(f"gpt-oss response is not terminal HTTP 200: {request_key}")
            state, label, _ = classify(raw)
            if state not in VALID_STATES:
                raise ValueError(f"gpt-oss normalized state is unknown: {request_key}")
            gcounts[state] += 1
            stream.write(json.dumps({"model": "gptoss", "key": scientific_key,
                "state": state, "predicted_label": label, "attempts": 1,
                "recoverable_transport_attempts": 0}, sort_keys=True) + "\n")

    return {"qwenKeys": len(qnorm), "gptOssKeys": len(greq),
            "qwenNormalizedSha256": QWEN_NORMALIZED_SHA,
            "combinedSha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "gptOssStates": dict(sorted(gcounts.items()))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("qwen_requests", type=Path)
    parser.add_argument("qwen_normalized", type=Path)
    parser.add_argument("qwen_raw_responses", type=Path)
    parser.add_argument("gpt_oss_requests", type=Path)
    parser.add_argument("gpt_oss_raw_responses", type=Path)
    parser.add_argument("combined_output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.qwen_requests, args.qwen_normalized,
        args.qwen_raw_responses, args.gpt_oss_requests,
        args.gpt_oss_raw_responses, args.combined_output), sort_keys=True))


if __name__ == "__main__":
    main()
