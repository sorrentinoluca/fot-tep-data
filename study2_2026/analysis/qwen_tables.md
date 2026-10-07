# S09 Qwen T2 fixed-denominator result tables

All cells are rendered from the pinned analysis output `S09_QWEN_T2_ANALYSIS.json` (analysis code SHA-256 `53bf18a2b90633b194d443c9018e4ae6e16ec3b2463116393d69d3eb610815bd`) and from `S09_SUPPLEMENTAL_ACCOUNTING.json`. Percentages are fixed-denominator operational correctness: invalid, abstained, truncated and missing outputs are scored zero and are listed separately. A missing or rejected response is never described as a wrong diagnosis.

## 1. Per-arm transport, format and correctness by domain (all eight faults)

`correct` is the exact-top-one match count taken from the confusion destinations; `valid fraction` is terminal contract-valid keys over planned keys. Equal-weight fault means are in Table 2, and differ from correct/planned because each fault is weighted equally rather than by key count.

### 1.a Own-fault domain

| Arm | Tier | Planned | Attempted | Transport attempts | Valid | Abstain | Invalid | Truncated | Missing | Uncertain | Correct | Correct/planned % | Valid fraction % | Input tokens | Output tokens | Reasoning tokens | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A0 | 1 | 192 | 192 | 192 | 178 | 10 | 0 | 4 | 0 | 0 | 164 | 85.417 | 92.708 | 159055 | 222924 | 0 (unobserved) | unavailable |
| B0 | 1 | 192 | 192 | 192 | 185 | 6 | 1 | 0 | 0 | 0 | 133 | 69.271 | 96.354 | 542247 | 228415 | 0 (unobserved) | unavailable |
| FULL | 2 | 192 | 192 | 192 | 185 | 5 | 2 | 0 | 0 | 0 | 173 | 90.104 | 96.354 | 596050 | 232678 | 0 (unobserved) | unavailable |
| SELF | 2 | 192 | 192 | 192 | 160 | 32 | 0 | 0 | 0 | 0 | 158 | 82.292 | 83.333 | 215863 | 223471 | 0 (unobserved) | unavailable |
| AGG | 3 | 192 | 192 | 192 | 180 | 12 | 0 | 0 | 0 | 0 | 168 | 87.500 | 93.750 | 708559 | 230338 | 0 (unobserved) | unavailable |
| S0 | 4 | 192 | 192 | 192 | 179 | 13 | 0 | 0 | 0 | 0 | 133 | 69.271 | 93.229 | 620935 | 224841 | 0 (unobserved) | unavailable |
| PL0 | 4 | 192 | 192 | 192 | 179 | 13 | 0 | 0 | 0 | 0 | 172 | 89.583 | 93.229 | 395239 | 218272 | 0 (unobserved) | unavailable |

### 1.b Local-unseen domain

| Arm | Tier | Planned | Attempted | Transport attempts | Valid | Abstain | Invalid | Truncated | Missing | Uncertain | Correct | Correct/planned % | Valid fraction % | Input tokens | Output tokens | Reasoning tokens | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A0 | 1 | 1344 | 1344 | 1344 | 1087 | 214 | 21 | 22 | 0 | 0 | 69 | 5.134 | 80.878 | 1098166 | 1546473 | 0 (unobserved) | unavailable |
| B0 | 1 | 1344 | 1344 | 1344 | 1275 | 66 | 2 | 1 | 0 | 0 | 869 | 64.658 | 94.866 | 3809300 | 1613524 | 0 (unobserved) | unavailable |
| FULL | 2 | 1344 | 1344 | 1344 | 1272 | 67 | 1 | 4 | 0 | 0 | 836 | 62.202 | 94.643 | 4209784 | 1634639 | 0 (unobserved) | unavailable |
| SELF | 2 | 1344 | 1344 | 1344 | 452 | 889 | 2 | 1 | 0 | 0 | 2 | 0.149 | 33.631 | 1509419 | 1574012 | 0 (unobserved) | unavailable |
| AGG | 3 | 1344 | 1344 | 1344 | 1198 | 142 | 2 | 2 | 0 | 0 | 836 | 62.202 | 89.137 | 4952214 | 1620476 | 0 (unobserved) | unavailable |
| S0 | 4 | 1344 | 1344 | 1344 | 1269 | 73 | 2 | 0 | 0 | 0 | 842 | 62.649 | 94.420 | 4340267 | 1571365 | 0 (unobserved) | unavailable |
| PL0 | 4 | 1344 | 1344 | 1344 | 865 | 473 | 5 | 1 | 0 | 0 | 36 | 2.679 | 64.360 | 2756555 | 1536240 | 0 (unobserved) | unavailable |

### 1.c Normal domain

| Arm | Tier | Planned | Attempted | Transport attempts | Valid | Abstain | Invalid | Truncated | Missing | Uncertain | Correct | Correct/planned % | Valid fraction % | Input tokens | Output tokens | Reasoning tokens | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A0 | 1 | 512 | 512 | 512 | 482 | 28 | 0 | 2 | 0 | 0 | 400 | 78.125 | 94.141 | 377856 | 578890 | 0 (unobserved) | unavailable |
| B0 | 1 | 512 | 512 | 512 | 478 | 34 | 0 | 0 | 0 | 0 | 370 | 72.266 | 93.359 | 1407040 | 608516 | 0 (unobserved) | unavailable |
| FULL | 2 | 512 | 512 | 512 | 477 | 33 | 1 | 1 | 0 | 0 | 361 | 70.508 | 93.164 | 1555576 | 623845 | 0 (unobserved) | unavailable |
| SELF | 2 | 512 | 512 | 512 | 409 | 103 | 0 | 0 | 0 | 0 | 372 | 72.656 | 79.883 | 529344 | 595292 | 0 (unobserved) | unavailable |
| AGG | 3 | 512 | 512 | 512 | 463 | 46 | 3 | 0 | 0 | 0 | 331 | 64.648 | 90.430 | 1832660 | 613238 | 0 (unobserved) | unavailable |
| S0 | 4 | 512 | 512 | 512 | 472 | 39 | 1 | 0 | 0 | 0 | 357 | 69.727 | 92.188 | 1606327 | 596705 | 0 (unobserved) | unavailable |
| PL0 | 4 | 512 | 512 | 512 | 467 | 45 | 0 | 0 | 0 | 0 | 383 | 74.805 | 91.211 | 1007680 | 576691 | 0 (unobserved) | unavailable |

Reasoning-token cells are zero only because `completion_tokens_details` is absent from all 14,336 stored responses, so the 1,024-token thinking budget is unobservable from this evidence; they are not measured zeros. Latency is unrecorded in the ledger; see Table 11 for the reservation-to-finish proxy.

## 2. Family A (primary) and Family B (selected confirmatory)

| Family | Prespecified domain and independent unit | Estimate (pp) | Interval | Raw p | Adjusted p | Direction / limit |
|---|---|---:|---|---:|---:|---|
| A: FULL-B0 | Eight equal-weight fault means; 24 own-fault runs each, 192 runs | +20.833 | Welch-Satterthwaite 95%: [+14.875, +26.792], SE 3.002 pp, df 95.72 | 4.649e-10 | N/A (single primary test at alpha 0.05) | Positive; rejects at alpha 0.05; model-conditional, assumes within-fault run independence and approximate t |
| B: F1 B0-PROTO | 24 F1 runs; seven local-unseen receivers averaged per run | +86.310 | N/A (exact sign-flip) | 9.537e-07 | Holm: 1.907e-06 | Positive; rejects at alpha 0.05; sign-flip null requires run-wise sign invariance |
| B: F8 B0-PROTO | 24 F8 runs; seven local-unseen receivers averaged per run | -45.833 | N/A (exact sign-flip) | 0.000945 | Holm: 0.000945 | Negative (adverse for B0); rejects at alpha 0.05; sign-flip null requires run-wise sign invariance |

Per-fault decomposition of the Family A paired difference (own-fault keys, 24 runs each):

| Fault | Mean FULL-B0 (pp) | Runs | Runs with gain | Runs with loss | Runs tied |
|---|---:|---:|---:|---:|---:|
| F1 | +62.500 | 24 | 15 | 0 | 9 |
| F2 | +0.000 | 24 | 0 | 0 | 24 |
| F3 | +45.833 | 24 | 11 | 0 | 13 |
| F8 | +33.333 | 24 | 8 | 0 | 16 |
| F10 | +0.000 | 24 | 0 | 0 | 24 |
| F13 | +0.000 | 24 | 1 | 1 | 22 |
| F14 | +4.167 | 24 | 1 | 0 | 23 |
| F15 | +20.833 | 24 | 9 | 4 | 11 |

## 3. Prespecified descriptive sensitivity over the three fixed partitions

| Partition | FULL-B0 own-fault (pp) | 20,000-resample pointwise 95% | B0-PROTO local-unseen (pp) | 20,000-resample pointwise 95% | Runs |
|---|---:|---|---:|---|---:|
| all_faults | +20.833 | [+15.104, +26.562] | +3.720 | [+0.074, +7.366] | 192 |
| excluding_F1_F8 | +11.806 | [+5.556, +18.056] | -1.786 | [-4.365, +0.397] | 144 |
| F1_F8 | +47.917 | [+33.333, +60.417] | +20.238 | [+8.333, +33.036] | 48 |

Resampling: 20000 within-fault run resamples with replacement, PCG64 seed 20261006, included classes enumerated in the fixed order. These intervals are pointwise, unadjusted and descriptive; they are outside the Family B Holm family and a pointwise interval excluding zero is not an additional rejection.

## 4. All prespecified secondary arm means, by partition and domain (%)

