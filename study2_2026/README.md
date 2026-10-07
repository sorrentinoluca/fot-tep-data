# Study 2 manuscript package

This directory is reserved for the data package supporting the manuscript version dated
2026-10-07. `MANIFEST.template.json` records the manuscript SHA-256 and the package fields to
complete when the matching source revision and study artifacts are assembled.

No release package is present here yet. The existing `study2_assets/view_data.js` supports the
previously archived 96-run cohort and must not be used as a substitute for the manuscript's
256-run follow-up. Keep those cohorts and their output files separate.

The complete package should include the exact prompts or their byte-for-byte builders, per-call
responses and status records, run-level inputs and truth mapping, deterministic scoring and
analysis code, output tables, and a manifest of hashes and provenance. The release should allow
the scoring and paper tables to be regenerated from archived responses without contacting an
inference service.
