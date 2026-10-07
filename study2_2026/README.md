# Study 2 reproducibility package

This package supports the 256-run follow-up and pins the manuscript snapshot in `MANIFEST.json`. It keeps the earlier 96-run cohort separate from the new follow-up.

## Contents

- `paper/`: the latest title-only manuscript source snapshot, its nine-page PDF, a sanitized build record, bibliography, and generated T2 tables.
- `data/`: the 256-case evaluation manifest and sealed numerical reference predictions.
- `requests/`: exact serialized request payloads for the Qwen and gpt-oss configured systems.
- `responses/`: per-request raw response bodies for both systems, normalized Qwen responses, and the combined normalized scoring rows. Raw response bytes are base64 encoded and linked by stable keys and SHA-256 digests.
- `analysis/`: reviewed analysis outputs, derived tables, usage accounting, source code, and offline reproduction receipts.
- `MANIFEST.json`: artifact sizes, hashes, manuscript identity, and limits.

## Verify the archive

From the repository root, run:

```sh
python3 study2_2026/verify_package.py
```

The verifier checks all manifest hashes, 256 case and numerical rows, request/response key joins for both models, raw response digests, and 28,672 combined normalized model rows. It makes no network requests and runs no model inference.

## Rebuild the offline analysis inputs

The combined per-request scoring file can be rebuilt directly from the archived request and response files:

```sh
python3 study2_2026/analysis/code/build_combined_response_scores.py \
  study2_2026/requests/qwen_requests.jsonl.gz \
  study2_2026/responses/qwen_normalized_responses.jsonl.gz \
  study2_2026/responses/qwen_responses.jsonl.gz \
  study2_2026/requests/gpt_oss_requests.jsonl.gz \
  study2_2026/responses/gpt_oss_responses.jsonl.gz \
  /tmp/study2_normalized_model_outputs.jsonl
```

The output SHA-256 should be `d269cdfc82a67566ae5b55c5a1d05c76fe0d96dc9360e976cb2252b1f2b94d5e`, matching the original analysis input. The code validates key mappings and raw-response hashes while rebuilding the rows.

The analysis scripts use Python, NumPy, and SciPy. The pinned result JSON files and `analysis/REPRODUCTION_CHECKS.json` record the reference outputs and the local offline recomputation. In the tested environment, the joint-model analysis reproduced byte for byte. The Qwen analysis had identical source/input digests and all non-numeric fields; floating-point estimates differed by at most `4.6e-14`, without changing reported rounded results.

## Reproduction scope and limits

The package supports offline scoring and analysis from the recorded model responses. It does not promise bit-identical outputs from fresh model inference, nor does it include the simulator installation and raw trajectories needed to regenerate the 256 physical runs. The manuscript review and both model-analysis reviews closed with limitations; consult the included paper and analysis outputs for adverse findings and inferential scope. The repository does not assign an explicit reuse license to these data.
