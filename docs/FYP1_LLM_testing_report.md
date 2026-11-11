# ATIDEP FYP-1 LLM Testing Report

Date: 2026-11-11
Project: Automated Threat-Informed Detection Engineering Platform (ATIDEP)
Supervisor: Dr. Shahbaz Siddiqui
Team: Abdul Rafy, Muhammad Owais, Abdul Ahad

---

## 1. Goal

The goal of this work is to evaluate whether local large language models (LLMs) running on consumer workstation hardware can generate valid Sigma detection rules from threat reports, and whether automated validation testing (the validation gate) prevents narrow or broken rules from entering a repository.

This report addresses two final year project research questions:
- RQ1: Can a local LLM write syntactically valid and effective Sigma rules from a single attack example?
- RQ2: Does automated validation on synthetic logs reduce the number of broken and overly narrow rules marked ready for deployment?

---

## 2. Setup

### 2.1 Hardware and Environment
- Workstation: Dell Precision 3680
- CPU: Intel Core i7-14700
- RAM: 32 GB
- GPU: NVIDIA RTX 4000 Ada Generation (20 GB VRAM)
- Operating System: Windows 11 Pro, PowerShell, Python 3.13
- LLM Runtime: Ollama version 0.40.7 (local HTTP API at `http://localhost:11434`)
- Core Libraries: pySigma, pysigma-backend-sqlite, PyYAML. No external cloud APIs are used.

### 2.2 Models and Quantisations
- `qwen2.5-coder:14b`: Q4_K_M quantisation, 9.0 GB, primary model.
- `qwen2.5-coder:7b`: Q4_K_M quantisation, 4.7 GB, comparison model.
- `mistral:7b`: Q4_K_M quantisation, 4.4 GB (evaluated in prompt v1 baseline, dropped due to syntax errors).
- `mistral-rules:latest`: jcordon5/Mistral-7B-cybersecurity-rules converted to GGUF Q8_0, 7.7 GB (evaluated in prompt v1 baseline, dropped due to prompt following issues).

### 2.3 Test Sets
- Set 1 (Development and Tuning Set): 12 MITRE ATT&CK techniques in `generator/generate.py`. Used for prompt iteration, error analysis, and tuning.
- Set 2 (Validation Baseline Set): 12 MITRE ATT&CK techniques in `generator/techniques_set2.py`. Evaluated once with prompt v1 as a baseline, then locked against prompt tuning.
- Set 3 (Final Locked Test Set): 20 fresh MITRE ATT&CK techniques in `generator/techniques_set3.py`. Locked into `SET3_LOCK.md`, pre-registered in `FROZEN.md`, and evaluated exactly once in Task 7.

### 2.4 The Validation Gate
Events are flat dictionaries following Windows Sysmon Event ID 1 process creation: `Image`, `CommandLine`, `ParentImage`, `ParentCommandLine`, `OriginalFileName`, `User`, `IntegrityLevel`, `Description`, `Product`, `Company`.

The validation gate evaluates each generated rule against three synthetic events:
1. Shown event: the exact attack command line shown to the model.
2. Variant event: a hidden attack command line of the same attack with altered details (different values, flag order, or prefix).
3. Benign event: a harmless near-miss execution of the same program.

Gate definitions:
- Syntax: pySigma successfully converts the Sigma rule into SQLite SQL queries.
- Single gate pass: syntax is valid, the rule fires on the shown malicious line, and the rule does not fire on the benign line.
- Strict gate pass: single gate pass and the rule also fires on the hidden variant line.
- Quiet: the rule does not fire on the harmless near-miss line.
- Verdicts (first match wins):
  - `SYNTAX_ERROR`: rule fails pySigma SQL conversion.
  - `MISSED_SHOWN`: rule does not fire on the shown attack line.
  - `NOISY`: rule fires on the harmless benign line.
  - `TOO_NARROW`: rule fires on shown line but misses the hidden variant.
  - `PASS`: rule passes the strict gate.

