# ATIDEP Results Summary

| id | date | set | prompt | model | temperature | repeats | single gate pass | strict gate pass | first-try syntax errors | final pass after repair (single gate) | final strict pass after repair | notes |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20261021_1510_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 10/12 | 2 | 10 | 10 | COMPLETE |
| 20261021_1510_01_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 10/12 | 2 | 10 | 10 | COMPLETE |
| 20261021_1511_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0 | 1 | 12/12 | 12/12 | 0 | 12 | 12 | COMPLETE |
| 20261021_1511_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0 | 1 | 8/12 | 8/12 | 4 | 8 | 8 | COMPLETE |
| 20261021_1528_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0.2 | 3 | 28/36 | 28/36 | 8 | 28 | 28 | COMPLETE |
| 20261021_1528_set1_v1 | 2026-10-21 | 1 | v1 | qwen2.5-coder:14b | 0.2 | 3 | 35/36 | 35/36 | 0 | 35 | 35 | COMPLETE |
| 20261021_1534_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | - | - | - | - | - | PARTIAL 40/72 rules |
| 20261021_1534_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | - | PARTIAL 40/72 rules |
| 20261021_1536_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | - | - | - | - | - | PARTIAL 67/72 rules |
| 20261021_1536_set1_v2 | 2026-10-21 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | - | PARTIAL 67/72 rules |
| 20261104_1503_set1_v2 | 2026-11-04 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 36/36 | 0 | 36 | 36 | COMPLETE |
| 20261104_1503_set1_v2 | 2026-11-04 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 26/36 | 10 | 26 | 26 | COMPLETE |
| 20261106_1338_set1_v2 | 2026-11-06 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 26/36 | 10 | 36 | 29 | COMPLETE |
| 20261106_1344_set1_v2_1 | 2026-11-06 | 1 | v2_1 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 36/36 | 0 | 36 | 36 | COMPLETE |
| 20261106_1344_set1_v2_1 | 2026-11-06 | 1 | v2_1 | qwen2.5-coder:14b | 0.2 | 3 | 36/36 | 36/36 | 0 | 36 | 36 | COMPLETE |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | mistral:7b | 0 | 1 | 4/12 | 4/12 | 0 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 10/12 | 2 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | mistral-rules | 0 | 1 | 10/12 | 10/12 | 0 | - | - | ARCHIVED |
| archive_v1_rescore | 2026-10-21 | 1 | v1 | qwen2.5-coder:14b | 0 | 1 | 11/12 | 11/12 | 0 | - | - | ARCHIVED |
| repair_hint_v2_14b | 2026-11-04 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | - | - | - | - | - | superseded: run as 20261106_1338_set1_v2 |

Set 1 variants cannot show generalisation, because a keyword rule passes all 12.

Set 2 is the prompt v1 baseline only.
