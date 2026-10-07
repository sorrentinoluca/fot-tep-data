# Study 2 reproducibility package

This package contains the 256-run follow-up, its recorded model requests and responses, offline analysis inputs, and the current author-provided manuscript snapshot. It keeps the earlier 96-run cohort separate.

## Contents

- `paper/`: a build wrapper, current manuscript source, bibliography, the eight LaTeX tables it includes, a PDF from the prior source revision, and build metadata that records both source hashes. The manuscript source SHA-256 is recorded in `MANIFEST.json`. Comment-only internal notes were removed from the public bibliography; citation entries and fields were retained.
- `data/`: the 256-case evaluation manifest and published numerical reference predictions.
- `requests/`: exact serialized request payloads for the two configured model systems.
- `responses/`: request-linked raw response bodies, normalized Qwen rows, and combined normalized scoring rows. Raw response bytes are base64 encoded and carry SHA-256 digests.
- `analysis/`: pinned outputs, analysis code, exact offline recomputation receipts, and an independent audit for numerical claims, manuscript text claims, and LaTeX tables.
- `configuration/`: the recorded threshold calibration and verbalization rules, development stream identities, the five-seed FedAvg development recipe, and the eight insight libraries in prose and structured form, plus the aggregate library. These are configuration and provenance materials, not the simulation trajectories or test feature signatures.
- `MANIFEST.json`: artifact sizes, hashes, manuscript identity, and reproduction limits.

## Verify the archive

From the repository root:

```sh
python3 study2_2026/verify_package.py
```

The verifier checks manifest hashes, the 256 case and numerical prediction rows, request/response key joins, raw-response digests, and 28,672 normalized model rows. It makes no network requests and performs no model inference.

## Build the paper snapshot

A LaTeX installation with IEEEtran and the packages used by the source is required. From the repository root:

```sh
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error \
  -outdir=/tmp/fot-tep-study2-build study2_2026/paper/main.tex
```

The packaged PDF is a verified ten-page build of the source hash in the manifest. LaTeX embeds build-time metadata, so a later PDF need not be byte-identical even when the source and rendered pages match. The manuscript snapshot links to this repository and study folder. For an immutable citation, record the package commit or release tag used for the submission.

## Reproduce the analyses and audit paper claims

Instructions for rebuilding normalized responses and model analyses are in [`analysis/README.md`](analysis/README.md). The independent audit, including the added text-only claims and numeric-cell comparisons for all eight LaTeX tables, is in [`analysis/audit/README.md`](analysis/audit/README.md).

The audit recomputes model outcomes from archived raw responses and checks 98 numeric prose fragments and 26 boolean conditions against the packaged manuscript. The extended checker is pinned to the manuscript SHA-256. It inventories 438 numeric tokens; 51 tokens in 20 statements remain outside checked fragments and are classified in `analysis/audit/uncovered_numeric_statements.md`. The checker does not verify every manuscript number: some claims rely on source material not distributed here, and literature-derived claims are not re-evaluated. PROTO and FedAvg statistics can be recalculated from the published predictions, but those test predictions cannot be regenerated because test signatures, fitted prototype class means, fitted weights, and prediction producer code are not included. The configuration folder records the five-seed development reconstruction recipe and selection procedure; it does not include fitted arrays or resolve the test-prediction limitation. The eight LaTeX table fragments consumed by the manuscript are included under `paper/manuscript/generated/`. The analysis renderers produce Markdown tables; they do not generate those LaTeX fragments. The manuscript describes a common system-prompt template. The aggregate condition has a small condition-specific wording difference in the `used_insight_ids` instruction, which is recorded in the audit materials.

## Scope and limits

The package supports offline scoring and analysis from recorded model responses. It does not reproduce fresh inference or regenerate the 256 physical simulator runs. The earlier 96-run cohort, raw simulation trajectories, and the pipeline that creates verbalized windows and insights are not fully included. No explicit reuse license is assigned to this package; users should obtain permission before reuse beyond applicable legal exceptions.