### 2.5 Prompts and Frozen Hashes
Prompts are recorded in `FROZEN.md` with their SHA-256 hashes:
- `v1` (`llm/prompts/v1.py`): SHA-256 `5fef6e6082f7f96920d48fab97cb8ee9d8c23b5e077c381dbccae71b67d54829`. Baseline prompt with two few-shot examples (T1016 and T1564.001).
- `v2` (`llm/prompts/v2.py`): SHA-256 `ae6231f8dd8cc67c7b574a573d6b4812ffbd0efad7864537080de3199be6f5d3`. Added explicit rules against specific values.
- `v2_1` (`llm/prompts/v2_1.py`): SHA-256 `bd19f52f5824f744286ccd9035e7ccc77337bf6cd4efc9abaffb753fea7761d4`. Corrected windash syntax instructions.
- `v3a` (`llm/prompts/v3a.py`): SHA-256 `4c8dbea167dc690b5c77226c42d5ac518b843183bfd655fd401b0f5c776e62d0`. Concise prompt enforcing a single keyword or flag and a token budget. Chosen for `qwen2.5-coder:7b`.
- `v3b` (`llm/prompts/v3b.py`): SHA-256 `cba7e60ab7d9075727e4841e1fd51ee09739d683bb1078af67378770540c746d`. Chain-of-thought scratchpad prompting (`# keep:` and `# ignore:` comments before YAML). Chosen for `qwen2.5-coder:14b`.

---

## 3. Results on Development and Baseline Sets

### 3.1 Set 2 Baseline Evaluation (Prompt v1, Temperature 0, 1 Repeat, N=12)
Source file: `results/analysis_set2_20261021_1452.md`

| Model | Syntax Errors | Single Pass (/12) | Strict Pass (/12) | MISSED_SHOWN | TOO_NARROW | NOISY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen2.5-coder:7b` | 1 | 10/12 | 2/12 | 1 | 8 | 0 |
| `qwen2.5-coder:14b` | 0 | 9/12 | 2/12 | 3 | 7 | 0 |
| `mistral-rules` | 0 | 6/12 | 0/12 | 6 | 6 | 0 |

On Set 2 under prompt v1, single-gate validation approved 10 and 9 rules for Qwen models. The strict gate revealed that 8 and 7 of those rules were `TOO_NARROW`, failing on the hidden variant. Both Qwen models passed only the same two techniques (T1546.007 and T1485) where variants differed only by path arguments. `mistral-rules` scored 0 of 12 strict passes.

### 3.2 Set 1 Variance and Tuning Rounds (Temperature 0.2, 3 Repeats, N=36)
Source files: `results/set1_strict_summary.md`, `results/set1_prompt_round3.md`

| Model | Prompt | Run ID | Syntax Errors | Single Pass | Strict Pass (/36) | Strict Pass (/30) | MISSED_SHOWN | NOISY | TOO_NARROW | Avg Sec/Rule |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen2.5-coder:7b` | v1 | `20261021_1528_set1_v1` | 8 | 28/36 | 7/36 | 7/30 | 0 | 0 | 21 | 4.53s |
| `qwen2.5-coder:14b` | v1 | `20261021_1528_set1_v1` | 0 | 35/36 | 3/36 | 3/30 | 1 | 0 | 32 | 5.36s |
| `qwen2.5-coder:7b` | v2 | `20261104_1503_set1_v2` | 0 | 36/36 | 9/36 | 9/30 | 0 | 0 | 27 | 4.16s |
| `qwen2.5-coder:14b` | v2 | `20261104_1503_set1_v2` | 10 | 26/36 | 8/36 | 8/30 | 0 | 0 | 18 | 9.87s |
| `qwen2.5-coder:7b` | v2_1 | `20261106_1344_set1_v2_1` | 0 | 36/36 | 11/36 | 11/30 | 0 | 0 | 25 | 3.74s |
| `qwen2.5-coder:14b` | v2_1 | `20261106_1344_set1_v2_1` | 0 | 36/36 | 8/36 | 8/30 | 0 | 0 | 28 | 5.25s |
| `qwen2.5-coder:7b` | **v3a** | `20261111_1403_set1_v3a` | 0 | 36/36 | **16/36** | 16/30 | 0 | 0 | 20 | 4.33s |
| `qwen2.5-coder:14b` | v3a | `20261111_1403_set1_v3a` | 0 | 35/36 | 19/36 | 19/30 | 0 | 1 | 16 | 10.87s |
| `qwen2.5-coder:7b` | v3b | `20261111_1413_set1_v3b` | 0 | 28/36 | 15/36 | 15/30 | 0 | 8 | 13 | 5.04s |
| `qwen2.5-coder:14b` | **v3b** | `20261111_1413_set1_v3b` | 0 | 30/36 | **21/36** | 21/30 | 0 | 6 | 9 | 8.21s |

