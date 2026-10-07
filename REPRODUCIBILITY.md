# Reproducing FoT-TEP results

This repository stores public data packages. Each package pins the exact manuscript snapshot and cohort it supports, and separates archived observations from derived analysis outputs.

## Package contents

A study package should provide the exact paper source and generated tables; public input data; model request payloads and available raw responses; deterministic scoring and analysis code; a manifest with artifact paths, byte sizes, SHA-256 digests, and provenance; and a clear account of unavailable inputs. Keep exploratory and confirmatory cohorts distinct.

## Language-model evidence

Preserve exact request payloads, generation settings, model identifier, per-request key, response status, and raw response bytes when available and suitable for release. If raw outputs are unavailable, state that directly and do not describe aggregate results as row-level reproducible. Fresh model calls can differ even with the same settings, so offline scoring from archived outputs is separate from regenerating model responses.

## Reviewer workflow

1. Run the package verifier and check every artifact digest.
2. Read the package README and scope limitations in its manifest.
3. Rebuild deterministic outputs only from inputs actually included.
4. Compare rebuilt tables with the pinned manuscript fragments.

Do not include credentials, private service configuration, internal coordination records, or unrelated local files. Preserve scientific model identity and material limitations needed to interpret the results.
