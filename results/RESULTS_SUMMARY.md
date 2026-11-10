# ATIDEP Results Summary

| id | date | set | prompt | model | temperature | repeats | single pass (first try) | strict pass (first try) | final single pass | final strict pass | notes |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20261021_1510_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | 10/12 | 2/12 | COMPLETE |
| 20261021_1510_01_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | 10/12 | 2/12 | COMPLETE |
| 20261021_1511_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0 | 1 | 12/12 | 3/12 | 12/12 | 3/12 | COMPLETE |
| 20261021_1511_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0 | 1 | 8/12 | 1/12 | 8/12 | 1/12 | COMPLETE |
| 20261021_1528_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0.2 | 3 | 28/36 | 7/36 | 28/36 | 7/36 | COMPLETE |
| 20261021_1528_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:14b | 0.2 | 3 | 35/36 | 3/36 | 35/36 | 3/36 | COMPLETE |
| 20261021_1534_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | - | - | - | - | PARTIAL 40/72 rules |
| 20261021_1534_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | PARTIAL 40/72 rules |
| 20261021_1536_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | - | - | - | - | PARTIAL 67/72 rules |
| 20261021_1536_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | PARTIAL 67/72 rules |
| 20261104_1503_set1_v2 | 2026-11-04 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 9/36 | 36/36 | 9/36 | COMPLETE |
| 20261104_1503_set1_v2 | 2026-11-04 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 8/36 | 26/36 | 8/36 | COMPLETE |
| 20261106_1338_set1_v2 | 2026-11-06 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 8/36 | 36/36 | 11/36 | COMPLETE |
| 20261106_1344_set1_v2_1 | 2026-11-06 | 1 | v2_1 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 11/36 | 36/36 | 11/36 | COMPLETE |
| 20261106_1344_set1_v2_1 | 2026-11-06 | 1 | v2_1 | qwen2.5-coder:14b | 0.2 | 3 | 36/36 | 8/36 | 36/36 | 8/36 | COMPLETE |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | mistral:7b | 0 | 1 | 4/12 | 1/12 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | mistral-rules | 0 | 1 | 10/12 | 1/12 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | qwen2.5-coder:14b | 0 | 1 | 11/12 | 1/12 | - | - | ARCHIVED |
| repair_hint_v2_14b | 2026-11-04 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | superseded: run as 20261106_1338_set1_v2 |

Under the true strict gate requiring the hidden variant, set 1 separates prompt versions and reveals overfitting: qwen 7b achieves 9/36 under v2 and 11/36 under v2_1, while qwen 14b achieves 8/36 under both. Most failures on set 1 are TOO_NARROW (rules that overfit to the shown command line).

Set 2 is the prompt v1 baseline only.