| Partition | Domain | A0 | B0 | FULL | SELF | AGG | S0 | PL0 | PROTO | FedAvg | Runs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all_faults | own | 85.417 | 69.271 | 90.104 | 82.292 | 87.500 | 69.271 | 89.583 | 60.938 | 72.917 | 192 |
| all_faults | local_unseen | 5.134 | 64.658 | 62.202 | 0.149 | 62.202 | 62.649 | 2.679 | 60.938 | 72.917 | 192 |
| excluding_F1_F8 | own | 83.333 | 77.083 | 88.889 | 76.389 | 86.806 | 68.750 | 86.111 | 65.278 | 66.667 | 144 |
| excluding_F1_F8 | local_unseen | 1.687 | 63.492 | 62.302 | 0.099 | 61.806 | 63.790 | 1.190 | 65.278 | 66.667 | 144 |
| F1_F8 | own | 91.667 | 45.833 | 93.750 | 100.000 | 89.583 | 70.833 | 100.000 | 47.917 | 91.667 | 48 |
| F1_F8 | local_unseen | 15.476 | 68.155 | 61.905 | 0.298 | 63.393 | 59.226 | 7.143 | 47.917 | 91.667 | 48 |
| F1 | own | 91.667 | 33.333 | 95.833 | 100.000 | 100.000 | 70.833 | 100.000 | 12.500 | 100.000 | 24 |
| F1 | local_unseen | 30.952 | 98.810 | 97.619 | 0.595 | 95.238 | 96.429 | 14.286 | 12.500 | 100.000 | 24 |
| F2 | own | 95.833 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 24 |
| F2 | local_unseen | 0.000 | 100.000 | 100.000 | 0.000 | 99.405 | 100.000 | 0.000 | 100.000 | 100.000 | 24 |
| F3 | own | 75.000 | 33.333 | 79.167 | 45.833 | 83.333 | 29.167 | 70.833 | 4.167 | 0.000 | 24 |
| F3 | local_unseen | 0.000 | 1.786 | 1.786 | 0.000 | 6.548 | 4.762 | 0.000 | 4.167 | 0.000 | 24 |
| F8 | own | 91.667 | 58.333 | 91.667 | 100.000 | 79.167 | 70.833 | 100.000 | 83.333 | 83.333 | 24 |
| F8 | local_unseen | 0.000 | 37.500 | 26.190 | 0.000 | 31.548 | 22.024 | 0.000 | 83.333 | 83.333 | 24 |
| F10 | own | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 24 |
| F10 | local_unseen | 8.333 | 100.000 | 100.000 | 0.595 | 100.000 | 100.000 | 4.762 | 100.000 | 100.000 | 24 |
| F13 | own | 95.833 | 75.000 | 75.000 | 91.667 | 75.000 | 75.000 | 100.000 | 87.500 | 100.000 | 24 |
| F13 | local_unseen | 0.000 | 72.619 | 72.024 | 0.000 | 64.881 | 72.024 | 0.595 | 87.500 | 100.000 | 24 |
| F14 | own | 100.000 | 95.833 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 100.000 | 24 |
| F14 | local_unseen | 1.190 | 100.000 | 99.405 | 0.000 | 100.000 | 100.000 | 1.786 | 100.000 | 100.000 | 24 |
| F15 | own | 33.333 | 58.333 | 79.167 | 20.833 | 62.500 | 8.333 | 45.833 | 0.000 | 0.000 | 24 |
| F15 | local_unseen | 0.595 | 6.548 | 0.595 | 0.000 | 0.000 | 5.952 | 0.000 | 0.000 | 0.000 | 24 |
| Normal | Normal | 78.125 | 72.266 | 70.508 | 72.656 | 64.648 | 69.727 | 74.805 | 96.875 | 100.000 | 64 |

PROTO and FedAvg columns are reconstructed exactly as `mean_B0 - (B0-PROTO)` and `mean_B0 - (B0-FedAvg)` from the pinned output. Their per-run label is receiver-invariant and copied across receiver keys; copies are not independent decisions.

## 5. All prespecified secondary contrasts with descriptive summaries and gain/loss

