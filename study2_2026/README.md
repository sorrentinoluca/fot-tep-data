# Study 2 reproducibility package

This package supports the 256-run follow-up reported in the manuscript snapshot identified in `MANIFEST.json`. It preserves the earlier 96-run cohort separately in the repository’s existing `study2_assets/` files.

## Contents

- `paper/`: the latest title-only manuscript source snapshot, its nine-page built PDF, a sanitized build record, bibliography, and generated T2 tables.
- `data/`: the 256-case evaluation manifest and sealed numerical reference predictions.
- `requests/`: exact serialized request payloads for the Qwen and gpt-oss configured systems.
- `responses/`: exact raw response bodies for gpt-oss, paired to request keys and carrying per-response SHA-256 digests.
- `analysis/`: reviewed machine-readable analyses, derived tables, usage accounting, and source code for normalization and table generation.
- `MANIFEST.json`: artifact sizes and SHA-256 digests, manuscript identity, and scope limits.

## Verification

From the repository root, run `python3 study2_2026/verify_package.py`. The verifier checks every artifact listed in `MANIFEST.json`, checks request/response row counts, and verifies embedded raw-response digests. It makes no network requests and runs no model inference.

## Reproduction scope

The gpt-oss request and raw-response archive is available for inspection. Exact Qwen request payloads and reviewed aggregate results are included, but the per-request Qwen response archive and normalized per-request outcomes are not part of this public package. A reader therefore cannot independently rebuild Qwen row-level scores from this release alone. The package records this limitation rather than treating aggregate analysis files as raw evidence.

S09, R08, and the manuscript review cycles closed with limitations. See the manuscript and analysis files for scientific limits, adverse findings, and inferential scope.
