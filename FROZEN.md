# ATIDEP Frozen Configuration

Date: 2026-11-11 (originally frozen 2026-11-06; decision redone 2026-11-10; updated 2026-11-11 following Round 3 prompt evaluation)

## Selected Models and Prompts

### Selection Decision Table (Set 1, Temperature 0.2, Repeats 3, Candidates: v2_1, v3a, v3b)

| Model | Prompt Candidate | First-try Strict Pass | First-try Syntax Errors | First-try Single Pass | Chosen |
| --- | --- | ---: | ---: | ---: | --- |
| qwen2.5-coder:7b | v2_1 (run 20261106_1344) | 11/36 | 0 | 36/36 | No |
| qwen2.5-coder:7b | v3a (run 20261111_1403) | 16/36 | 0 | 36/36 | **Yes** (highest strict pass: 16 > 15 > 11) |
| qwen2.5-coder:7b | v3b (run 20261111_1413) | 15/36 | 0 | 28/36 | No |
| qwen2.5-coder:14b | v2_1 (run 20261106_1344) | 8/36 | 0 | 36/36 | No |
| qwen2.5-coder:14b | v3a (run 20261111_1403) | 19/36 | 0 | 35/36 | No |
| qwen2.5-coder:14b | v3b (run 20261111_1413) | 21/36 | 0 | 30/36 | **Yes** (highest strict pass: 21 > 19 > 8) |

Primary model choice:
- qwen2.5-coder:14b under chosen prompt v3b: 21/36 first-try strict pass.
- qwen2.5-coder:7b under chosen prompt v3a: 16/36 first-try strict pass.
- Selection: qwen2.5-coder:14b is selected as primary model (higher first-try strict pass: 21 > 16).

### Frozen Configuration

- Primary model: qwen2.5-coder:14b
  - Chosen prompt: v3b
  - Quantization: Q4_K_M
  - Selection rationale: In prompt round 3 on set 1 (temperature 0.2, 3 repeats, seed 100), qwen2.5-coder:14b achieved 21/36 first-try strict passes under prompt v3b (versus 19/36 under v3a and 8/36 under v2_1, all with 0 syntax errors). Under the primary model selection rule (highest strict pass under chosen prompt), qwen2.5-coder:14b (21/36) outperformed qwen2.5-coder:7b (16/36 under v3a), and is therefore selected as the primary model.
- Comparison model: qwen2.5-coder:7b
  - Chosen prompt: v3a
  - Quantization: Q4_K_M
  - Selection rationale: In prompt round 3 on set 1, qwen2.5-coder:7b achieved 16/36 first-try strict passes under prompt v3a (versus 15/36 under v3b and 11/36 under v2_1, all with 0 syntax errors). Prompt v3a maintained a 36/36 single pass rate with 0 syntax errors and 0 noisy rules.

The final evaluation on test set 3 compares prompt v1 with the frozen prompt for each model (v1 vs v3b for qwen2.5-coder:14b; v1 vs v3a for qwen2.5-coder:7b).

## Runtime Parameters

- Temperature: 0.2
- Repeats: 3
- Seed option and value: --seed 100 (repeat 1 uses 100, repeat 2 uses 101, repeat 3 uses 102)
- num_ctx: 4096
- max_tokens: 800

## Environment Information

- Ollama version: ollama version is 0.40.7
- GPU name: NVIDIA RTX 4000 Ada Generation

### Local Ollama Models (http://localhost:11434/api/tags)

- qwen2.5-coder:7b: dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364 (quantization: Q4_K_M)
- qwen2.5-coder:14b: 9ec8897f747e246e970bc5cfdda85d22f1123dc2e3d34978a010a75968716849 (quantization: Q4_K_M)
- mistral:7b: 6577803aa9a036369e481d648a2baebb381ebc6e897f2bb9a766a2aa7bfbc1cf
- mistral-rules:latest: b6c19935b6d332bac251c646dc98331796577fa73a57feb5e49233fa07010688

## Frozen File Hashes (SHA-256)