| Partition | Domain | Contrast | Estimate (pp) | Descriptive stratified-t 95% | Runs | Run gain | Run loss | Run tie | Pair gain | Pair loss | Pair tie |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| all_faults | own | B0-A0 | -16.146 | [-22.046, -10.246] | 192 | 9 | 40 | 143 | 9 | 40 | 143 |
| all_faults | own | SELF-A0 | -3.125 | [-7.985, +1.735] | 192 | 9 | 15 | 168 | 9 | 15 | 168 |
| all_faults | own | FULL-SELF | +7.813 | [+2.699, +12.926] | 192 | 25 | 10 | 157 | 25 | 10 | 157 |
| all_faults | own | interaction | +23.958 | [+16.419, +31.498] | 192 | 55 | 12 | 125 | - | - | - |
| all_faults | own | AGG-FULL | -2.604 | [-5.948, +0.740] | 192 | 3 | 8 | 181 | 3 | 8 | 181 |
| all_faults | own | S0-B0 | +0.000 | [-5.604, +5.604] | 192 | 19 | 19 | 154 | 19 | 19 | 154 |
| all_faults | own | PL0-B0 | +20.313 | [+14.651, +25.974] | 192 | 44 | 5 | 143 | 44 | 5 | 143 |
| all_faults | own | FULL-B0 | +20.833 | [+14.875, +26.792] | 192 | 45 | 5 | 142 | - | - | - |
| all_faults | own | B0-PROTO | +8.333 | [+2.672, +13.994] | 192 | 29 | 13 | 150 | 29 | 13 | 150 |
| all_faults | own | B0-FedAvg | -3.646 | [-9.462, +2.170] | 192 | 24 | 31 | 137 | 24 | 31 | 137 |
| all_faults | local_unseen | B0-A0 | +59.524 | [+56.702, +62.346] | 192 | 148 | 1 | 43 | 802 | 2 | 540 |
| all_faults | local_unseen | SELF-A0 | -4.985 | [-5.893, -4.077] | 192 | 1 | 39 | 152 | 2 | 69 | 1273 |
| all_faults | local_unseen | FULL-SELF | +62.054 | [+59.507, +64.600] | 192 | 134 | 0 | 58 | 834 | 0 | 510 |
| all_faults | local_unseen | interaction | +2.530 | [+0.671, +4.388] | 192 | 48 | 32 | 112 | - | - | - |
| all_faults | local_unseen | AGG-FULL | +0.000 | [-1.773, +1.773] | 192 | 22 | 18 | 152 | 49 | 49 | 1246 |
| all_faults | local_unseen | S0-B0 | -2.009 | [-3.951, -0.067] | 192 | 20 | 28 | 144 | 35 | 62 | 1247 |
| all_faults | local_unseen | PL0-B0 | -61.979 | [-64.811, -59.147] | 192 | 0 | 148 | 44 | 0 | 833 | 511 |
| all_faults | local_unseen | B0-PROTO | +3.720 | [-0.037, +7.477] | 192 | 39 | 29 | 124 | 173 | 123 | 1048 |
| all_faults | local_unseen | B0-FedAvg | -8.259 | [-11.994, -4.524] | 192 | 18 | 33 | 141 | 33 | 144 | 1167 |
| excluding_F1_F8 | own | B0-A0 | -6.250 | [-11.929, -0.571] | 144 | 7 | 16 | 121 | 7 | 16 | 121 |
| excluding_F1_F8 | own | SELF-A0 | -6.944 | [-12.864, -1.024] | 144 | 5 | 15 | 124 | 5 | 15 | 124 |
| excluding_F1_F8 | own | FULL-SELF | +12.500 | [+6.077, +18.923] | 144 | 25 | 7 | 112 | 25 | 7 | 112 |
| excluding_F1_F8 | own | interaction | +18.750 | [+10.655, +26.845] | 144 | 32 | 8 | 104 | - | - | - |
| excluding_F1_F8 | own | AGG-FULL | -2.083 | [-5.712, +1.546] | 144 | 2 | 5 | 137 | 2 | 5 | 137 |
| excluding_F1_F8 | own | S0-B0 | -8.333 | [-13.643, -3.024] | 144 | 4 | 16 | 124 | 4 | 16 | 124 |
| excluding_F1_F8 | own | PL0-B0 | +9.028 | [+3.076, +14.979] | 144 | 18 | 5 | 121 | 18 | 5 | 121 |
| excluding_F1_F8 | own | FULL-B0 | +11.806 | [+5.309, +18.302] | 144 | 22 | 5 | 117 | - | - | - |
| excluding_F1_F8 | own | B0-PROTO | +11.806 | [+6.443, +17.168] | 144 | 21 | 4 | 119 | 21 | 4 | 119 |
| excluding_F1_F8 | own | B0-FedAvg | +10.417 | [+4.656, +16.177] | 144 | 22 | 7 | 115 | 22 | 7 | 115 |
| excluding_F1_F8 | local_unseen | B0-A0 | +61.806 | [+58.889, +64.722] | 144 | 106 | 1 | 37 | 624 | 1 | 383 |
| excluding_F1_F8 | local_unseen | SELF-A0 | -1.587 | [-2.378, -0.796] | 144 | 1 | 15 | 128 | 1 | 17 | 990 |
| excluding_F1_F8 | local_unseen | FULL-SELF | +62.202 | [+59.475, +64.930] | 144 | 96 | 0 | 48 | 627 | 0 | 381 |
| excluding_F1_F8 | local_unseen | interaction | +0.397 | [-0.933, +1.727] | 144 | 21 | 18 | 105 | - | - | - |
| excluding_F1_F8 | local_unseen | AGG-FULL | -0.496 | [-1.947, +0.955] | 144 | 12 | 11 | 121 | 21 | 26 | 961 |
| excluding_F1_F8 | local_unseen | S0-B0 | +0.298 | [-0.846, +1.441] | 144 | 16 | 11 | 117 | 17 | 14 | 977 |
| excluding_F1_F8 | local_unseen | PL0-B0 | -62.302 | [-65.161, -59.442] | 144 | 0 | 106 | 38 | 0 | 628 | 380 |
| excluding_F1_F8 | local_unseen | B0-PROTO | -1.786 | [-4.269, +0.698] | 144 | 14 | 9 | 121 | 14 | 32 | 962 |
| excluding_F1_F8 | local_unseen | B0-FedAvg | -3.175 | [-6.007, -0.342] | 144 | 14 | 11 | 119 | 14 | 46 | 948 |
| F1_F8 | own | B0-A0 | -45.833 | [-62.517, -29.150] | 48 | 2 | 24 | 22 | 2 | 24 | 22 |
| F1_F8 | own | SELF-A0 | +8.333 | [+0.131, +16.536] | 48 | 4 | 0 | 44 | 4 | 0 | 44 |
| F1_F8 | own | FULL-SELF | -6.250 | [-13.426, +0.926] | 48 | 0 | 3 | 45 | 0 | 3 | 45 |
| F1_F8 | own | interaction | +39.583 | [+21.176, +57.991] | 48 | 23 | 4 | 21 | - | - | - |
| F1_F8 | own | AGG-FULL | -4.167 | [-12.323, +3.990] | 48 | 1 | 3 | 44 | 1 | 3 | 44 |
| F1_F8 | own | S0-B0 | +25.000 | [+8.827, +41.173] | 48 | 15 | 3 | 30 | 15 | 3 | 30 |
| F1_F8 | own | PL0-B0 | +54.167 | [+39.851, +68.482] | 48 | 26 | 0 | 22 | 26 | 0 | 22 |
| F1_F8 | own | FULL-B0 | +47.917 | [+33.736, +62.098] | 48 | 23 | 0 | 25 | - | - | - |
| F1_F8 | own | B0-PROTO | -2.083 | [-18.376, +14.210] | 48 | 8 | 9 | 31 | 8 | 9 | 31 |
| F1_F8 | own | B0-FedAvg | -45.833 | [-61.788, -29.878] | 48 | 2 | 24 | 22 | 2 | 24 | 22 |
| F1_F8 | local_unseen | B0-A0 | +52.679 | [+45.184, +60.173] | 48 | 42 | 0 | 6 | 178 | 1 | 157 |
| F1_F8 | local_unseen | SELF-A0 | -15.179 | [-18.035, -12.322] | 48 | 0 | 24 | 24 | 1 | 52 | 283 |
| F1_F8 | local_unseen | FULL-SELF | +61.607 | [+55.153, +68.061] | 48 | 38 | 0 | 10 | 207 | 0 | 129 |
| F1_F8 | local_unseen | interaction | +8.929 | [+2.570, +15.287] | 48 | 27 | 14 | 7 | - | - | - |
| F1_F8 | local_unseen | AGG-FULL | +1.488 | [-4.240, +7.216] | 48 | 10 | 7 | 31 | 28 | 23 | 285 |
| F1_F8 | local_unseen | S0-B0 | -8.929 | [-16.001, -1.856] | 48 | 4 | 17 | 27 | 18 | 48 | 270 |
| F1_F8 | local_unseen | PL0-B0 | -61.012 | [-68.759, -53.265] | 48 | 0 | 42 | 6 | 0 | 205 | 131 |
| F1_F8 | local_unseen | B0-PROTO | +20.238 | [+6.999, +33.478] | 48 | 25 | 20 | 3 | 159 | 91 | 86 |
| F1_F8 | local_unseen | B0-FedAvg | -23.512 | [-36.206, -10.818] | 48 | 4 | 22 | 22 | 19 | 98 | 219 |
| F1 | own | B0-A0 | -58.333 | [-82.976, -33.690] | 24 | 1 | 15 | 8 | 1 | 15 | 8 |
| F1 | own | SELF-A0 | +8.333 | [-3.588, +20.255] | 24 | 2 | 0 | 22 | 2 | 0 | 22 |
| F1 | own | FULL-SELF | -4.167 | [-12.786, +4.453] | 24 | 0 | 1 | 23 | 0 | 1 | 23 |
| F1 | own | interaction | +54.167 | [+26.382, +81.952] | 24 | 15 | 2 | 7 | - | - | - |
| F1 | own | AGG-FULL | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F1 | own | S0-B0 | +37.500 | [+13.187, +61.813] | 24 | 10 | 1 | 13 | 10 | 1 | 13 |
| F1 | own | PL0-B0 | +66.667 | [+46.333, +87.000] | 24 | 16 | 0 | 8 | 16 | 0 | 8 |
| F1 | own | B0-PROTO | +20.833 | [-4.005, +45.672] | 24 | 7 | 2 | 15 | 7 | 2 | 15 |
| F1 | own | B0-FedAvg | -66.667 | [-87.000, -46.333] | 24 | 0 | 16 | 8 | 0 | 16 | 8 |
| F1 | local_unseen | B0-A0 | +67.857 | [+61.891, +73.824] | 24 | 24 | 0 | 0 | 115 | 1 | 52 |
| F1 | local_unseen | SELF-A0 | -30.357 | [-36.070, -24.645] | 24 | 0 | 24 | 0 | 1 | 52 | 115 |
| F1 | local_unseen | FULL-SELF | +97.024 | [+93.055, +100.993] | 24 | 24 | 0 | 0 | 163 | 0 | 5 |
| F1 | local_unseen | interaction | +29.167 | [+22.168, +36.165] | 24 | 23 | 1 | 0 | - | - | - |
| F1 | local_unseen | AGG-FULL | -2.381 | [-8.957, +4.195] | 24 | 1 | 4 | 19 | 3 | 7 | 158 |
| F1 | local_unseen | S0-B0 | -2.381 | [-4.677, -0.084] | 24 | 0 | 4 | 20 | 1 | 5 | 162 |
| F1 | local_unseen | PL0-B0 | -84.524 | [-91.840, -77.207] | 24 | 0 | 24 | 0 | 0 | 142 | 26 |
| F1 | local_unseen | B0-PROTO | +86.310 | [+72.137, +100.482] | 24 | 21 | 0 | 3 | 145 | 0 | 23 |
| F1 | local_unseen | B0-FedAvg | -1.190 | [-2.894, +0.513] | 24 | 0 | 2 | 22 | 0 | 2 | 166 |
| F2 | own | B0-A0 | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F2 | own | SELF-A0 | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F2 | own | FULL-SELF | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | own | interaction | -4.167 | [-12.786, +4.453] | 24 | 0 | 1 | 23 | - | - | - |
| F2 | own | AGG-FULL | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | own | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | own | PL0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | own | B0-PROTO | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | own | B0-FedAvg | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F2 | local_unseen | B0-A0 | +100.000 | n/a | 24 | 24 | 0 | 0 | 168 | 0 | 0 |
| F2 | local_unseen | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F2 | local_unseen | FULL-SELF | +100.000 | n/a | 24 | 24 | 0 | 0 | 168 | 0 | 0 |
| F2 | local_unseen | interaction | +0.000 | n/a | 24 | 0 | 0 | 24 | - | - | - |
| F2 | local_unseen | AGG-FULL | -0.595 | [-1.827, +0.636] | 24 | 0 | 1 | 23 | 0 | 1 | 167 |
| F2 | local_unseen | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F2 | local_unseen | PL0-B0 | -100.000 | n/a | 24 | 0 | 24 | 0 | 0 | 168 | 0 |
| F2 | local_unseen | B0-PROTO | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F2 | local_unseen | B0-FedAvg | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F3 | own | B0-A0 | -41.667 | [-62.932, -20.401] | 24 | 0 | 10 | 14 | 0 | 10 | 14 |
| F3 | own | SELF-A0 | -29.167 | [-52.393, -5.941] | 24 | 1 | 8 | 15 | 1 | 8 | 15 |
| F3 | own | FULL-SELF | +33.333 | [+6.434, +60.232] | 24 | 10 | 2 | 12 | 10 | 2 | 12 |
| F3 | own | interaction | +75.000 | [+43.870, +106.130] | 24 | 16 | 1 | 7 | - | - | - |
| F3 | own | AGG-FULL | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F3 | own | S0-B0 | -4.167 | [-27.393, +19.059] | 24 | 3 | 4 | 17 | 3 | 4 | 17 |
| F3 | own | PL0-B0 | +37.500 | [+13.187, +61.813] | 24 | 10 | 1 | 13 | 10 | 1 | 13 |
| F3 | own | B0-PROTO | +29.167 | [+9.561, +48.773] | 24 | 7 | 0 | 17 | 7 | 0 | 17 |
| F3 | own | B0-FedAvg | +33.333 | [+13.000, +53.667] | 24 | 8 | 0 | 16 | 8 | 0 | 16 |
| F3 | local_unseen | B0-A0 | +1.786 | [-0.252, +3.824] | 24 | 3 | 0 | 21 | 3 | 0 | 165 |
| F3 | local_unseen | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F3 | local_unseen | FULL-SELF | +1.786 | [-0.252, +3.824] | 24 | 3 | 0 | 21 | 3 | 0 | 165 |
| F3 | local_unseen | interaction | +0.000 | [-1.779, +1.779] | 24 | 1 | 1 | 22 | - | - | - |
| F3 | local_unseen | AGG-FULL | +4.762 | [+0.527, +8.996] | 24 | 9 | 2 | 13 | 11 | 3 | 154 |
| F3 | local_unseen | S0-B0 | +2.976 | [-0.572, +6.525] | 24 | 7 | 2 | 15 | 7 | 2 | 159 |
| F3 | local_unseen | PL0-B0 | -1.786 | [-3.824, +0.252] | 24 | 0 | 3 | 21 | 0 | 3 | 165 |
| F3 | local_unseen | B0-PROTO | -2.381 | [-11.393, +6.631] | 24 | 3 | 1 | 20 | 3 | 7 | 158 |
| F3 | local_unseen | B0-FedAvg | +1.786 | [-0.252, +3.824] | 24 | 3 | 0 | 21 | 3 | 0 | 165 |
| F8 | own | B0-A0 | -33.333 | [-57.177, -9.490] | 24 | 1 | 9 | 14 | 1 | 9 | 14 |
| F8 | own | SELF-A0 | +8.333 | [-3.588, +20.255] | 24 | 2 | 0 | 22 | 2 | 0 | 22 |
| F8 | own | FULL-SELF | -8.333 | [-20.255, +3.588] | 24 | 0 | 2 | 22 | 0 | 2 | 22 |
| F8 | own | interaction | +25.000 | [-0.670, +50.670] | 24 | 8 | 2 | 14 | - | - | - |
| F8 | own | AGG-FULL | -12.500 | [-26.765, +1.765] | 24 | 0 | 3 | 21 | 0 | 3 | 21 |
| F8 | own | S0-B0 | +12.500 | [-10.163, +35.163] | 24 | 5 | 2 | 17 | 5 | 2 | 17 |
| F8 | own | PL0-B0 | +41.667 | [+20.401, +62.932] | 24 | 10 | 0 | 14 | 10 | 0 | 14 |
| F8 | own | B0-PROTO | -25.000 | [-47.448, -2.552] | 24 | 1 | 7 | 16 | 1 | 7 | 16 |
| F8 | own | B0-FedAvg | -25.000 | [-50.670, +0.670] | 24 | 2 | 8 | 14 | 2 | 8 | 14 |
| F8 | local_unseen | B0-A0 | +37.500 | [+23.515, +51.485] | 24 | 18 | 0 | 6 | 63 | 0 | 105 |
| F8 | local_unseen | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F8 | local_unseen | FULL-SELF | +26.190 | [+13.781, +38.600] | 24 | 14 | 0 | 10 | 44 | 0 | 124 |
| F8 | local_unseen | interaction | -11.310 | [-22.272, -0.347] | 24 | 4 | 13 | 7 | - | - | - |
| F8 | local_unseen | AGG-FULL | +5.357 | [-4.355, +15.070] | 24 | 9 | 3 | 12 | 25 | 16 | 127 |
| F8 | local_unseen | S0-B0 | -15.476 | [-29.473, -1.479] | 24 | 4 | 13 | 7 | 17 | 43 | 108 |
| F8 | local_unseen | PL0-B0 | -37.500 | [-51.485, -23.515] | 24 | 0 | 18 | 6 | 0 | 63 | 105 |
| F8 | local_unseen | B0-PROTO | -45.833 | [-68.888, -22.778] | 24 | 4 | 20 | 0 | 14 | 91 | 63 |
| F8 | local_unseen | B0-FedAvg | -45.833 | [-71.177, -20.490] | 24 | 4 | 20 | 0 | 19 | 96 | 53 |
| F10 | own | B0-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | FULL-SELF | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | interaction | +0.000 | n/a | 24 | 0 | 0 | 24 | - | - | - |
| F10 | own | AGG-FULL | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | PL0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | B0-PROTO | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | own | B0-FedAvg | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F10 | local_unseen | B0-A0 | +91.667 | [+87.722, +95.611] | 24 | 24 | 0 | 0 | 154 | 0 | 14 |
| F10 | local_unseen | SELF-A0 | -7.738 | [-12.088, -3.388] | 24 | 1 | 12 | 11 | 1 | 14 | 153 |
| F10 | local_unseen | FULL-SELF | +99.405 | [+98.173, +100.636] | 24 | 24 | 0 | 0 | 167 | 0 | 1 |
| F10 | local_unseen | interaction | +7.738 | [+3.388, +12.088] | 24 | 12 | 1 | 11 | - | - | - |
| F10 | local_unseen | AGG-FULL | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F10 | local_unseen | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F10 | local_unseen | PL0-B0 | -95.238 | [-98.143, -92.333] | 24 | 0 | 24 | 0 | 0 | 160 | 8 |
| F10 | local_unseen | B0-PROTO | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F10 | local_unseen | B0-FedAvg | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F13 | own | B0-A0 | -20.833 | [-38.351, -3.316] | 24 | 0 | 5 | 19 | 0 | 5 | 19 |
| F13 | own | SELF-A0 | -4.167 | [-19.311, +10.977] | 24 | 1 | 2 | 21 | 1 | 2 | 21 |
| F13 | own | FULL-SELF | -16.667 | [-32.742, -0.591] | 24 | 0 | 4 | 20 | 0 | 4 | 20 |
| F13 | own | interaction | +4.167 | [-15.439, +23.773] | 24 | 3 | 2 | 19 | - | - | - |
| F13 | own | AGG-FULL | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F13 | own | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F13 | own | PL0-B0 | +25.000 | [+6.322, +43.678] | 24 | 6 | 0 | 18 | 6 | 0 | 18 |
| F13 | own | B0-PROTO | -12.500 | [-26.765, +1.765] | 24 | 0 | 3 | 21 | 0 | 3 | 21 |
| F13 | own | B0-FedAvg | -25.000 | [-43.678, -6.322] | 24 | 0 | 6 | 18 | 0 | 6 | 18 |
| F13 | local_unseen | B0-A0 | +72.619 | [+55.940, +89.298] | 24 | 20 | 0 | 4 | 122 | 0 | 46 |
| F13 | local_unseen | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F13 | local_unseen | FULL-SELF | +72.024 | [+55.869, +88.179] | 24 | 20 | 0 | 4 | 121 | 0 | 47 |
| F13 | local_unseen | interaction | -0.595 | [-5.775, +4.585] | 24 | 4 | 4 | 16 | - | - | - |
| F13 | local_unseen | AGG-FULL | -7.143 | [-14.690, +0.404] | 24 | 2 | 7 | 15 | 9 | 21 | 138 |
| F13 | local_unseen | S0-B0 | -0.595 | [-5.460, +4.270] | 24 | 5 | 4 | 15 | 6 | 7 | 155 |
| F13 | local_unseen | PL0-B0 | -72.024 | [-88.566, -55.482] | 24 | 0 | 20 | 4 | 0 | 121 | 47 |
| F13 | local_unseen | B0-PROTO | -14.881 | [-26.877, -2.885] | 24 | 0 | 8 | 16 | 0 | 25 | 143 |
| F13 | local_unseen | B0-FedAvg | -27.381 | [-44.060, -10.702] | 24 | 0 | 11 | 13 | 0 | 46 | 122 |
| F14 | own | B0-A0 | -4.167 | [-12.786, +4.453] | 24 | 0 | 1 | 23 | 0 | 1 | 23 |
| F14 | own | SELF-A0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F14 | own | FULL-SELF | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F14 | own | interaction | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | - | - | - |
| F14 | own | AGG-FULL | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 24 |
| F14 | own | S0-B0 | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F14 | own | PL0-B0 | +4.167 | [-4.453, +12.786] | 24 | 1 | 0 | 23 | 1 | 0 | 23 |
| F14 | own | B0-PROTO | -4.167 | [-12.786, +4.453] | 24 | 0 | 1 | 23 | 0 | 1 | 23 |
| F14 | own | B0-FedAvg | -4.167 | [-12.786, +4.453] | 24 | 0 | 1 | 23 | 0 | 1 | 23 |
| F14 | local_unseen | B0-A0 | +98.810 | [+97.106, +100.513] | 24 | 24 | 0 | 0 | 166 | 0 | 2 |
| F14 | local_unseen | SELF-A0 | -1.190 | [-2.894, +0.513] | 24 | 0 | 2 | 22 | 0 | 2 | 166 |
| F14 | local_unseen | FULL-SELF | +99.405 | [+98.173, +100.636] | 24 | 24 | 0 | 0 | 167 | 0 | 1 |
| F14 | local_unseen | interaction | +0.595 | [-1.568, +2.759] | 24 | 2 | 1 | 21 | - | - | - |
| F14 | local_unseen | AGG-FULL | +0.595 | [-0.636, +1.827] | 24 | 1 | 0 | 23 | 1 | 0 | 167 |
| F14 | local_unseen | S0-B0 | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F14 | local_unseen | PL0-B0 | -98.214 | [-100.252, -96.176] | 24 | 0 | 24 | 0 | 0 | 165 | 3 |
| F14 | local_unseen | B0-PROTO | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F14 | local_unseen | B0-FedAvg | +0.000 | n/a | 24 | 0 | 0 | 24 | 0 | 0 | 168 |
| F15 | own | B0-A0 | +25.000 | [+6.322, +43.678] | 24 | 6 | 0 | 18 | 6 | 0 | 18 |
| F15 | own | SELF-A0 | -12.500 | [-35.163, +10.163] | 24 | 2 | 5 | 17 | 2 | 5 | 17 |
| F15 | own | FULL-SELF | +58.333 | [+33.690, +82.976] | 24 | 15 | 1 | 8 | 15 | 1 | 8 |
| F15 | own | interaction | +33.333 | [+1.183, +65.484] | 24 | 12 | 4 | 8 | - | - | - |
| F15 | own | AGG-FULL | -16.667 | [-37.000, +3.667] | 24 | 1 | 5 | 18 | 1 | 5 | 18 |
| F15 | own | S0-B0 | -50.000 | [-71.567, -28.433] | 24 | 0 | 12 | 12 | 0 | 12 | 12 |
| F15 | own | PL0-B0 | -12.500 | [-31.435, +6.435] | 24 | 1 | 4 | 19 | 1 | 4 | 19 |
| F15 | own | B0-PROTO | +58.333 | [+37.068, +79.599] | 24 | 14 | 0 | 10 | 14 | 0 | 10 |
| F15 | own | B0-FedAvg | +58.333 | [+37.068, +79.599] | 24 | 14 | 0 | 10 | 14 | 0 | 10 |
| F15 | local_unseen | B0-A0 | +5.952 | [+2.432, +9.473] | 24 | 11 | 1 | 12 | 11 | 1 | 156 |
| F15 | local_unseen | SELF-A0 | -0.595 | [-1.827, +0.636] | 24 | 0 | 1 | 23 | 0 | 1 | 167 |
| F15 | local_unseen | FULL-SELF | +0.595 | [-0.636, +1.827] | 24 | 1 | 0 | 23 | 1 | 0 | 167 |
| F15 | local_unseen | interaction | -5.357 | [-9.259, -1.455] | 24 | 2 | 11 | 11 | - | - | - |
| F15 | local_unseen | AGG-FULL | -0.595 | [-1.827, +0.636] | 24 | 0 | 1 | 23 | 0 | 1 | 167 |
| F15 | local_unseen | S0-B0 | -0.595 | [-4.360, +3.169] | 24 | 4 | 5 | 15 | 4 | 5 | 159 |
| F15 | local_unseen | PL0-B0 | -6.548 | [-9.618, -3.477] | 24 | 0 | 11 | 13 | 0 | 11 | 157 |
| F15 | local_unseen | B0-PROTO | +6.548 | [+3.477, +9.618] | 24 | 11 | 0 | 13 | 11 | 0 | 157 |
| F15 | local_unseen | B0-FedAvg | +6.548 | [+3.477, +9.618] | 24 | 11 | 0 | 13 | 11 | 0 | 157 |
| Normal | Normal | B0-A0 | -5.859 | not prespecified | 64 | 3 | 25 | 36 | 4 | 34 | 474 |
| Normal | Normal | SELF-A0 | -5.469 | not prespecified | 64 | 3 | 28 | 33 | 6 | 34 | 472 |
| Normal | Normal | FULL-SELF | -2.148 | not prespecified | 64 | 7 | 12 | 45 | 13 | 24 | 475 |
| Normal | Normal | interaction | +3.711 | not prespecified | 64 | 25 | 7 | 32 | - | - | - |
| Normal | Normal | AGG-FULL | -5.859 | not prespecified | 64 | 6 | 29 | 29 | 14 | 44 | 454 |
| Normal | Normal | S0-B0 | -2.539 | not prespecified | 64 | 5 | 12 | 47 | 5 | 18 | 489 |
| Normal | Normal | PL0-B0 | +2.539 | not prespecified | 64 | 13 | 1 | 50 | 17 | 4 | 491 |
| Normal | Normal | B0-PROTO | -24.609 | not prespecified | 64 | 1 | 61 | 2 | 4 | 130 | 378 |
| Normal | Normal | B0-FedAvg | -27.734 | not prespecified | 64 | 0 | 63 | 1 | 0 | 142 | 370 |