Set 1 strict pass rates out of 30 exclude `T1136.001` (`net.exe` vs `net1.exe`) and `T1003.001` (`procdump.exe` vs `procdump64.exe`), whose variants require alias knowledge that process creation prompts do not provide.

---

## 4. Final Test on Set 3

Test Set 3 consists of 20 newly added techniques, evaluated under pre-registration in `FROZEN.md` (temperature 0.2, 3 repeats, seed 100, N=60 rules per configuration). The test was executed once across five runs without post-hoc tuning.

Source file: `results/FINAL_set3_report.md`

### 4.1 Headline Pre-Registered Results (First-Try Strict Pass out of 60)

| Configuration | Role | Model | Prompt | Syntax Errors | Single Pass (/60) | Strict Pass (/60) | Strict Pass (%) | MISSED_SHOWN | TOO_NARROW | NOISY | Techniques Passed (>=2/3) | Avg Sec/Rule |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 14B Primary | **PRIMARY** | `qwen2.5-coder:14b` | `v3b` | 0 | 60/60 | **57/60** | **95.0%** | 0 | 3 | 0 | **19/20** | 6.27s |
| 7B Primary | **PRIMARY** | `qwen2.5-coder:7b` | `v3a` | 1 | 59/60 | **58/60** | **96.7%** | 0 | 1 | 0 | **20/20** | 4.08s |
| 14B Baseline | **BASELINE** | `qwen2.5-coder:14b` | `v1` | 0 | 54/60 | **47/60** | **78.3%** | 6 | 7 | 0 | **16/20** | 5.12s |
| 7B Baseline | **BASELINE** | `qwen2.5-coder:7b` | `v1` | 1 | 56/60 | **35/60** | **58.3%** | 3 | 21 | 0 | **11/20** | 3.69s |
| 14B Exploratory | **EXPLORATORY** | `qwen2.5-coder:14b` | `v3a` | 0 | 58/60 | **55/60** | **91.7%** | 2 | 3 | 0 | **18/20** | 5.72s |
| 7B Exploratory | **EXPLORATORY** | `qwen2.5-coder:7b` | `v3b` | 0 | 59/60 | **54/60** | **90.0%** | 1 | 5 | 0 | **18/20** | 4.37s |

### 4.2 Primary Paired Comparison and Exploratory Sign Tests
Comparing each model under its frozen prompt against baseline prompt v1 on the same 20 techniques:

- `qwen2.5-coder:14b` (Primary Model, v1 to v3b):
  - Strict pass count increased from 47/60 to 57/60 (+10 rules, +21.3% relative improvement).
  - Techniques passed (at least 2 of 3 repeats): increased from 16/20 to 19/20 (+3 techniques).
  - Paired technique shifts: 4 improved, 16 same, 0 worse.
  - Exploratory two-sided sign test: p about 0.125.
- `qwen2.5-coder:7b` (Comparison Model, v1 to v3a):
  - Strict pass count increased from 35/60 to 58/60 (+23 rules, +65.7% relative improvement).
  - Techniques passed (at least 2 of 3 repeats): increased from 11/20 to 20/20 (+9 techniques).
  - Paired technique shifts: 9 improved, 11 same, 0 worse.
  - Exploratory two-sided sign test: p about 0.004.

These sign tests are labelled as exploratory statistics because MITRE ATT&CK techniques are not a random sample, and repeats of one technique are not statistically independent.

### 4.3 One-Log Gate Effect
A gate that checks only the shown attack log and a benign log lets narrow rules pass. Comparing single-gate passes with strict-gate passes measures this effect:

| Configuration | Single Pass (/60) | Strict Pass (/60) | Single-Gate Passes Failing Strict Gate | Failure Share |
| --- | ---: | ---: | ---: | ---: |
| 7B Baseline (`v1`) | 56 | 35 | 21 of 56 | 37.5% |
| 14B Baseline (`v1`) | 54 | 47 | 7 of 54 | 13.0% |
| 7B Primary (`v3a`) | 59 | 58 | 1 of 59 | 1.7% |
| 14B Primary (`v3b`) | 60 | 57 | 3 of 60 | 5.0% |
| 14B Exploratory (`v3a`) | 58 | 55 | 3 of 58 | 5.2% |
| 7B Exploratory (`v3b`) | 59 | 54 | 5 of 59 | 8.5% |

