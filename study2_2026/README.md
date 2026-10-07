# Study 2 reproducibility package

This package contains the 256-run follow-up, its recorded model requests and responses, offline analysis inputs, and the current author-provided manuscript snapshot. It keeps the earlier 96-run cohort separate.

## Contents

- `paper/`: a build wrapper, exact manuscript source, bibliography, the eight LaTeX tables it includes, the locally compiled ten-page PDF, and a build record. The manuscript source SHA-256 is recorded in `MANIFEST.json`. Comment-only internal notes were removed from the public bibliography; citation entries and fields were retained.
- `data/`: the 256-case evaluation manifest and published numerical reference predictions.
- `requests/`: exact serialized request payloads for the two configured model systems.
- `responses/`: request-linked raw response bodies, normalized Qwen rows, and combined normalized scoring rows. Raw response bytes are base64 encoded and carry SHA-256 digests.
- `analysis/`: pinned outputs, analysis code, exact offline recomputation receipts, and an independent audit for the numerical claims and LaTeX tables.
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

The packaged PDF is a verified ten-page build of the source hash in the manifest. LaTeX embeds build-time metadata, so a later PDF need not be byte-identical even when the source and rendered pages match. The current manuscript file itself does not yet cite or link this data package; add a repository reference to the manuscript before submission.

## Reproduce the analyses and audit paper claims

Instructions for rebuilding normalized responses and model analyses are in [`analysis/README.md`](analysis/README.md). The independent audit, including the added text-only claims and numeric-cell comparisons for all eight LaTeX tables, is in [`analysis/audit/README.md`](analysis/audit/README.md).

The audit recomputes model outcomes from archived raw responses. PROTO and FedAvg statistics can be recalculated from the published predictions, but those predictions cannot be regenerated because feature signatures, class means, fitted weights, and producer code are not included. The audit also confirms that the archived AGG system instruction differs from the other conditions in its `used_insight_ids` wording; the manuscript currently describes the system prompt as shared.

## Scope and limits

The package supports offline scoring and analysis from recorded model responses. It does not reproduce fresh inference or regenerate the 256 physical simulator runs. The earlier 96-run cohort, raw simulation trajectories, and the pipeline that creates verbalized windows and insights are not fully included. No explicit reuse license is assigned to this package; users should obtain permission before reuse beyond applicable legal exceptions.