No secondary p-value column is rendered. S05 section 5 prespecifies no secondary hypothesis test and no secondary p-value, so none is offered to readers here. The pinned pre-open analysis output `S09_QWEN_T2_ANALYSIS.json` does carry a descriptive stratified-t summary on 201 of its 371 prespecified secondary rows, all 201 of them rows of this table, of which 163 returned a non-null unadjusted two-sided value and 38 hit the zero-SE unavailable rule; that frozen file is retained unchanged at SHA-256 `df8ea84c4930e6439b5c8b40fc3615f4539370c279a16f7ddcea83dc4307673a` for audit only. None of those 163 values is used as a test, a rejection, a discovery or a familywise result anywhere in S09, and none may be cited as one. The interval column that remains is the descriptive stratified-t interval; it is unadjusted, is outside the Family B Holm family, and an interval excluding zero is not an additional rejection.

## 6. Per-fault destination tables, all eight faults, every arm

### 6.1 F1

own domain, 24 planned keys per arm:

| Arm | correct (=F1) | F8 | abstain | truncated |
|---|---:|---:|---:|---:|
| A0 | 22 | 0 | 0 | 2 |
| B0 | 8 | 16 | 0 | 0 |
| FULL | 23 | 0 | 1 | 0 |
| SELF | 24 | 0 | 0 | 0 |
| AGG | 24 | 0 | 0 | 0 |
| S0 | 17 | 6 | 1 | 0 |
| PL0 | 24 | 0 | 0 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F1) | F10 | F13 | F14 | F15 | F2 | F3 | F8 | Normal | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 52 | 16 | 15 | 1 | 3 | 18 | 3 | 17 | 11 | 26 | 2 | 4 |
| B0 | 166 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| FULL | 164 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| SELF | 1 | 0 | 3 | 2 | 1 | 0 | 2 | 22 | 4 | 133 | 0 | 0 |
| AGG | 160 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 6 | 0 | 0 |
| S0 | 162 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| PL0 | 24 | 14 | 14 | 3 | 0 | 18 | 0 | 21 | 6 | 68 | 0 | 0 |