| File | SHA-256 |
| --- | --- |
| llm/prompts/v1.py | 5fef6e6082f7f96920d48fab97cb8ee9d8c23b5e077c381dbccae71b67d54829 |
| llm/prompts/v2.py | ae6231f8dd8cc67c7b574a573d6b4812ffbd0efad7864537080de3199be6f5d3 |
| llm/prompts/v2_1.py | bd19f52f5824f744286ccd9035e7ccc77337bf6cd4efc9abaffb753fea7761d4 |
| llm/prompts/v3a.py | 4c8dbea167dc690b5c77226c42d5ac518b843183bfd655fd401b0f5c776e62d0 |
| llm/prompts/v3b.py | cba7e60ab7d9075727e4841e1fd51ee09739d683bb1078af67378770540c746d |
| validator/runner.py | e9aa0bf6189b57f0a99319e60c3dddeb0663bc1b3d9a1b6a75193b160f97f54f |
| generator/generate.py | 2dce9a88ebbb79187ed558c3e9ffd0cf8170733ff7dcce2376e20468b00f8700 |
| generator/techniques_set2.py | 8577581a4d9d1e3524d1bae28e850f26e23f714f7ef8c5d4c101979044b74acf |
| generator/techniques_set3.py | c86d7307e124309f0824e3dd844673d381f0275cdd333ec6d57dabdb575179f8 |
| llm/analyze_results.py | d0627fdb2870beb7152607f0a1a60fd91e1b393fe845b0356c1ac41e4598c2e3 |
| llm/run_experiment.py | 7b20b37a787848636be485a9e3c7641ab875c44113d6680abad3291003711dfd |
| llm/scoring.py | 193c272d45fa23c6f5daf5f50bfbfcdeeb89b896f99425e42a358685b336385c |

## Superseded decisions

### Superseded decision 2 (2026-11-10: v2_1 selected over v2)

On 2026-11-10, following the strict gate rescoring, prompt v2_1 was selected for both models over prompt v2:
- qwen2.5-coder:7b scored 11/36 first-try strict passes on v2_1 vs 9/36 on v2.
- qwen2.5-coder:14b tied on strict passes (8/36 on both), but v2_1 had 0 syntax errors vs 10 on v2.
- qwen2.5-coder:7b was primary model (11 > 8).
Superseded on 2026-11-11 by prompt round 3 results where prompt v3a scored 16/36 for 7b, prompt v3b scored 21/36 for 14b, and 14b became primary model.

### Superseded decision 1 (2026-11-06: used single-gate numbers by mistake)

On 2026-11-06, qwen2.5-coder:7b was assigned prompt v2 under the assumption that both v2 and v2_1 scored 36/36 first-try strict passes on set 1, triggering the tie-breaker to pick v2. However, the pipeline at that time evaluated only the single gate for set 1 (checking shown line and benign line, but omitting the hidden variant). Under the true strict gate checking the hidden variant, prompt v2 scores only 9/36 while prompt v2_1 scores 11/36. Thus, prompt v2_1 is selected for qwen2.5-coder:7b without needing a tie-breaker.

## Pre-registration for the final test on set 3 (written 2026-11-11 14:45 PKT, before any run)

Primary comparison: for each model, its frozen prompt against prompt v1. Primary metric: first-try strict pass out of 60 (20 techniques x 3 repeats). Also reported: techniques passed (at least 2 of 3 repeats strict) out of 20, and the paired comparison per technique (improved, same, worse).
Exploratory (labelled as such in every table): the other v3 prompt for each model.
Exactly these runs, set 3, --final, temperature 0.2, 3 repeats, seed from this file:
1. prompt v1, qwen2.5-coder:14b and qwen2.5-coder:7b
2. prompt v3b, qwen2.5-coder:14b (primary)
3. prompt v3a, qwen2.5-coder:7b (primary)
4. prompt v3a, qwen2.5-coder:14b (exploratory)
5. prompt v3b, qwen2.5-coder:7b (exploratory)
The test is run once. If a run crashes it may be repeated only into a new folder with the same settings, and the crash must be written down. No other runs, no tuning, no edits after seeing results.
