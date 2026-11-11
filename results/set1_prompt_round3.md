# Set 1 Prompt Round 3 Comparison (Final Tuning Round)

This document evaluates prompt versions v1, v2, v2_1, v3a, and v3b on Set 1 across `qwen2.5-coder:7b` and `qwen2.5-coder:14b` (temperature 0.2, 3 repeats, seed 100, 36 rules per model-prompt configuration).

## Overall Metrics Comparison (First-Try Rules)

| Model | Prompt | Syntax Errors | Single Pass | Strict Pass (/36) | Strict Pass (/30) | MISSED_SHOWN | NOISY | TOO_NARROW | Avg Sec/Rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 8 | 28/36 | **7/36** | 7/30 | 0 | 0 | 21 | 4.53s |
| qwen2.5-coder:14b | v1 | 0 | 35/36 | **3/36** | 3/30 | 1 | 0 | 32 | 5.36s |
| qwen2.5-coder:7b | v2 | 0 | 36/36 | **9/36** | 9/30 | 0 | 0 | 27 | 4.16s |
| qwen2.5-coder:14b | v2 | 10 | 26/36 | **8/36** | 8/30 | 0 | 0 | 18 | 9.87s |
| qwen2.5-coder:7b | v2_1 | 0 | 36/36 | **11/36** | 11/30 | 0 | 0 | 25 | 3.74s |
| qwen2.5-coder:14b | v2_1 | 0 | 36/36 | **8/36** | 8/30 | 0 | 0 | 28 | 5.25s |
| qwen2.5-coder:7b | v3a | 0 | 36/36 | **16/36** | 16/30 | 0 | 0 | 20 | 4.33s |
| qwen2.5-coder:14b | v3a | 0 | 35/36 | **19/36** | 19/30 | 0 | 1 | 16 | 10.87s |
| qwen2.5-coder:7b | v3b | 0 | 28/36 | **15/36** | 15/30 | 0 | 8 | 13 | 5.04s |
| qwen2.5-coder:14b | v3b | 0 | 30/36 | **21/36** | 21/30 | 0 | 6 | 9 | 8.21s |

## Strict Passes per Technique (out of 3 repeats)

| Model | Prompt | T1059.001 | T1218.011 | T1218.005 | T1218.010 | T1105 | T1053.005 | T1547.001 | T1136.001 | T1003.001 | T1197 | T1047 | T1033 | Total (/36) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 0/3 | 0/3 | 3/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | **7/36** |
| qwen2.5-coder:14b | v1 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | **3/36** |
| qwen2.5-coder:7b | v2 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | **9/36** |
| qwen2.5-coder:14b | v2 | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | **8/36** |
| qwen2.5-coder:7b | v2_1 | 0/3 | 0/3 | 0/3 | 3/3 | 2/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | **11/36** |
| qwen2.5-coder:14b | v2_1 | 0/3 | 0/3 | 0/3 | 3/3 | 1/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | **8/36** |
| qwen2.5-coder:7b | v3a | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 1/3 | 3/3 | 3/3 | **16/36** |
| qwen2.5-coder:14b | v3a | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 0/3 | 0/3 | 0/3 | 1/3 | 1/3 | 3/3 | **19/36** |
| qwen2.5-coder:7b | v3b | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 2/3 | 3/3 | **15/36** |
| qwen2.5-coder:14b | v3b | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 | **21/36** |

## Failure Mode Classification Across Prompts (Primary Blocker for TOO_NARROW Rules)

| Model | Prompt | Total TOO_NARROW | ALIAS_IMAGE | VALUE | FLAG_INCIDENTAL | ADJACENT | PREFIX | OTHER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | v1 | 21 | 3 | 12 | 0 | 3 | 3 | 0 |
| qwen2.5-coder:14b | v1 | 32 | 5 | 21 | 3 | 0 | 3 | 0 |
| qwen2.5-coder:7b | v2 | 27 | 6 | 18 | 3 | 0 | 0 | 0 |
| qwen2.5-coder:14b | v2 | 18 | 3 | 15 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | v2_1 | 25 | 6 | 16 | 3 | 0 | 0 | 0 |
| qwen2.5-coder:14b | v2_1 | 28 | 6 | 19 | 3 | 0 | 0 | 0 |
| qwen2.5-coder:7b | v3a | 20 | 6 | 11 | 3 | 0 | 0 | 0 |
| qwen2.5-coder:14b | v3a | 16 | 6 | 7 | 3 | 0 | 0 | 0 |
| qwen2.5-coder:7b | v3b | 13 | 3 | 6 | 4 | 0 | 0 | 0 |
| qwen2.5-coder:14b | v3b | 9 | 6 | 0 | 3 | 0 | 0 | 0 |

## Prompt v3b Chain-of-Thought Scratchpad Analysis

For prompt v3b, models were instructed to output `# keep: <token>` and `# ignore: <tokens>` comments before the YAML rule.

- Total first-try raw responses analyzed: 72 (36 from `qwen2.5-coder:7b`, 36 from `qwen2.5-coder:14b`).
- Responses containing a line starting with `# keep:`: 72 of 72 (100%).
- Responses containing a line starting with `# ignore:`: 72 of 72 (100%).
- Responses containing any other comments: 0 of 72 (0%).

Both models strictly followed the required comment formatting without extraneous text.