### 6.2 F2

own domain, 24 planned keys per arm:

| Arm | correct (=F2) | abstain |
|---|---:|---:|
| A0 | 23 | 1 |
| B0 | 24 | 0 |
| FULL | 24 | 0 |
| SELF | 24 | 0 |
| AGG | 24 | 0 |
| S0 | 24 | 0 |
| PL0 | 24 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F2) | F1 | F10 | F13 | F14 | F15 | F3 | F8 | Normal | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 0 | 19 | 26 | 14 | 2 | 19 | 10 | 14 | 17 | 36 | 8 | 3 |
| B0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FULL | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SELF | 0 | 1 | 0 | 2 | 0 | 7 | 3 | 0 | 15 | 140 | 0 | 0 |
| AGG | 167 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| S0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PL0 | 0 | 17 | 26 | 11 | 2 | 2 | 0 | 11 | 6 | 91 | 2 | 0 |

### 6.3 F3

own domain, 24 planned keys per arm:

| Arm | correct (=F3) | F1 | F14 | F15 | Normal | abstain |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 18 | 1 | 0 | 0 | 2 | 3 |
| B0 | 8 | 1 | 1 | 12 | 1 | 1 |
| FULL | 19 | 1 | 1 | 1 | 1 | 1 |
| SELF | 11 | 0 | 0 | 0 | 0 | 13 |
| AGG | 20 | 1 | 0 | 0 | 1 | 2 |
| S0 | 7 | 1 | 1 | 13 | 0 | 2 |
| PL0 | 17 | 0 | 0 | 0 | 1 | 6 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F3) | F1 | F10 | F14 | F15 | F2 | F8 | Normal | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 0 | 4 | 1 | 1 | 13 | 1 | 0 | 139 | 8 | 0 | 1 |
| B0 | 3 | 5 | 0 | 4 | 12 | 0 | 2 | 128 | 14 | 0 | 0 |
| FULL | 3 | 6 | 0 | 3 | 17 | 0 | 1 | 126 | 11 | 1 | 0 |
| SELF | 0 | 1 | 0 | 0 | 4 | 0 | 1 | 135 | 27 | 0 | 0 |
| AGG | 11 | 4 | 0 | 1 | 14 | 0 | 1 | 113 | 24 | 0 | 0 |
| S0 | 8 | 6 | 0 | 7 | 6 | 0 | 0 | 123 | 18 | 0 | 0 |
| PL0 | 0 | 2 | 1 | 0 | 9 | 1 | 1 | 134 | 20 | 0 | 0 |

### 6.4 F8

own domain, 24 planned keys per arm:

| Arm | correct (=F8) | F1 | F10 | F2 | abstain | truncated |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 22 | 0 | 0 | 0 | 0 | 2 |
| B0 | 14 | 7 | 1 | 2 | 0 | 0 |
| FULL | 22 | 1 | 0 | 1 | 0 | 0 |
| SELF | 24 | 0 | 0 | 0 | 0 | 0 |
| AGG | 19 | 2 | 1 | 1 | 1 | 0 |
| S0 | 17 | 5 | 0 | 1 | 1 | 0 |
| PL0 | 24 | 0 | 0 | 0 | 0 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F8) | F1 | F10 | F13 | F14 | F15 | F2 | F3 | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 0 | 53 | 26 | 24 | 11 | 2 | 14 | 0 | 34 | 0 | 4 |
| B0 | 63 | 67 | 8 | 2 | 0 | 0 | 10 | 0 | 17 | 1 | 0 |
| FULL | 44 | 82 | 8 | 1 | 0 | 0 | 11 | 0 | 20 | 0 | 2 |
| SELF | 0 | 21 | 1 | 15 | 0 | 0 | 4 | 4 | 122 | 1 | 0 |
| AGG | 53 | 41 | 6 | 1 | 0 | 0 | 7 | 0 | 58 | 1 | 1 |
| S0 | 37 | 87 | 10 | 3 | 1 | 0 | 13 | 0 | 17 | 0 | 0 |
| PL0 | 0 | 33 | 20 | 23 | 12 | 0 | 15 | 0 | 65 | 0 | 0 |

### 6.5 F10

own domain, 24 planned keys per arm:

| Arm | correct (=F10) |  |
|---|---:|
| A0 | 24 |  |
| B0 | 24 |  |
| FULL | 24 |  |
| SELF | 24 |  |
| AGG | 24 |  |
| S0 | 24 |  |
| PL0 | 24 |  |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F10) | F1 | F13 | F14 | F15 | F2 | F3 | F8 | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 14 | 25 | 24 | 22 | 14 | 15 | 4 | 23 | 20 | 3 | 4 |
| B0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FULL | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SELF | 1 | 2 | 0 | 7 | 1 | 1 | 3 | 4 | 149 | 0 | 0 |
| AGG | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| S0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PL0 | 8 | 24 | 24 | 22 | 4 | 16 | 0 | 23 | 44 | 2 | 1 |

### 6.6 F13

own domain, 24 planned keys per arm:

| Arm | correct (=F13) | F10 | F2 | abstain |
|---|---:|---:|---:|---:|
| A0 | 23 | 1 | 0 | 0 |
| B0 | 18 | 2 | 2 | 2 |
| FULL | 18 | 2 | 1 | 3 |
| SELF | 22 | 0 | 0 | 2 |
| AGG | 18 | 2 | 1 | 3 |
| S0 | 18 | 2 | 2 | 2 |
| PL0 | 24 | 0 | 0 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F13) | F1 | F10 | F14 | F15 | F2 | F3 | F8 | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 0 | 22 | 58 | 11 | 5 | 12 | 6 | 22 | 26 | 3 | 3 |
| B0 | 122 | 0 | 15 | 0 | 0 | 14 | 0 | 3 | 12 | 1 | 1 |
| FULL | 121 | 0 | 11 | 0 | 0 | 14 | 0 | 2 | 18 | 0 | 2 |
| SELF | 0 | 11 | 0 | 1 | 2 | 5 | 2 | 16 | 130 | 1 | 0 |
| AGG | 109 | 2 | 14 | 0 | 0 | 10 | 0 | 1 | 31 | 0 | 1 |
| S0 | 121 | 1 | 16 | 0 | 0 | 18 | 0 | 1 | 10 | 1 | 0 |
| PL0 | 1 | 17 | 40 | 16 | 4 | 15 | 0 | 24 | 51 | 0 | 0 |

### 6.7 F14

own domain, 24 planned keys per arm:

| Arm | correct (=F14) | F10 |
|---|---:|---:|
| A0 | 24 | 0 |
| B0 | 23 | 1 |
| FULL | 24 | 0 |
| SELF | 24 | 0 |
| AGG | 24 | 0 |
| S0 | 24 | 0 |
| PL0 | 24 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F14) | F1 | F10 | F13 | F15 | F2 | F3 | F8 | Normal | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 2 | 7 | 39 | 17 | 13 | 3 | 5 | 13 | 4 | 58 | 5 | 2 |
| B0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FULL | 167 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| SELF | 0 | 0 | 1 | 0 | 2 | 0 | 1 | 3 | 0 | 160 | 0 | 1 |
| AGG | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| S0 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| PL0 | 3 | 3 | 11 | 12 | 3 | 1 | 1 | 13 | 0 | 120 | 1 | 0 |

