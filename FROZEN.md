# ATIDEP Frozen Configuration

Date: 2026-11-10 (originally frozen 2026-11-06; decision redone 2026-11-10 following strict gate fix)

## Selected Models and Prompts

### Selection Decision Table (Set 1, Temperature 0.2, Repeats 3)

| Model | Prompt Candidate | First-try Strict Pass | First-try Syntax Errors | First-try Single Pass | Chosen |
| --- | --- | ---: | ---: | ---: | --- |
| qwen2.5-coder:7b | v2 (run 20261104_1503) | 9/36 | 0 | 36/36 | No |
| qwen2.5-coder:7b | v2_1 (run 20261106_1344) | 11/36 | 0 | 36/36 | **Yes** (higher strict pass: 11 > 9) |
| qwen2.5-coder:14b | v2 (run 20261104_1503) | 8/36 | 10 | 26/36 | No |
| qwen2.5-coder:14b | v2_1 (run 20261106_1344) | 8/36 | 0 | 36/36 | **Yes** (tie on strict pass 8 vs 8; fewer syntax errors: 0 < 10) |

Primary model choice:
- qwen2.5-coder:7b under chosen prompt v2_1: 11/36 first-try strict pass.
- qwen2.5-coder:14b under chosen prompt v2_1: 8/36 first-try strict pass.
- Selection: qwen2.5-coder:7b is selected as primary model (higher first-try strict pass: 11 > 8).

### Frozen Configuration

- Primary model: qwen2.5-coder:7b
  - Chosen prompt: v2_1
  - Quantization: Q4_K_M
  - Selection rationale: In the complete temperature 0.2, 3-repeat set 1 evaluation under the true strict gate, qwen2.5-coder:7b scored 11/36 first-try strict passes under prompt v2_1 versus 9/36 under prompt v2 (both 0 syntax errors). Under v2, rules overfit to the shown command line and fail the hidden variant (TOO_NARROW). Prompt v2_1 provides explicit guidance against overfitting, resulting in higher generalisation. qwen2.5-coder:7b achieved 11/36 strict passes compared to 8/36 for qwen2.5-coder:14b, so it is selected as the primary model.
- Comparison model: qwen2.5-coder:14b
  - Chosen prompt: v2_1
  - Quantization: Q4_K_M
  - Selection rationale: In the complete temperature 0.2, 3-repeat set 1 evaluation, qwen2.5-coder:14b tied on first-try strict passes (8/36 on both v2 and v2_1), but prompt v2_1 completely eliminated first-try syntax errors (0 under v2_1 versus 10 under v2). Following the fixed tie-breaker rule (fewer syntax errors), prompt v2_1 is selected.

The final evaluation on test set 3 compares prompt v1 with the frozen prompt for each model (v1 vs v2_1 for qwen2.5-coder:7b; v1 vs v2_1 for qwen2.5-coder:14b).

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
| validator/runner.py | e9aa0bf6189b57f0a99319e60c3dddeb0663bc1b3d9a1b6a75193b160f97f54f |
| generator/generate.py | 2dce9a88ebbb79187ed558c3e9ffd0cf8170733ff7dcce2376e20468b00f8700 |
| generator/techniques_set2.py | 8577581a4d9d1e3524d1bae28e850f26e23f714f7ef8c5d4c101979044b74acf |
| generator/techniques_set3.py | c86d7307e124309f0824e3dd844673d381f0275cdd333ec6d57dabdb575179f8 |
| llm/analyze_results.py | d0627fdb2870beb7152607f0a1a60fd91e1b393fe845b0356c1ac41e4598c2e3 |
| llm/run_experiment.py | db4cb085de96804cb56f346b0fb405e394a217a7437411c8b8ee1598031a1241 |
| llm/scoring.py | 193c272d45fa23c6f5daf5f50bfbfcdeeb89b896f99425e42a358685b336385c |

## Superseded decision (used single-gate numbers by mistake)

On 2026-11-06, qwen2.5-coder:7b was assigned prompt v2 under the assumption that both v2 and v2_1 scored 36/36 first-try strict passes on set 1, triggering the tie-breaker to pick v2. However, the pipeline at that time evaluated only the single gate for set 1 (checking shown line and benign line, but omitting the hidden variant). Under the true strict gate checking the hidden variant, prompt v2 scores only 9/36 while prompt v2_1 scores 11/36. Thus, prompt v2_1 is selected for qwen2.5-coder:7b without needing a tie-breaker.
