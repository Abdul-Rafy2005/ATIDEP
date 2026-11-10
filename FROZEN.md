# ATIDEP Frozen Configuration

Date: 2026-11-06

## Selected Models and Prompts

- Primary model: qwen2.5-coder:7b
  - Chosen prompt: v2
  - Quantization: Q4_K_M
  - Selection rationale: In the complete temperature 0.2, 3-repeat set 1 evaluation, qwen2.5-coder:7b scored 36/36 first-try strict passes under both prompt v2 and v2_1 with 0 syntax errors. Following the fixed tie-breaker rule (prefer v2), prompt v2 is selected. qwen2.5-coder:7b achieved 36/36 first-try strict passes, tying with qwen2.5-coder:14b, and is chosen as the primary model by the tie-breaker rule (faster execution).
- Comparison model: qwen2.5-coder:14b
  - Chosen prompt: v2_1
  - Quantization: Q4_K_M
  - Selection rationale: In the complete temperature 0.2, 3-repeat set 1 evaluation, qwen2.5-coder:14b scored 36/36 first-try strict passes under prompt v2_1 (0 syntax errors) versus 26/36 under prompt v2 (10 syntax errors). Following the fixed rule (higher first-try strict pass), prompt v2_1 is selected.

The final evaluation on test set 3 compares prompt v1 with the frozen prompt for each model (v1 vs v2 for qwen2.5-coder:7b; v1 vs v2_1 for qwen2.5-coder:14b).

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
set 3 file updated after review on 2026-11-10, reason: fairness fixes before lock
| llm/analyze_results.py | a314792406b02524194d7f1e78fb338c4305493241af19df679f72bd01c2df20 |
| llm/run_experiment.py | 7baaea439b6eb89ea2313ebcfeef1af8aa4b79e734796e79458de1bf540005a9 |