### 6.8 F15

own domain, 24 planned keys per arm:

| Arm | correct (=F15) | F13 | F14 | F3 | Normal | abstain | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| A0 | 8 | 1 | 0 | 0 | 9 | 6 | 0 |
| B0 | 14 | 0 | 0 | 1 | 5 | 3 | 1 |
| FULL | 19 | 0 | 1 | 1 | 1 | 0 | 2 |
| SELF | 5 | 0 | 0 | 0 | 2 | 17 | 0 |
| AGG | 15 | 0 | 0 | 0 | 3 | 6 | 0 |
| S0 | 2 | 0 | 0 | 13 | 2 | 7 | 0 |
| PL0 | 11 | 0 | 0 | 0 | 6 | 7 | 0 |

local_unseen domain, 168 planned keys per arm:

| Arm | correct (=F15) | F1 | F10 | F14 | F3 | F8 | Normal | abstain | invalid | truncated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 1 | 0 | 2 | 1 | 20 | 1 | 136 | 6 | 0 | 1 |
| B0 | 11 | 0 | 0 | 1 | 7 | 0 | 127 | 22 | 0 | 0 |
| FULL | 1 | 0 | 0 | 0 | 19 | 0 | 131 | 17 | 0 | 0 |
| SELF | 0 | 0 | 0 | 0 | 8 | 0 | 132 | 28 | 0 | 0 |
| AGG | 0 | 0 | 0 | 3 | 33 | 0 | 109 | 22 | 1 | 0 |
| S0 | 10 | 0 | 0 | 1 | 6 | 0 | 125 | 25 | 1 | 0 |
| PL0 | 0 | 1 | 1 | 1 | 18 | 0 | 133 | 14 | 0 | 0 |

Destination cells labelled `valid`-state labels are model answers; `abstain`, `invalid` and `truncated` cells are non-answers scored zero, not misdiagnoses.

## 7. Normal domain: correctness, false alarms and false own-label assignments

| Arm | Correct / 512 | False alarms / 512 | False own-label assignments / 512 | Abstain | Invalid | Truncated | Planned pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| A0 | 400 | 82 | 78 | 28 | 0 | 2 | 512 |
| B0 | 370 | 108 | 69 | 34 | 0 | 0 | 512 |
| FULL | 361 | 116 | 99 | 33 | 1 | 1 | 512 |
| SELF | 372 | 37 | 37 | 103 | 0 | 0 | 512 |
| AGG | 331 | 132 | 103 | 46 | 3 | 0 | 512 |
| S0 | 357 | 115 | 32 | 39 | 1 | 0 | 512 |
| PL0 | 383 | 84 | 83 | 45 | 0 | 0 | 512 |

Normal has 64 independent physical runs, each reused across eight receivers; 512 is a planned key count, not 512 independent observations.

## 8. Labelled-example / target collision (seven flagged C_F2 keys)

Flagged case `case_208de85d389949569608a5a94d4dd19a`, receiver C_F2, one key per arm. The flagged case's evaluator label is F2: **True**, so the visible labelled example does reveal the correct label for those seven keys.

| Arm | Terminal state of the flagged key |
|---|---|
| A0 | valid |
| B0 | valid |
| FULL | valid |
| SELF | valid |
| AGG | valid |
| S0 | valid |
| PL0 | valid |

Full-denominator results above are retained as primary. The prespecified whole-physical-run point-only sensitivity (dropping the one flagged case from every display containing it) is:

| Partition | Domain | Contrast | Point estimate without the flagged run (pp) | Runs | Receiver keys |
|---|---|---|---:|---:|---:|
| all_faults | own | mean_A0 | +85.394 | 191 | 191 |
| all_faults | own | mean_B0 | +69.271 | 191 | 191 |
| all_faults | own | mean_FULL | +90.104 | 191 | 191 |
| all_faults | own | mean_SELF | +82.292 | 191 | 191 |
| all_faults | own | mean_AGG | +87.500 | 191 | 191 |
| all_faults | own | mean_S0 | +69.271 | 191 | 191 |
| all_faults | own | mean_PL0 | +89.583 | 191 | 191 |
| all_faults | own | B0-A0 | -16.123 | 191 | 191 |
| all_faults | own | SELF-A0 | -3.102 | 191 | 191 |
| all_faults | own | FULL-SELF | +7.813 | 191 | 191 |
| all_faults | own | interaction | +23.936 | 191 | 191 |
| all_faults | own | AGG-FULL | -2.604 | 191 | 191 |
| all_faults | own | S0-B0 | +0.000 | 191 | 191 |
| all_faults | own | PL0-B0 | +20.313 | 191 | 191 |
| all_faults | own | B0-PROTO | +8.333 | 191 | 191 |
| all_faults | own | B0-FedAvg | -3.646 | 191 | 191 |
| all_faults | own | FULL-B0 | +20.833 | 191 | 191 |
| all_faults | local_unseen | mean_A0 | +5.134 | 191 | 1337 |
| all_faults | local_unseen | mean_B0 | +64.658 | 191 | 1337 |
| all_faults | local_unseen | mean_FULL | +62.202 | 191 | 1337 |
| all_faults | local_unseen | mean_SELF | +0.149 | 191 | 1337 |
| all_faults | local_unseen | mean_AGG | +62.199 | 191 | 1337 |
| all_faults | local_unseen | mean_S0 | +62.649 | 191 | 1337 |
| all_faults | local_unseen | mean_PL0 | +2.679 | 191 | 1337 |
| all_faults | local_unseen | B0-A0 | +59.524 | 191 | 1337 |
| all_faults | local_unseen | SELF-A0 | -4.985 | 191 | 1337 |
| all_faults | local_unseen | FULL-SELF | +62.054 | 191 | 1337 |
| all_faults | local_unseen | interaction | +2.530 | 191 | 1337 |
| all_faults | local_unseen | AGG-FULL | -0.003 | 191 | 1337 |
| all_faults | local_unseen | S0-B0 | -2.009 | 191 | 1337 |
| all_faults | local_unseen | PL0-B0 | -61.979 | 191 | 1337 |
| all_faults | local_unseen | B0-PROTO | +3.720 | 191 | 1337 |
| all_faults | local_unseen | B0-FedAvg | -8.259 | 191 | 1337 |
| excluding_F1_F8 | own | mean_A0 | +83.303 | 143 | 143 |
| excluding_F1_F8 | own | mean_B0 | +77.083 | 143 | 143 |
| excluding_F1_F8 | own | mean_FULL | +88.889 | 143 | 143 |
| excluding_F1_F8 | own | mean_SELF | +76.389 | 143 | 143 |
| excluding_F1_F8 | own | mean_AGG | +86.806 | 143 | 143 |
| excluding_F1_F8 | own | mean_S0 | +68.750 | 143 | 143 |
| excluding_F1_F8 | own | mean_PL0 | +86.111 | 143 | 143 |
| excluding_F1_F8 | own | B0-A0 | -6.220 | 143 | 143 |
| excluding_F1_F8 | own | SELF-A0 | -6.914 | 143 | 143 |
| excluding_F1_F8 | own | FULL-SELF | +12.500 | 143 | 143 |
| excluding_F1_F8 | own | interaction | +18.720 | 143 | 143 |
| excluding_F1_F8 | own | AGG-FULL | -2.083 | 143 | 143 |
| excluding_F1_F8 | own | S0-B0 | -8.333 | 143 | 143 |
| excluding_F1_F8 | own | PL0-B0 | +9.028 | 143 | 143 |
| excluding_F1_F8 | own | B0-PROTO | +11.806 | 143 | 143 |
| excluding_F1_F8 | own | B0-FedAvg | +10.417 | 143 | 143 |
| excluding_F1_F8 | own | FULL-B0 | +11.806 | 143 | 143 |
| excluding_F1_F8 | local_unseen | mean_A0 | +1.687 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_B0 | +63.492 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_FULL | +62.302 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_SELF | +0.099 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_AGG | +61.801 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_S0 | +63.790 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | mean_PL0 | +1.190 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | B0-A0 | +61.806 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | SELF-A0 | -1.587 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | FULL-SELF | +62.202 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | interaction | +0.397 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | AGG-FULL | -0.500 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | S0-B0 | +0.298 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | PL0-B0 | -62.302 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | B0-PROTO | -1.786 | 143 | 1001 |
| excluding_F1_F8 | local_unseen | B0-FedAvg | -3.175 | 143 | 1001 |
| F2 | own | mean_A0 | +95.652 | 23 | 23 |
| F2 | own | mean_B0 | +100.000 | 23 | 23 |
| F2 | own | mean_FULL | +100.000 | 23 | 23 |
| F2 | own | mean_SELF | +100.000 | 23 | 23 |
| F2 | own | mean_AGG | +100.000 | 23 | 23 |
| F2 | own | mean_S0 | +100.000 | 23 | 23 |
| F2 | own | mean_PL0 | +100.000 | 23 | 23 |
| F2 | own | B0-A0 | +4.348 | 23 | 23 |
| F2 | own | SELF-A0 | +4.348 | 23 | 23 |
| F2 | own | FULL-SELF | +0.000 | 23 | 23 |
| F2 | own | interaction | -4.348 | 23 | 23 |
| F2 | own | AGG-FULL | +0.000 | 23 | 23 |
| F2 | own | S0-B0 | +0.000 | 23 | 23 |
| F2 | own | PL0-B0 | +0.000 | 23 | 23 |
| F2 | own | B0-PROTO | +0.000 | 23 | 23 |
| F2 | own | B0-FedAvg | +0.000 | 23 | 23 |
| F2 | local_unseen | mean_A0 | +0.000 | 23 | 161 |
| F2 | local_unseen | mean_B0 | +100.000 | 23 | 161 |
| F2 | local_unseen | mean_FULL | +100.000 | 23 | 161 |
| F2 | local_unseen | mean_SELF | +0.000 | 23 | 161 |
| F2 | local_unseen | mean_AGG | +99.379 | 23 | 161 |
| F2 | local_unseen | mean_S0 | +100.000 | 23 | 161 |
| F2 | local_unseen | mean_PL0 | +0.000 | 23 | 161 |
| F2 | local_unseen | B0-A0 | +100.000 | 23 | 161 |
| F2 | local_unseen | SELF-A0 | +0.000 | 23 | 161 |
| F2 | local_unseen | FULL-SELF | +100.000 | 23 | 161 |
| F2 | local_unseen | interaction | +0.000 | 23 | 161 |
| F2 | local_unseen | AGG-FULL | -0.621 | 23 | 161 |
| F2 | local_unseen | S0-B0 | +0.000 | 23 | 161 |
| F2 | local_unseen | PL0-B0 | -100.000 | 23 | 161 |
| F2 | local_unseen | B0-PROTO | +0.000 | 23 | 161 |
| F2 | local_unseen | B0-FedAvg | +0.000 | 23 | 161 |