Under baseline prompt v1, more than one in three rules approved by a single-log gate for the 7B model failed against a hidden variant. Improved prompting reduced this gap to 1.7% and 5.0%.

### 4.4 Known Flaw in Set 3 and Post-Hoc Sensitivity Table
In Test Set 3, the description for technique `T1529` reads "An attacker restarts the machine immediately using shutdown.exe". The shown line is `shutdown.exe /r /t 0`. The hidden variant line is `shutdown.exe /r /t 30`. Because the description specified immediate reboot, rules that retained `/t 0` were penalised despite correctly matching the description.

All 3 non-passing rules for `qwen2.5-coder:14b` under primary prompt v3b were caused by `T1529`. The table below provides a post-hoc sensitivity check excluding `T1529` across all configurations (out of 57 rules and 19 techniques). This analysis is post-hoc and not pre-registered; the pre-registered table in Section 4.1 remains the headline metric.

| Configuration | Role | Strict Pass (/57) | Strict Pass (%) | Techniques Passed (>=2/3) (/19) |
| --- | --- | ---: | ---: | ---: |
| 14B Primary (`v3b`) | PRIMARY | 57/57 | 100.0% | 19/19 |
| 7B Primary (`v3a`) | PRIMARY | 56/57 | 98.2% | 19/19 |
| 14B Baseline (`v1`) | BASELINE | 47/57 | 82.5% | 16/19 |
| 7B Baseline (`v1`) | BASELINE | 35/57 | 61.4% | 11/19 |
| 14B Exploratory (`v3a`) | EXPLORATORY | 55/57 | 96.5% | 18/19 |
| 7B Exploratory (`v3b`) | EXPLORATORY | 54/57 | 94.7% | 18/19 |

---

## 5. What We Found

1. Prompt v1 rules overfit heavily to individual command lines. Under prompt v1, the strict gate failed 32 of 36 rules for 14B and 21 of 36 for 7B on Set 1, and 21 of 56 single-pass rules for 7B on Set 3. (Files: `results/set1_strict_summary.md`, `results/FINAL_set3_report.md`).
2. There is an inverse trade-off between TOO_NARROW and NOISY failure modes across prompt designs. On Set 1:
   - Prompt v2_1 produced 25 (7B) and 28 (14B) TOO_NARROW rules, with 0 NOISY rules.
   - Prompt v3a produced 20 (7B) and 16 (14B) TOO_NARROW rules, with 0 and 1 NOISY rules.
   - Prompt v3b produced 13 (7B) and 9 (14B) TOO_NARROW rules, but increased NOISY rules to 8 (7B) and 6 (14B).
   Forcing minimal keywords reduces narrowing but increases false alarms on shared programs. (File: `results/set1_prompt_round3.md`).
3. Set 1 was used for tuning, so Set 1 numbers represent practice iterations. Set 3 was locked and evaluated once, making it the only clean test. (Files: `FROZEN.md`, `results/FINAL_set3_report.md`).
4. Repeat variance across identical seeds is largely discrete. Each technique almost always scores 0 of 3 or 3 of 3 passes. On Set 3, 14B v3b had nineteen 3/3 techniques and one 0/3 technique; 7B v3a had eighteen 3/3 techniques and two 2/3 techniques. The effective sample size is primarily the number of techniques rather than individual rule generations. (File: `results/FINAL_set3_report.md`).
5. Identical seeds and prompts yield deterministic results. A repeated run on Set 1 with prompt v2 and temperature 0.2 produced identical results across runs `20261104_1503` and `20261106_1338`. (File: `results/rescore_strict_all.md`).
6. Prompts v3a and v3b were statistically indistinguishable on Set 1 development tests (16 vs 15 for 7B; 19 vs 21 for 14B). The selection of v3b for 14B and v3a for 7B followed a pre-registered decision rule based on highest first-try strict pass. (Files: `FROZEN.md`, `results/set1_prompt_round3.md`).
7. Chain-of-thought formatting in prompt v3b achieved 100% compliance. Across 72 raw responses in Set 1 and 120 in Set 3, both models produced `# keep:` and `# ignore:` comments without generating markdown syntax errors or breaking YAML output. (Files: `results/set1_prompt_round3.md`, `results/FINAL_set3_report.md`).
8. The false-alarm check uses one harmless line per technique with the same program, so noise is likely underestimated compared to diverse production environments. (Files: `generator/generate.py`, `generator/techniques_set3.py`).

