# Rescore of All Saved Runs under True Strict Gate

This document records the true single-gate and strict-gate numbers for all saved complete runs and prompt v1 archives.

## Rescore Table

| run or archive id | set | prompt | model | temperature | repeats | single pass first try | strict pass first try | single pass final | strict pass final | SYNTAX_ERROR | MISSED_SHOWN | NOISY | TOO_NARROW | old strict number | changed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20261021_1510_set1_v1 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | 10/12 | 2/12 | 2 | 0 | 0 | 8 | 10/12 | yes |
| 20261021_1510_01_set1_v1 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | 10/12 | 2/12 | 2 | 0 | 0 | 8 | 10/12 | yes |
| 20261021_1511_set1_v2 | 1 | v2 | qwen2.5-coder:7b | 0 | 1 | 12/12 | 3/12 | 12/12 | 3/12 | 0 | 0 | 0 | 9 | 12/12 | yes |
| 20261021_1511_set1_v2 | 1 | v2 | qwen2.5-coder:14b | 0 | 1 | 8/12 | 1/12 | 8/12 | 1/12 | 4 | 0 | 0 | 7 | 8/12 | yes |
| 20261021_1528_set1_v1 | 1 | v1 | qwen2.5-coder:7b | 0.2 | 3 | 28/36 | 7/36 | 28/36 | 7/36 | 8 | 0 | 0 | 21 | 28/36 | yes |
| 20261021_1528_set1_v1 | 1 | v1 | qwen2.5-coder:14b | 0.2 | 3 | 35/36 | 3/36 | 35/36 | 3/36 | 0 | 1 | 0 | 32 | 35/36 | yes |
| 20261104_1503_set1_v2 | 1 | v2 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 9/36 | 36/36 | 9/36 | 0 | 0 | 0 | 27 | 36/36 | yes |
| 20261104_1503_set1_v2 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 8/36 | 26/36 | 8/36 | 10 | 0 | 0 | 18 | 26/36 | yes |
| 20261106_1338_set1_v2 | 1 | v2 | qwen2.5-coder:14b | 0.2 | 3 | 26/36 | 8/36 | 36/36 | 11/36 | 10 | 0 | 0 | 18 | 26/36 | yes |
| 20261106_1344_set1_v2_1 | 1 | v2_1 | qwen2.5-coder:7b | 0.2 | 3 | 36/36 | 11/36 | 36/36 | 11/36 | 0 | 0 | 0 | 25 | 36/36 | yes |
| 20261106_1344_set1_v2_1 | 1 | v2_1 | qwen2.5-coder:14b | 0.2 | 3 | 36/36 | 8/36 | 36/36 | 8/36 | 0 | 0 | 0 | 28 | 36/36 | yes |
| archive_v1_set1 | 1 | v1 | mistral:7b | 0 | 1 | 4/12 | 1/12 | - | - | 6 | 2 | 0 | 3 | 4/12 | yes |
| archive_v1_set1 | 1 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | - | - | 2 | 0 | 0 | 8 | 10/12 | yes |
| archive_v1_set1 | 1 | v1 | mistral-rules | 0 | 1 | 10/12 | 1/12 | - | - | 0 | 2 | 0 | 9 | 10/12 | yes |
| archive_v1_set1 | 1 | v1 | qwen2.5-coder:14b | 0 | 1 | 11/12 | 1/12 | - | - | 0 | 1 | 0 | 10 | 11/12 | yes |
| archive_v1_set2 | 2 | v1 | qwen2.5-coder:7b | 0 | 1 | 10/12 | 2/12 | - | - | 1 | 1 | 0 | 8 | 2/12 | no |
| archive_v1_set2 | 2 | v1 | qwen2.5-coder:14b | 0 | 1 | 9/12 | 2/12 | - | - | 0 | 3 | 0 | 7 | 2/12 | no |
| archive_v1_set2 | 2 | v1 | mistral-rules | 0 | 1 | 6/12 | 0/12 | - | - | 0 | 6 | 0 | 6 | 0/12 | no |

## Regression Checks

### Set 2 Baseline Counts

Baseline reported in AGENTS.md for set 2 (prompt v1, 12 techniques):

| Model | PASS | SYNTAX_ERROR | MISSED_SHOWN | TOO_NARROW | NOISY | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| qwen2.5-coder:7b | 2 | 1 | 1 | 8 | 0 | PASS |
| qwen2.5-coder:14b | 2 | 0 | 3 | 7 | 0 | PASS |
| mistral-rules | 0 | 0 | 6 | 6 | 0 | PASS |

### Run 20261106_1338 Repair Check

- First-try strict pass: 8/36 (expected 8/36)
- Final strict pass after repair: 11/36 (expected 11/36)
- Status: PASS