No interval, p-value, rejection or denominator change is attached to any row in this table.

## 9. Four duplicate model-facing inputs: point-only whole-run sensitivity

Retained / dropped-in-sensitivity-only case pairs, fixed truth-blind on 2026-10-07 07:33 UTC and verified again in S09 on the frozen request grid:

| Retain | Drop in sensitivity only |
|---|---|
| `case_0617f84123844834bbb8da2aa42ca582` | `case_bf19dbac638643edb2eb333532df1b09` |
| `case_0e79c55689df4f5f966352afd33f3adc` | `case_47e998f732e548c88076ed9da43223f5` |
| `case_10f4beae3ddf46f191b52d43236563fe` | `case_cbb9bbea62584e34818f951019fd4886` |
| `case_15de141b3fce4de09e4dde88473d9b0f` | `case_e3b4f18cded74e768ec9aa331cd0dc5d` |

| Partition | Domain | Contrast | Point estimate with duplicates dropped (pp) | Runs | Receiver keys | Dropped case IDs |
|---|---|---|---:|---:|---:|---|
| all_faults | own | FULL-B0 | +20.901 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| F1 | local_unseen | B0-PROTO | +85.714 | 23 | 161 | e3b4f18c |
| all_faults | own | mean_A0 | +85.236 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_B0 | +69.067 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_FULL | +89.968 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_SELF | +82.541 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_AGG | +87.409 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_S0 | +69.271 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | mean_PL0 | +89.425 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | B0-A0 | -16.168 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | SELF-A0 | -2.695 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | FULL-SELF | +7.428 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | interaction | +23.596 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | AGG-FULL | -2.559 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | S0-B0 | +0.204 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | PL0-B0 | +20.358 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | B0-PROTO | +8.039 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | B0-FedAvg | -3.850 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | own | FULL-B0 | +20.901 | 189 | 189 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_A0 | +5.231 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_B0 | +64.661 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_FULL | +62.196 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_SELF | +0.152 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_AGG | +62.212 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_S0 | +62.655 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | mean_PL0 | +2.766 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | B0-A0 | +59.430 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | SELF-A0 | -5.079 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | FULL-SELF | +62.044 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | interaction | +2.614 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | AGG-FULL | +0.016 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | S0-B0 | -2.006 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | PL0-B0 | -61.895 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | B0-PROTO | +3.633 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| all_faults | local_unseen | B0-FedAvg | -8.256 | 189 | 1323 | 47e998f7, bf19dbac, e3b4f18c |
| excluding_F1_F8 | own | mean_A0 | +83.152 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_B0 | +77.295 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_FULL | +88.738 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_SELF | +76.721 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_AGG | +86.685 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_S0 | +68.961 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | mean_PL0 | +85.900 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | B0-A0 | -5.857 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | SELF-A0 | -6.431 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | FULL-SELF | +12.017 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | interaction | +17.874 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | AGG-FULL | -2.053 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | S0-B0 | -8.333 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | PL0-B0 | +8.605 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | B0-PROTO | +11.987 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | B0-FedAvg | +10.628 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | own | FULL-B0 | +11.443 | 142 | 142 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_A0 | +1.695 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_B0 | +63.505 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_FULL | +62.310 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_SELF | +0.099 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_AGG | +61.853 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_S0 | +63.824 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | mean_PL0 | +1.203 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | B0-A0 | +61.810 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | SELF-A0 | -1.596 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | FULL-SELF | +62.211 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | interaction | +0.401 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | AGG-FULL | -0.457 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | S0-B0 | +0.319 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | PL0-B0 | -62.302 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | B0-PROTO | -1.803 | 142 | 994 | 47e998f7, bf19dbac |
| excluding_F1_F8 | local_unseen | B0-FedAvg | -3.162 | 142 | 994 | 47e998f7, bf19dbac |
| F1_F8 | own | mean_A0 | +91.486 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_B0 | +44.384 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_FULL | +93.659 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_SELF | +100.000 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_AGG | +89.583 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_S0 | +70.199 | 47 | 47 | e3b4f18c |
| F1_F8 | own | mean_PL0 | +100.000 | 47 | 47 | e3b4f18c |
| F1_F8 | own | B0-A0 | -47.101 | 47 | 47 | e3b4f18c |
| F1_F8 | own | SELF-A0 | +8.514 | 47 | 47 | e3b4f18c |
| F1_F8 | own | FULL-SELF | -6.341 | 47 | 47 | e3b4f18c |
| F1_F8 | own | interaction | +40.761 | 47 | 47 | e3b4f18c |
| F1_F8 | own | AGG-FULL | -4.076 | 47 | 47 | e3b4f18c |
| F1_F8 | own | S0-B0 | +25.815 | 47 | 47 | e3b4f18c |
| F1_F8 | own | PL0-B0 | +55.616 | 47 | 47 | e3b4f18c |
| F1_F8 | own | B0-PROTO | -3.804 | 47 | 47 | e3b4f18c |
| F1_F8 | own | B0-FedAvg | -47.283 | 47 | 47 | e3b4f18c |
| F1_F8 | own | FULL-B0 | +49.275 | 47 | 47 | e3b4f18c |
| F1_F8 | local_unseen | mean_A0 | +15.839 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_B0 | +68.129 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_FULL | +61.853 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_SELF | +0.311 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_AGG | +63.289 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_S0 | +59.149 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | mean_PL0 | +7.453 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | B0-A0 | +52.290 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | SELF-A0 | -15.528 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | FULL-SELF | +61.542 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | interaction | +9.252 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | AGG-FULL | +1.436 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | S0-B0 | -8.980 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | PL0-B0 | -60.675 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | B0-PROTO | +19.940 | 47 | 329 | e3b4f18c |
| F1_F8 | local_unseen | B0-FedAvg | -23.538 | 47 | 329 | e3b4f18c |
| F1 | own | mean_A0 | +91.304 | 23 | 23 | e3b4f18c |
| F1 | own | mean_B0 | +30.435 | 23 | 23 | e3b4f18c |
| F1 | own | mean_FULL | +95.652 | 23 | 23 | e3b4f18c |
| F1 | own | mean_SELF | +100.000 | 23 | 23 | e3b4f18c |
| F1 | own | mean_AGG | +100.000 | 23 | 23 | e3b4f18c |
| F1 | own | mean_S0 | +69.565 | 23 | 23 | e3b4f18c |
| F1 | own | mean_PL0 | +100.000 | 23 | 23 | e3b4f18c |
| F1 | own | B0-A0 | -60.870 | 23 | 23 | e3b4f18c |
| F1 | own | SELF-A0 | +8.696 | 23 | 23 | e3b4f18c |
| F1 | own | FULL-SELF | -4.348 | 23 | 23 | e3b4f18c |
| F1 | own | interaction | +56.522 | 23 | 23 | e3b4f18c |
| F1 | own | AGG-FULL | +4.348 | 23 | 23 | e3b4f18c |
| F1 | own | S0-B0 | +39.130 | 23 | 23 | e3b4f18c |
| F1 | own | PL0-B0 | +69.565 | 23 | 23 | e3b4f18c |
| F1 | own | B0-PROTO | +17.391 | 23 | 23 | e3b4f18c |
| F1 | own | B0-FedAvg | -69.565 | 23 | 23 | e3b4f18c |
| F1 | local_unseen | mean_A0 | +31.677 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_B0 | +98.758 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_FULL | +97.516 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_SELF | +0.621 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_AGG | +95.031 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_S0 | +96.273 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | mean_PL0 | +14.907 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | B0-A0 | +67.081 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | SELF-A0 | -31.056 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | FULL-SELF | +96.894 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | interaction | +29.814 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | AGG-FULL | -2.484 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | S0-B0 | -2.484 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | PL0-B0 | -83.851 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | B0-PROTO | +85.714 | 23 | 161 | e3b4f18c |
| F1 | local_unseen | B0-FedAvg | -1.242 | 23 | 161 | e3b4f18c |
| F3 | own | mean_A0 | +73.913 | 23 | 23 | 47e998f7 |
| F3 | own | mean_B0 | +34.783 | 23 | 23 | 47e998f7 |
| F3 | own | mean_FULL | +78.261 | 23 | 23 | 47e998f7 |
| F3 | own | mean_SELF | +47.826 | 23 | 23 | 47e998f7 |
| F3 | own | mean_AGG | +82.609 | 23 | 23 | 47e998f7 |
| F3 | own | mean_S0 | +30.435 | 23 | 23 | 47e998f7 |
| F3 | own | mean_PL0 | +69.565 | 23 | 23 | 47e998f7 |
| F3 | own | B0-A0 | -39.130 | 23 | 23 | 47e998f7 |
| F3 | own | SELF-A0 | -26.087 | 23 | 23 | 47e998f7 |
| F3 | own | FULL-SELF | +30.435 | 23 | 23 | 47e998f7 |
| F3 | own | interaction | +69.565 | 23 | 23 | 47e998f7 |
| F3 | own | AGG-FULL | +4.348 | 23 | 23 | 47e998f7 |
| F3 | own | S0-B0 | -4.348 | 23 | 23 | 47e998f7 |
| F3 | own | PL0-B0 | +34.783 | 23 | 23 | 47e998f7 |
| F3 | own | B0-PROTO | +30.435 | 23 | 23 | 47e998f7 |
| F3 | own | B0-FedAvg | +34.783 | 23 | 23 | 47e998f7 |
| F3 | local_unseen | mean_A0 | +0.000 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_B0 | +1.863 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_FULL | +1.863 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_SELF | +0.000 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_AGG | +6.832 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_S0 | +4.969 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | mean_PL0 | +0.000 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | B0-A0 | +1.863 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | SELF-A0 | +0.000 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | FULL-SELF | +1.863 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | interaction | +0.000 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | AGG-FULL | +4.969 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | S0-B0 | +3.106 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | PL0-B0 | -1.863 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | B0-PROTO | -2.484 | 23 | 161 | 47e998f7 |
| F3 | local_unseen | B0-FedAvg | +1.863 | 23 | 161 | 47e998f7 |
| F14 | own | mean_A0 | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | mean_B0 | +95.652 | 23 | 23 | bf19dbac |
| F14 | own | mean_FULL | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | mean_SELF | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | mean_AGG | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | mean_S0 | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | mean_PL0 | +100.000 | 23 | 23 | bf19dbac |
| F14 | own | B0-A0 | -4.348 | 23 | 23 | bf19dbac |
| F14 | own | SELF-A0 | +0.000 | 23 | 23 | bf19dbac |
| F14 | own | FULL-SELF | +0.000 | 23 | 23 | bf19dbac |
| F14 | own | interaction | +4.348 | 23 | 23 | bf19dbac |
| F14 | own | AGG-FULL | +0.000 | 23 | 23 | bf19dbac |
| F14 | own | S0-B0 | +4.348 | 23 | 23 | bf19dbac |
| F14 | own | PL0-B0 | +4.348 | 23 | 23 | bf19dbac |
| F14 | own | B0-PROTO | -4.348 | 23 | 23 | bf19dbac |
| F14 | own | B0-FedAvg | -4.348 | 23 | 23 | bf19dbac |
| F14 | local_unseen | mean_A0 | +1.242 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_B0 | +100.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_FULL | +99.379 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_SELF | +0.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_AGG | +100.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_S0 | +100.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | mean_PL0 | +1.863 | 23 | 161 | bf19dbac |
| F14 | local_unseen | B0-A0 | +98.758 | 23 | 161 | bf19dbac |
| F14 | local_unseen | SELF-A0 | -1.242 | 23 | 161 | bf19dbac |
| F14 | local_unseen | FULL-SELF | +99.379 | 23 | 161 | bf19dbac |
| F14 | local_unseen | interaction | +0.621 | 23 | 161 | bf19dbac |
| F14 | local_unseen | AGG-FULL | +0.621 | 23 | 161 | bf19dbac |
| F14 | local_unseen | S0-B0 | +0.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | PL0-B0 | -98.137 | 23 | 161 | bf19dbac |
| F14 | local_unseen | B0-PROTO | +0.000 | 23 | 161 | bf19dbac |
| F14 | local_unseen | B0-FedAvg | +0.000 | 23 | 161 | bf19dbac |
| Normal | Normal | mean_A0 | +78.175 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_B0 | +72.222 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_FULL | +70.437 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_SELF | +72.619 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_AGG | +64.484 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_S0 | +69.643 | 63 | 504 | cbb9bbea |
| Normal | Normal | mean_PL0 | +74.802 | 63 | 504 | cbb9bbea |
| Normal | Normal | B0-A0 | -5.952 | 63 | 504 | cbb9bbea |
| Normal | Normal | SELF-A0 | -5.556 | 63 | 504 | cbb9bbea |
| Normal | Normal | FULL-SELF | -2.183 | 63 | 504 | cbb9bbea |
| Normal | Normal | interaction | +3.770 | 63 | 504 | cbb9bbea |
| Normal | Normal | AGG-FULL | -5.952 | 63 | 504 | cbb9bbea |
| Normal | Normal | S0-B0 | -2.579 | 63 | 504 | cbb9bbea |
| Normal | Normal | PL0-B0 | +2.579 | 63 | 504 | cbb9bbea |
| Normal | Normal | B0-PROTO | -24.603 | 63 | 504 | cbb9bbea |
| Normal | Normal | B0-FedAvg | -27.778 | 63 | 504 | cbb9bbea |

