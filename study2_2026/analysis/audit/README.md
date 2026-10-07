# Independent package audit

This audit recomputes the model-response outcomes and reported contrasts from the archived requests, responses, case manifest and published numerical predictions. It does not contact an inference endpoint or simulator. The raw-response parser and statistical checks are independent of the package analysis implementation; the audit also runs the package's own verifier and recomputation commands for comparison.

## Run

From the repository root, install the pinned dependencies and provide a new or empty output directory outside `study2_2026`:

```sh
python3 -m pip install -r study2_2026/analysis/requirements.txt
mkdir -p /tmp/fot-tep-study2-audit
python3 -c 'import os; assert not os.listdir("/tmp/fot-tep-study2-audit")'
study2_2026/analysis/audit/run_package_audit.sh /tmp/fot-tep-study2-audit
```

To compare a separate manuscript table directory, pass it as the second argument:

```sh
study2_2026/analysis/audit/run_package_audit.sh /tmp/fot-tep-study2-audit /path/to/generated
```

The output directory must be empty. The script does not delete or overwrite files. It writes logs and intermediate normalized data there. Python bytecode writing is disabled for the run.

## Checks

- Package hashes, response joins and raw response digests.
- Rebuilding the combined normalized model rows and both analysis outputs.
- Independent parsing of all 28,672 raw model responses and independent recomputation of primary statistics.
- Duplicate-request outcome agreement, prompt facts, and additional quantitative manuscript claims.
- Numeric cells in the eight LaTeX tables against recomputed results.

The audit can recompute statistical summaries for PROTO and FedAvg from their published predictions. It cannot regenerate those predictions because the feature signatures, class means, fitted weights and producer code are not included. It also cannot regenerate the physical runs or fresh model responses.
