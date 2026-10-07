# Offline analysis reproduction

The package contains exact serialized requests and raw responses for both configured models, normalized row-level outputs, analysis code, and an independent audit. The commands below use local files only; they make no model calls or network requests.

## Verify package contents

From the repository root:

```sh
python3 study2_2026/verify_package.py
```

The verifier checks manifest hashes, the 256 cases and numerical prediction rows, request/response joins, raw response digests, and the 28,672 normalized model-response rows.

## Rebuild normalized response rows

```sh
python3 study2_2026/analysis/code/build_combined_response_scores.py \
  study2_2026/requests/qwen_requests.jsonl.gz \
  study2_2026/responses/qwen_normalized_responses.jsonl.gz \
  study2_2026/responses/qwen_responses.jsonl.gz \
  study2_2026/requests/gpt_oss_requests.jsonl.gz \
  study2_2026/responses/gpt_oss_responses.jsonl.gz \
  /tmp/study2_normalized_model_outputs.jsonl
```

The output SHA-256 should be `d269cdfc82a67566ae5b55c5a1d05c76fe0d96dc9360e976cb2252b1f2b94d5e`.

## Recompute analyses

```sh
gzip -dc study2_2026/responses/qwen_normalized_responses.jsonl.gz > /tmp/study2_qwen_normalized.jsonl
python3 study2_2026/analysis/code/analyze_qwen.py \
  study2_2026/data/case_manifest.jsonl /tmp/study2_qwen_normalized.jsonl \
  study2_2026/data/numerical_predictions.jsonl /tmp/study2_qwen_analysis.json
python3 study2_2026/analysis/code/analyze_gpt_oss_and_cross_model.py \
  study2_2026/data/case_manifest.jsonl /tmp/study2_normalized_model_outputs.jsonl \
  study2_2026/data/numerical_predictions.jsonl /tmp/study2_combined_analysis.json
```

The pinned combined analysis reproduces byte for byte. Qwen estimates are numerically equivalent; the largest observed floating-point difference was `4.6e-14`, with all non-numeric fields matching. The pinned JSON files remain the manuscript analysis inputs.

## Reproduce manuscript text claims and verify LaTeX tables

Run the independent audit described in [`audit/README.md`](audit/README.md). It includes the calculations added after the earlier package snapshot: the relaxed 1,200-character parser sensitivity, F3/F15 contribution, own-label assignments, local-unseen error destinations, request-repeat agreement, insight byte sizes and cited-ID traceability. Its final step compares every numeric cell in the eight packaged LaTeX tables with the recomputed results.

The audit writes its logs and intermediate files to a caller-provided empty output directory. It makes no network requests and does not write into the package.
