#!/usr/bin/env bash
# Re-run package checks and an independent analysis from the archived responses.
# Usage: run_package_audit.sh <empty output directory> [directory with tab_t2_*.tex]
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
STUDY=$(cd -- "$HERE/../.." && pwd)
REPO=$(cd -- "$STUDY/.." && pwd)
OUT=${1:?provide a new or empty output directory outside the package}
TABLES=${2:-$STUDY/paper/manuscript/generated}
OUT=$(python3 - "$OUT" <<'PYRESOLVE'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PYRESOLVE
)
case "$OUT/" in "$STUDY/"*) echo "Output must be outside the package." >&2; exit 2;; esac
if [[ -e "$OUT" ]]; then
  [[ -d "$OUT" ]] || { echo "Output path exists and is not a directory." >&2; exit 2; }
  [[ -z "$(find "$OUT" -mindepth 1 -maxdepth 1 -print -quit)" ]] || { echo "Output directory must be empty." >&2; exit 2; }
else
  mkdir -p "$OUT"
fi
OUT=$(cd -- "$OUT" && pwd)
export PYTHONDONTWRITEBYTECODE=1
{
  echo "package_commit: $(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo unavailable)"
  python3 --version
  python3 -c "import numpy,scipy; print('numpy',numpy.__version__,'scipy',scipy.__version__)"
} | tee "$OUT/00_environment.txt"
P="$STUDY"
python3 "$P/verify_package.py" | tee "$OUT/A1_verify_package.txt"
python3 "$P/analysis/code/build_combined_response_scores.py" "$P/requests/qwen_requests.jsonl.gz" "$P/responses/qwen_normalized_responses.jsonl.gz" "$P/responses/qwen_responses.jsonl.gz" "$P/requests/gpt_oss_requests.jsonl.gz" "$P/responses/gpt_oss_responses.jsonl.gz" "$OUT/normalized_model_outputs.jsonl" | tee "$OUT/A2_rebuild_normalized.txt"
gzip -dc "$P/responses/qwen_normalized_responses.jsonl.gz" > "$OUT/qwen_normalized.jsonl"
python3 "$P/analysis/code/analyze_qwen.py" "$P/data/case_manifest.jsonl" "$OUT/qwen_normalized.jsonl" "$P/data/numerical_predictions.jsonl" "$OUT/qwen_analysis.json"
python3 "$P/analysis/code/analyze_gpt_oss_and_cross_model.py" "$P/data/case_manifest.jsonl" "$OUT/normalized_model_outputs.jsonl" "$P/data/numerical_predictions.jsonl" "$OUT/combined_analysis.json"
python3 "$P/analysis/code/render_qwen_tables.py" "$P/analysis/qwen_t2_analysis.json" "$P/analysis/qwen_supplemental_accounting.json" "$OUT/qwen_tables.md" > /dev/null
python3 "$P/analysis/code/render_gpt_oss_tables.py" "$P/analysis/gpt_oss_and_cross_model_analysis.json" "$OUT/gpt_oss_tables.md" > /dev/null
{
  echo "-- Qwen analysis, regenerated vs pinned:"; python3 "$HERE/compare_json.py" "$OUT/qwen_analysis.json" "$P/analysis/qwen_t2_analysis.json"
  echo "-- joint analysis, regenerated vs pinned:"; cmp "$OUT/combined_analysis.json" "$P/analysis/gpt_oss_and_cross_model_analysis.json" && echo "byte-identical"
  echo "-- gpt_oss_tables.md:"; cmp "$OUT/gpt_oss_tables.md" "$P/analysis/gpt_oss_tables.md" && echo "byte-identical"
  echo "-- qwen_tables.md:"; cmp "$OUT/qwen_tables.md" "$P/analysis/qwen_tables.md" && echo "byte-identical"
} 2>&1 | tee "$OUT/A3_compare_with_pinned.txt"
python3 "$HERE/01_parse_raw_responses.py" "$P" "$OUT/parsed.pkl" | tee "$OUT/B1_parse_raw_responses.txt"
python3 "$HERE/02_recompute_statistics.py" "$OUT/parsed.pkl" | tee "$OUT/B2_statistics.txt"
python3 "$HERE/03_design_and_request_checks.py" "$P" "$OUT/parsed.pkl" | tee "$OUT/B3_design_and_requests.txt"
python3 "$HERE/04_prompt_facts.py" "$P" | tee "$OUT/B4_prompt_facts.txt"
python3 "$HERE/05_resend_agreement.py" "$P" | tee "$OUT/B5_resend_agreement.txt"
python3 "$HERE/06_reproduce_manuscript_claims.py" "$P" "$OUT/parsed.pkl" | tee "$OUT/B6_manuscript_claims.txt"
python3 "$HERE/07_check_latex_tables.py" "$OUT/parsed.pkl" "$TABLES" "$OUT/qwen_analysis.json" "$OUT/combined_analysis.json" | tee "$OUT/B7_latex_tables.txt"
echo "Audit complete. Outputs and intermediate files are in: $OUT"