Point estimates only, across all receivers and arms. No replacement case, no alternative pair member chosen after labels, no new interval, p-value or rejection. This sensitivity describes possible dependence; it does not make the primary independence assumption true.

## 10. Missingness, format and transport accounting

| Quantity | Value |
|---|---:|
| Planned semantic keys | 14336 |
| Keys with at least one transport attempt | 14336 |
| Total transport attempts (ceiling 28,672) | 14336 |
| Adjudications required | 0 |
| Terminal state `valid` | 11912 |
| Terminal state `abstain` | 2343 |
| Terminal state `invalid` | 43 |
| Terminal state `truncated` | 38 |
| Terminal state `missing` | 0 |
| Terminal state `uncertain` | 0 |
| Contract-rejected responses (deployed-parser-only) | 43 |
| ... all rejected solely by the 1,200-character summary cap | 43 |
| ... rejected-response summary length range (chars) | 1232-3592 |

## 11. Supplemental cost and duration accounting (separately named, not a primary score)

| Arm | Tier | Full input tokens | Full output tokens | Reasoning tokens | Input tokens omitted by the pinned normalizer | Output tokens omitted | Reservation-to-finish median s | p90 s | Total s | First finish UTC | Last finish UTC |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| A0 | 1 | 1650296 | 2382210 | unobserved | 15219 | 33923 | 12.483 | 13.048 | 25751 | 2026-10-06T16:30:53.645191+00:00 | 2026-10-07T01:38:35.627184+00:00 |
| B0 | 1 | 5767032 | 2455271 | unobserved | 8445 | 4816 | 12.556 | 13.044 | 25896 | 2026-10-06T16:30:53.699605+00:00 | 2026-10-07T01:38:48.650069+00:00 |
| FULL | 2 | 6372984 | 2496863 | unobserved | 11574 | 5701 | 12.672 | 13.219 | 26166 | 2026-10-06T16:30:53.803872+00:00 | 2026-10-07T01:38:48.660456+00:00 |
| SELF | 2 | 2256248 | 2395734 | unobserved | 1622 | 2959 | 12.527 | 13.109 | 25844 | 2026-10-06T16:30:53.809605+00:00 | 2026-10-07T01:38:48.661543+00:00 |
| AGG | 3 | 7511672 | 2471502 | unobserved | 18239 | 7450 | 12.612 | 13.098 | 25953 | 2026-10-06T16:31:06.397270+00:00 | 2026-10-07T01:38:48.662557+00:00 |
| S0 | 4 | 6577016 | 2397453 | unobserved | 9487 | 4542 | 12.24 | 12.597 | 25157 | 2026-10-07T01:39:00.961585+00:00 | 2026-10-07T05:09:51.480927+00:00 |
| PL0 | 4 | 4169592 | 2339556 | unobserved | 10118 | 8353 | 12.264 | 12.61 | 25233 | 2026-10-07T01:39:00.995618+00:00 | 2026-10-07T05:09:51.491535+00:00 |

Total tokens the pinned primary accounting omits: 74704 input and 67744 output, all from the 43 contract-rejected responses. The reservation-to-finish column includes scheduler reservation overhead and is not server-side request latency; no latency field exists in the ledger, so the Latency column of the prepared displays stays unfillable.

Per-tier serving identity:

| Event kind | Events | Distinct fingerprints (timestamps ignored) | First UTC | Last UTC |
|---|---:|---:|---|---|
| periodic_serving_identity | 74 | 1 | 2026-10-06T16:40:38.610804+00:00 | 2026-10-07T05:00:51.186721+00:00 |
| secondary_serving_identity | 1 | 1 | 2026-10-07T01:38:48.676229+00:00 | 2026-10-07T01:38:48.676229+00:00 |
| serving_identity | 1 | 1 | 2026-10-06T16:30:38.549159+00:00 | 2026-10-06T16:30:38.549159+00:00 |

Observed fingerprint, identical for the interleaved primary pass and the later tier-4 pass: model `qwen3.5-122b`, root `Qwen/Qwen3.5-122B-A10B-FP8`, vLLM `0.27.1`, maxModelLen 131072, checkpointRevision None, tokenizer fixture response SHA-256 `cc39c68295a95cc26f1642095bc55adefdccaff706f5441b3905ee0c01938077`.

## 12. Backend nondeterminism on byte-identical requests

| Quantity | Value |
|---|---:|
| Distinct wire digests sent more than once | 224 |
| Keys inside those groups | 448 |
| Comparable key pairs | 224 |
| Pairs whose stored response bytes are identical | 0 |

Under temperature 0, top_p 1 and seed 20260927, no byte-identical request pair returned byte-identical stored output. The campaign cannot be reproduced by re-sending; the immutable backup is the sole evidentiary record.

## 13. Length-only baseline check

| Length-only baseline check | Definition frozen before opening | Result | Limit |
|---|---|---|---|
| Scored comparator using response or prompt length without diagnostic text | **none** | not computed | No such comparator was defined or hashed before the opening, so any definition chosen now would be post-hoc. S09 declines to fill this cell rather than invent a comparator after truth access. |

The only length-related evidence S09 can report without post-hoc definition is the truth-blind summary-length distribution measured before the first truth access:

| Arm | Mean summary chars | 0-199 | 200-399 | 400-599 | 600-799 | 800-999 | 1000-1199 | 1200-1599 | 1600-2399 | 2400+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 394.7 | 71 | 1216 | 602 | 91 | 15 | 4 | 2 | 9 | 10 |
| B0 | 467.1 | 7 | 528 | 1310 | 189 | 9 | 1 | 2 | 0 | 1 |
| FULL | 470.5 | 6 | 524 | 1299 | 183 | 26 | 1 | 4 | 0 | 0 |
| SELF | 374.5 | 58 | 1264 | 660 | 55 | 7 | 1 | 1 | 1 | 0 |
| AGG | 444.1 | 7 | 696 | 1198 | 130 | 6 | 4 | 3 | 2 | 0 |
| S0 | 400.8 | 50 | 1037 | 900 | 52 | 4 | 2 | 0 | 3 | 0 |
| PL0 | 358.7 | 104 | 1314 | 587 | 35 | 2 | 0 | 1 | 1 | 3 |

Bins at or above 1200 characters are the region the deployed parser rejects outright.
