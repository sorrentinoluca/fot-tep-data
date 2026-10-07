# R08 exploratory descriptive result tables

All values are fixed-denominator operational correctness or run-paired contrasts from the frozen R07 analysis. Intervals are pointwise descriptive, not confirmatory tests. Configured-model comparisons do not isolate model weights.

## Seven-arm means by domain

| Model | Domain | A0 | B0 | FULL | SELF | AGG | S0 | PL0 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gptoss | Own fault | +66.667 | +39.062 | +61.979 | +79.167 | +64.583 | +44.271 | +74.479 |
| gptoss | Local unseen | +9.598 | +51.414 | +52.083 | +6.027 | +50.595 | +55.134 | +8.929 |
| gptoss | Normal | +76.367 | +90.625 | +81.641 | +76.953 | +80.664 | +68.750 | +74.609 |
| qwen | Own fault | +85.417 | +69.271 | +90.104 | +82.292 | +87.500 | +69.271 | +89.583 |
| qwen | Local unseen | +5.134 | +64.658 | +62.202 | +0.149 | +62.202 | +62.649 | +2.679 |
| qwen | Normal | +78.125 | +72.266 | +70.508 | +72.656 | +64.648 | +69.727 | +74.805 |

## Main descriptive contrasts and fixed partitions

| Partition | Domain | Contrast | gpt-oss estimate (pp) | gpt-oss pointwise 95% | Qwen estimate (pp) | Matched gpt-oss minus Qwen effect (pp) | Matched pointwise 95% |
| --- | --- | --- | ---: | --- | ---: | ---: | --- |
| all_faults | own | FULL-B0 | +22.917 | [+16.667, +29.167] | +20.833 | +2.083 | [-6.250, +10.937] |
| all_faults | own | B0-PROTO | -21.875 | [-28.125, -15.625] | not defined | not defined | not defined |
| all_faults | local_unseen | FULL-B0 | +0.670 | [-1.116, +2.381] | -2.455 | +3.125 | [+0.670, +5.580] |
| all_faults | local_unseen | B0-PROTO | -9.524 | [-13.616, -5.357] | not defined | not defined | not defined |
| excluding_F1_F8 | own | FULL-B0 | +22.917 | [+15.972, +30.556] | +11.806 | +11.111 | [+2.083, +20.833] |
| excluding_F1_F8 | own | B0-PROTO | -18.750 | [-25.694, -11.806] | not defined | not defined | not defined |
| excluding_F1_F8 | local_unseen | FULL-B0 | +0.496 | [-1.190, +1.984] | -1.190 | +1.687 | [-0.298, +3.571] |
| excluding_F1_F8 | local_unseen | B0-PROTO | -13.194 | [-16.766, -9.623] | not defined | not defined | not defined |
| F1_F8 | own | FULL-B0 | +22.917 | [+10.417, +35.417] | +47.917 | -25.000 | [-43.750, -6.250] |
| F1_F8 | own | B0-PROTO | -31.250 | [-43.750, -16.667] | not defined | not defined | not defined |
| F1_F8 | local_unseen | FULL-B0 | +1.190 | [-4.167, +6.548] | -6.250 | +7.440 | [-0.298, +15.476] |
| F1_F8 | local_unseen | B0-PROTO | +1.488 | [-11.012, +14.583] | not defined | not defined | not defined |

B0−PROTO is defined for gpt-oss only in the frozen R07 analysis; Qwen B0−PROTO is reported in S09.

## gpt-oss means by fault and domain

| Fault | Domain | A0 | B0 | FULL | SELF | AGG | S0 | PL0 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F1 | own | +58.333 | +12.500 | +33.333 | +87.500 | +70.833 | +12.500 | +70.833 |
| F1 | local_unseen | +69.048 | +83.929 | +89.881 | +45.833 | +77.381 | +84.524 | +66.071 |
| F2 | own | +83.333 | +87.500 | +95.833 | +100.000 | +100.000 | +87.500 | +79.167 |
| F2 | local_unseen | +5.357 | +92.262 | +94.048 | +0.595 | +89.881 | +94.643 | +1.786 |
| F3 | own | +66.667 | +29.167 | +54.167 | +70.833 | +79.167 | +0.000 | +66.667 |
| F3 | local_unseen | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +12.500 | +0.000 |
| F8 | own | +95.833 | +20.833 | +45.833 | +87.500 | +29.167 | +75.000 | +100.000 |
| F8 | local_unseen | +1.190 | +14.881 | +11.310 | +0.595 | +8.929 | +10.714 | +2.381 |
| F10 | own | +29.167 | +58.333 | +95.833 | +79.167 | +100.000 | +50.000 | +54.167 |
| F10 | local_unseen | +0.000 | +100.000 | +100.000 | +0.595 | +100.000 | +100.000 | +0.000 |
| F13 | own | +66.667 | +37.500 | +41.667 | +66.667 | +20.833 | +50.000 | +83.333 |
| F13 | local_unseen | +1.190 | +33.333 | +38.690 | +0.595 | +43.452 | +42.262 | +0.595 |
| F14 | own | +95.833 | +58.333 | +91.667 | +95.833 | +100.000 | +62.500 | +95.833 |
| F14 | local_unseen | +0.000 | +86.905 | +82.738 | +0.000 | +85.119 | +94.643 | +0.595 |
| F15 | own | +37.500 | +8.333 | +37.500 | +45.833 | +16.667 | +16.667 | +45.833 |
| F15 | local_unseen | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +1.786 | +0.000 |

## gpt-oss response states by arm, all 2,048 planned keys each

| Arm | Planned | Attempted | Valid | Abstain | Invalid | Truncated | Missing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A0 | 2048 | 2048 | 1852 | 196 | 0 | 0 | 0 |
| B0 | 2048 | 2048 | 1673 | 375 | 0 | 0 | 0 |
| FULL | 2048 | 2048 | 1696 | 352 | 0 | 0 | 0 |
| SELF | 2048 | 2048 | 1443 | 605 | 0 | 0 | 0 |
| AGG | 2048 | 2048 | 1631 | 417 | 0 | 0 | 0 |
| S0 | 2048 | 2048 | 1686 | 362 | 0 | 0 | 0 |
| PL0 | 2048 | 2048 | 1927 | 121 | 0 | 0 | 0 |

The complete machine-readable output contains every prespecified contrast, count and collision sensitivity. No arm or fault is selected by result direction.
