# Set 1 Strict Summary

This document summarizes the first-try strict gate results for all complete set 1 evaluations.

## Variance Evaluations (Temperature 0.2, 3 Repeats, N=36)

| Model | Prompt | Run ID | Syntax Errors | Single Pass | Strict Pass | MISSED_SHOWN | NOISY | TOO_NARROW | Total N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 20261021_1528_set1_v1 | 8 | 28/36 | 7/36 | 0 | 0 | 21 | 36 |
| qwen2.5-coder:14b | v1 | 20261021_1528_set1_v1 | 0 | 35/36 | 3/36 | 1 | 0 | 32 | 36 |
| qwen2.5-coder:7b | v2 | 20261104_1503_set1_v2 | 0 | 36/36 | 9/36 | 0 | 0 | 27 | 36 |
| qwen2.5-coder:14b | v2 | 20261104_1503_set1_v2 | 10 | 26/36 | 8/36 | 0 | 0 | 18 | 36 |
| qwen2.5-coder:7b | v2_1 | 20261106_1344_set1_v2_1 | 0 | 36/36 | 11/36 | 0 | 0 | 25 | 36 |
| qwen2.5-coder:14b | v2_1 | 20261106_1344_set1_v2_1 | 0 | 36/36 | 8/36 | 0 | 0 | 28 | 36 |
| qwen2.5-coder:7b | v3a | 20261111_1403_set1_v3a | 0 | 36/36 | 16/36 | 0 | 0 | 20 | 36 |
| qwen2.5-coder:14b | v3a | 20261111_1403_set1_v3a | 0 | 35/36 | 19/36 | 0 | 1 | 16 | 36 |
| qwen2.5-coder:7b | v3b | 20261111_1413_set1_v3b | 0 | 28/36 | 15/36 | 0 | 8 | 13 | 36 |
| qwen2.5-coder:14b | v3b | 20261111_1413_set1_v3b | 0 | 30/36 | 21/36 | 0 | 6 | 9 | 36 |

## Single Runs (Temperature 0, 1 Repeat, N=12)

| Model | Prompt | Run ID | Syntax Errors | Single Pass | Strict Pass | MISSED_SHOWN | NOISY | TOO_NARROW | Total N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 20261021_1510_set1_v1 | 2 | 10/12 | 2/12 | 0 | 0 | 8 | 12 |
| qwen2.5-coder:7b | v1 | 20261021_1510_01_set1_v1 | 2 | 10/12 | 2/12 | 0 | 0 | 8 | 12 |
| qwen2.5-coder:7b | v2 | 20261021_1511_set1_v2 | 0 | 12/12 | 3/12 | 0 | 0 | 9 | 12 |
| qwen2.5-coder:14b | v2 | 20261021_1511_set1_v2 | 4 | 8/12 | 1/12 | 0 | 0 | 7 | 12 |

## Strict Passes per Technique (out of 3 repeats, Temperature 0.2)

| Model | Prompt | T1059.001 | T1218.011 | T1218.005 | T1218.010 | T1105 | T1053.005 | T1547.001 | T1136.001 | T1003.001 | T1197 | T1047 | T1033 | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 0/3 | 0/3 | 3/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 7/36 |
| qwen2.5-coder:14b | v1 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/36 |
| qwen2.5-coder:7b | v2 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 9/36 |
| qwen2.5-coder:14b | v2 | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 8/36 |
| qwen2.5-coder:7b | v2_1 | 0/3 | 0/3 | 0/3 | 3/3 | 2/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 11/36 |
| qwen2.5-coder:14b | v2_1 | 0/3 | 0/3 | 0/3 | 3/3 | 1/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 8/36 |
| qwen2.5-coder:7b | v3a | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 3/3 | 3/3 | 16/36 |
| qwen2.5-coder:14b | v3a | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 3/3 | 19/36 |
| qwen2.5-coder:7b | v3b | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 2/3 | 3/3 | 15/36 |
| qwen2.5-coder:14b | v3b | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 21/36 |