---

## 6. Limitations

- Set 3 was built to be fair and is easier than sets 1 and 2, so absolute scores are not comparable across sets.
- The prompt and the gate share the assumption that attackers change values and argument order, and no obfuscation, encoding or renamed programs are tested.
- NOISY is 0 on set 3 but the harmless lines are mostly trivial, while the same v3b prompt gave 6 to 8 noisy rules out of 36 on set 1.
- Public-data contamination is possible because model pre-training corpora may include public SigmaHQ repositories.
- `qwen2.5-coder:7b` (v3a) and `qwen2.5-coder:14b` (v3b) are not distinguishable on set 3 (58 versus 57 of 60) and the 7B model is faster (4.08s versus 6.27s per rule).
- One remaining syntax error observed in 7B was a list-item dictionary formatting mistake, and the repair prompt retry was not used in the final run.

---

## 7. What We Cannot Claim

- We cannot claim that these rules detect real-world malware or sophisticated attacks.
- We cannot claim that these rules are deployable directly into production enterprise SIEMs without further tuning.
- All evaluations are conducted exclusively on harmless synthetic command lines representing Sysmon Event ID 1 process creation logs.
- We do not measure network telemetry, registry persistence, memory injection, file system modifications, or multi-stage correlation rules.

---

## 8. Next Steps (FYP-2)

1. Multi-event false alarm baselines: evaluate each rule against several realistic benign logs, background administrative scripts, and commercial software telemetry.
2. Advanced evasion testing: add obfuscation, string reversal, environment variable expansion, and renamed binary variants.
3. Expanded log coverage: include Windows Event ID 4688, PowerShell script block logs (Event ID 4104), and Sysmon network connections (Event ID 3).
4. Dual-detection pipeline: combine Sigma process creation rules with YARA file rule generation.
5. User interface: build an interactive analyst review dashboard to inspect gate test results, diffs, and SQL translations.

---

## 9. How to Reproduce

### 9.1 Environment Setup
```powershell
# Clone repository and change directory
cd C:\ATIDEP

# Verify Python version (3.13 required)
python --version

# Install dependencies
pip install pySigma pysigma-backend-sqlite pyyaml

# Verify Ollama server is running and models are installed
ollama list
```

### 9.2 Running Unit Tests
```powershell
python -m unittest discover -s tests -p "test_*.py"
python tools/check_frozen.py
```

### 9.3 Running Set 1 Variance Experiments
```powershell
# Prompt v3a on Set 1
python llm/run_experiment.py --set 1 --prompt v3a --models qwen2.5-coder:7b qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100

# Prompt v3b on Set 1
python llm/run_experiment.py --set 1 --prompt v3b --models qwen2.5-coder:7b qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100
```

### 9.4 Running Set 3 Final Test
```powershell
# Verify frozen files
python tools/check_frozen.py

# 1. Baseline prompt v1 (both models)
python llm/run_experiment.py --set 3 --final --reason "final test: v1 baseline both models" --prompt v1 --models qwen2.5-coder:14b qwen2.5-coder:7b --repeats 3 --temperature 0.2 --seed 100

# 2. Primary 14B prompt v3b
python llm/run_experiment.py --set 3 --final --reason "final test: 14b primary v3b" --prompt v3b --models qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100

# 3. Primary 7B prompt v3a
python llm/run_experiment.py --set 3 --final --reason "final test: 7b primary v3a" --prompt v3a --models qwen2.5-coder:7b --repeats 3 --temperature 0.2 --seed 100

# 4. Exploratory 14B prompt v3a
python llm/run_experiment.py --set 3 --final --reason "final test: 14b exploratory v3a" --prompt v3a --models qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100

# 5. Exploratory 7B prompt v3b
python llm/run_experiment.py --set 3 --final --reason "final test: 7b exploratory v3b" --prompt v3b --models qwen2.5-coder:7b --repeats 3 --temperature 0.2 --seed 100
```

### 9.5 Generating Coverage Matrix and Reports
```powershell
python llm/analyze_failure_modes_set3.py
python coverage/build_coverage.py
```

