# Offline analysis reproduction

The package contains the exact per-request inputs and responses used for both model conditions. No network endpoint or simulator is contacted by the following commands.

## Rebuild normalized response rows

From the repository root:

```sh
python3 study2_2026/analysis/code/build_combined_response_scores.py \
  study2_2026/requests/qwen_requests.jsonl.gz \
  study2_2026/responses/qwen_normalized_responses.jsonl.gz \
  study2_2026/responses/qwen_responses.jsonl.gz \
  study2_2026/requests/gpt_oss_requests.jsonl.gz \
  study2_2026/responses/gpt_oss_responses.jsonl.gz \
  /tmp/study2_normalized_model_outputs.jsonl
```

The script joins each response to the corresponding scientific request key, checks the raw response digest, applies the frozen response classifier, and compares the Qwen raw response with its archived normalized prediction. Its output must hash to `d269cdfc82a67566ae5b55c5a1d05c76fe0d96dc9360e976cb2252b1f2b94d5e`.

## Recompute the Qwen analysis

```sh
gzip -dc study2_2026/responses/qwen_normalized_responses.jsonl.gz \
  > /tmp/study2_qwen_normalized.jsonl
python3 study2_2026/analysis/code/analyze_qwen.py \
  study2_2026/data/case_manifest.jsonl \
  /tmp/study2_qwen_normalized.jsonl \
  study2_2026/data/numerical_predictions.jsonl \
  /tmp/study2_qwen_analysis.json
```

## Recompute the combined model analysis

```sh
python3 study2_2026/analysis/code/analyze_gpt_oss_and_cross_model.py \
  study2_2026/data/case_manifest.jsonl \
  /tmp/study2_normalized_model_outputs.jsonl \
  study2_2026/data/numerical_predictions.jsonl \
  /tmp/study2_combined_analysis.json
```

Install the versions in `requirements.txt` if NumPy and SciPy are not available. The pinned combined analysis reproduces byte for byte. Qwen estimates are numerically equivalent to the pinned file; the largest observed difference with the pinned local environment was `4.6e-14`, while every non-numeric field matched. The pinned result files remain the authoritative manuscript inputs.
