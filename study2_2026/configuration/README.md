# Development configuration and insight materials

This folder publishes the recorded configuration used to define development-time features and insights. It complements the analysis archive; it does not by itself regenerate the simulation or the test predictions.

## Files

- `verbalization_rules.json` gives the four standardized thresholds, their common calibration rule, temporal rules, feature meanings, and English reporting vocabulary. The same threshold applies to each of the 41 measured variables for its statistic. The legacy `faultInjectionHours` field is scoped in that file and is not the current-study onset. The automatic English vocabulary is descriptive, non-exhaustive guidance rather than a binding whitelist. `normalization_reference.json` identifies the shared N1-N5 baseline and its digests; its stream IDs are not included.
- `development_streams.json` lists the 80 development runs, stream identifiers, class labels, raw-source digests, and eight selected five-hour windows per run. The 40 Normal runs also identify their client (five per client). It is an identity/provenance roster; raw simulator trajectories and the simulator configuration needed to regenerate them are not included.
- `fedavg_development_recipe.json` records the logistic-regression FedAvg development reconstruction recipe, its five initialization seeds, and the development-only cross-validation grid, metric, seed, and tie-break rule. It does not include fitted arrays or the separate test signatures needed to regenerate the published test predictions.
- `insights/prose/` contains the eight class-specific natural-language insights.
- `insights/structured/` contains the corresponding eight structured records.
- `insights/AGG_LIBRARY_BLOCK.txt` and `insights/AGG_LIBRARY.json` contain the aggregate insight library exactly as sent in prompts and a structured representation whose entry text matches the archived prompt block.
- `PROVENANCE.json` records source-file digests and the scope of these materials.

The run roster is not the simulation itself. Likewise, the development recipe is not a release of test-time model state. No feature-signature matrix, class-mean vectors, fitted FedAvg weights, or test prediction producer code is included here.
