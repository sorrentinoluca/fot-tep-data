# Reproducing FoT-TEP results

This repository stores public data packages. The FoT-TEP source repository stores the code and
instructions used to produce analyses. Each data package must point to the exact source revision
and manuscript version it supports.

## Package contents

Use a separate directory or release for each study and cohort. A package should contain:

- `README.md` with the study, cohort, manuscript version, intended analysis, software
  requirements, and reproduction commands.
- `MANIFEST.json` with the source repository and immutable revision, manuscript SHA-256,
  creation date, artifact paths, byte sizes, SHA-256 digests, and provenance for each artifact.
- The public input data and the exact derived files required to regenerate the reported tables
  and figures.
- A dependency lockfile or exact environment description when the analysis requires software
  beyond the standard runtime.

Keep exploratory and confirmatory cohorts distinct, and identify which cohort supports each
reported result. Preserve prior releases when adding a new manuscript or cohort.

## Language-model requests

For every evaluated request, preserve the exact request payload or the immutable components and
builder needed to reconstruct it byte for byte. Record its case key, receiver, condition, model
identifier, generation settings, timestamp, terminal status, and a link to the stored response.
Preserve the first scored response and separately record transport retries, parser outcomes,
abstentions, truncations, and missing responses. Store prompt and response bytes with hashes so a
reader can verify that the release matches the analysis inputs.

Re-running an external or locally served language model may produce different text even when the
same settings are supplied. A data release should therefore let readers reproduce the scoring and
analysis from the archived responses, while clearly describing any limits on regenerating those
responses.

## Reviewer workflow

1. Check each artifact's byte size and SHA-256 against `MANIFEST.json`.
2. Check out the source revision recorded by the package.
3. Follow the package instructions to regenerate the deterministic preprocessing, scoring,
   analysis tables, and figures from the archived inputs and responses.
4. Compare the regenerated outputs with the recorded output hashes and the manuscript tables.

Do not include credentials, private service configuration, or unrelated local files in a public
package. Record unavailable inputs explicitly rather than substituting artifacts from another
cohort or an earlier study.
