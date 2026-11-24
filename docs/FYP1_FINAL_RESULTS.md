# ATIDEP FYP-1 Final Results

Date: 2026-11-24
Project: Automated Threat-Informed Detection Engineering Platform (ATIDEP)
Supervisor: Dr. Shahbaz Siddiqui
Team: Abdul Rafy, Muhammad Owais, Abdul Ahad

This document collects the final numbers, tables, and analysis for the FYP-1 report. All results were produced on the frozen configurations registered in FROZEN.md before any Set 3 run.

---

## 1. Environment

- Hardware: Dell Precision 3680, Intel Core i7-14700, 32 GB RAM, NVIDIA RTX 4000 Ada 20 GB VRAM
- OS: Windows 11 Pro, Python 3.13, PowerShell
- LLM runtime: Ollama 0.40.7 (local, no cloud APIs)
- Libraries: pySigma, pysigma-backend-sqlite, PyYAML, Flask

## 2. Models

| Model | Parameters | Quantisation | Size | Role |
|---|---|---|---|---|
| qwen2.5-coder:14b | 14B | Q4_K_M | 9.0 GB | Primary |
| qwen2.5-coder:7b | 7B | Q4_K_M | 4.7 GB | Comparison |
| mistral-rules | 7B | Q8_0 | 7.7 GB | Dropped (prompt v1 baseline only) |
| mistral:7b | 7B | Q4_K_M | 4.4 GB | Dropped (syntax errors) |

## 3. Test Sets

| Set | Techniques | Purpose | Status |
|---|---|---|---|
| Set 1 | 12 | Development and prompt tuning | Closed for tuning after round 3 |
| Set 2 | 12 | Baseline validation (prompt v1 only) | Locked, never re-run |
| Set 3 | 20 | Final clean test | Pre-registered, run once |

Total: 44 MITRE ATT&CK techniques, all Windows process creation (Sysmon Event ID 1).

## 4. Validation Gate

The gate evaluates each LLM-generated Sigma rule against three synthetic events per technique:
- **Shown event**: the attack command line given to the model in the prompt.
- **Variant event**: a hidden attack command line with altered values, flag order, or prefix.
- **Benign event**: a harmless near-miss execution of the same program.

Verdicts (first match):
1. SYNTAX_ERROR: pySigma cannot convert the rule to SQL.
2. MISSED_SHOWN: rule does not fire on the shown attack line.
3. NOISY: rule fires on the harmless benign line.
4. TOO_NARROW: rule fires on shown line but misses the hidden variant.
5. PASS: rule passes all four checks.

The strict gate (requiring the hidden variant) is the primary metric. A single gate (without the variant check) is reported for comparison.

## 5. Prompt Versions

| Prompt | Description | Frozen For |
|---|---|---|
| v1 | Baseline: technique ID, description, process path, one command line, two few-shot examples | Baseline comparison |
| v2 | Added explicit rules against copying specific values | Superseded |
| v2_1 | Corrected windash syntax instructions | Superseded |
| v3a | Concise prompt: single keyword/flag focus, token budget | qwen2.5-coder:7b |
| v3b | Chain-of-thought scratchpad (# keep: / # ignore: comments before YAML) | qwen2.5-coder:14b |

All prompts are frozen in llm/prompts/ with SHA-256 hashes in FROZEN.md.

## 6. Headline Results: Set 3 Final Test

Temperature 0.2, 3 repeats per technique, seed 100, N=60 rules per configuration. Run once, no post-hoc tuning.

| Configuration | Role | Strict Pass (/60) | Strict % | Techniques (>=2/3) | Syntax Errors | TOO_NARROW | Avg Sec/Rule |
|---|---|---|---|---|---|---|---|
| 14b v3b | **Primary** | **57/60** | **95.0%** | **19/20** | 0 | 3 | 6.27s |
| 7b v3a | **Comparison** | **58/60** | **96.7%** | **20/20** | 1 | 1 | 4.08s |
| 14b v1 | Baseline | 47/60 | 78.3% | 16/20 | 0 | 7 | 5.12s |
| 7b v1 | Baseline | 35/60 | 58.3% | 11/20 | 1 | 21 | 3.69s |
| 14b v3a | Exploratory | 55/60 | 91.7% | 18/20 | 0 | 3 | 5.72s |
| 7b v3b | Exploratory | 54/60 | 90.0% | 18/20 | 0 | 5 | 4.37s |

## 7. Improvement from Prompt Engineering

| Model | Baseline (v1) | Frozen Prompt | Absolute Gain | Relative Gain |
|---|---|---|---|---|
| qwen2.5-coder:14b | 47/60 (78.3%) | 57/60 (95.0%) | +10 rules | +21.3% |
| qwen2.5-coder:7b | 35/60 (58.3%) | 58/60 (96.7%) | +23 rules | +65.7% |

Paired technique shifts (improved / same / worse):
- 14b (v1 to v3b): 4 improved, 16 same, 0 worse.
- 7b (v1 to v3a): 9 improved, 11 same, 0 worse.

No technique got worse under the improved prompts.

## 8. The Gate Effect: Why One Log Is Not Enough

A gate that checks only the shown attack log and a benign log lets narrow rules through. The strict gate catches them.

| Configuration | Single Pass (/60) | Strict Pass (/60) | Rules Approved by Single but Failed Strict | Failure Share |
|---|---|---|---|---|
| 7b v1 (baseline) | 56 | 35 | 21 | **37.5%** |
| 14b v1 (baseline) | 54 | 47 | 7 | 13.0% |
| 7b v3a (primary) | 59 | 58 | 1 | 1.7% |
| 14b v3b (primary) | 60 | 57 | 3 | 5.0% |

Under the baseline prompt, more than one in three rules approved by a single-log gate for the 7b model were actually broken (would miss hidden attack variants). The improved prompts reduced this gap to under 5%.

This is the evidence for RQ2: automated validation on hidden variants catches narrow rules that a single-log test would miss.

## 9. Set 2 Baseline (Prompt v1, Temperature 0, 1 Repeat)

| Model | Single Pass (/12) | Strict Pass (/12) | TOO_NARROW |
|---|---|---|---|
| qwen2.5-coder:7b | 10/12 | 2/12 | 8 |
| qwen2.5-coder:14b | 9/12 | 2/12 | 7 |
| mistral-rules | 6/12 | 0/12 | 6 |

Set 2 showed that prompt v1 rules massively overfit: 8 of 10 single-pass rules for 7b were actually too narrow to catch variants. This motivated the prompt engineering work.

## 10. Prompt Tuning Progression on Set 1

Set 1 (12 techniques, temperature 0.2, 3 repeats, N=36).

| Model | Prompt | Strict Pass (/36) | Syntax Errors | TOO_NARROW | NOISY |
|---|---|---|---|---|---|
| 7b | v1 | 7/36 | 8 | 21 | 0 |
| 14b | v1 | 3/36 | 0 | 32 | 0 |
| 7b | v2 | 9/36 | 0 | 27 | 0 |
| 14b | v2 | 8/36 | 10 | 18 | 0 |
| 7b | v2_1 | 11/36 | 0 | 25 | 0 |
| 14b | v2_1 | 8/36 | 0 | 28 | 0 |
| 7b | **v3a** | **16/36** | 0 | 20 | 0 |
| 14b | v3a | 19/36 | 0 | 16 | 1 |
| 7b | v3b | 15/36 | 0 | 13 | 8 |
| 14b | **v3b** | **21/36** | 0 | 9 | 6 |

Observations:
- Strict pass improved from 7 to 16 (7b) and from 3 to 21 (14b) across four prompt rounds.
- TOO_NARROW decreased from 21 to 20 (7b) and from 32 to 9 (14b).
- v3b introduced a narrow-vs-noisy trade-off: fewer TOO_NARROW but more NOISY.
- Set 1 is a development set and these numbers are practice scores, not accuracy claims.

## 11. ATT&CK Coverage

| Metric | Value |
|---|---|
| Total techniques in catalog | 44 |
| Techniques covered (any configuration passes all repeats) | 29/44 (65.9%) |
| Sets 1 and 3 combined (development + final test) | 27/32 (84.4%) |
| Set 3 alone (clean final test, frozen 14b v3b) | 19/20 (95.0%) |
| Set 2 baseline (prompt v1 only, never re-tested) | 2/12 (16.7%) |

Frozen configuration coverage:
- 14b v3b on Set 3: 19/20 (95.0%)
- 14b v3b on Set 1: 7/12 (58.3%)
- 7b v3a on Set 3: 18/20 (90.0%)
- 7b v3a on Set 1: 5/12 (41.7%)

## 12. Known Limitations

1. Only Windows process creation logs (Sysmon Event ID 1) are covered.
2. Synthetic logs are hand-written templates, not generated from real malware execution.
3. Each technique has one benign near-miss line, so noise detection is likely underestimated.
4. No obfuscation, encoding, or renamed binary variants are tested.
5. Set 3 was designed to be fair and is easier than Sets 1 and 2, so absolute scores are not comparable across sets.
6. Public-data contamination is possible since model training corpora may include SigmaHQ rules.
7. The 7b and 14b models are not distinguishable on Set 3 (58 vs 57 of 60), and 7b is faster (4.08s vs 6.27s per rule).
8. T1529 (System Shutdown/Reboot) is a known flaw: the description says "immediate reboot" but the variant uses /t 30, penalising correct rules. Excluding T1529, the 14b primary achieves 57/57 (100%).

## 13. What We Cannot Claim

- These rules detect real-world malware or sophisticated attacks.
- These rules are deployable directly into production enterprise SIEMs without further tuning.
- The evaluation covers network, registry, memory, or multi-stage correlation rules.

## 14. Answers to Research Questions

**RQ1: Can a local LLM write syntactically valid and effective Sigma rules from a single attack example?**

Yes, with appropriate prompt engineering. On the final clean test (Set 3), both models produced rules with near-zero syntax errors (0-1 of 60) and 95-97% strict pass rates. Without prompt engineering (baseline v1), the same models achieved only 58-78% strict pass rates.

**RQ2: Does automated validation on synthetic logs reduce the number of broken and overly narrow rules marked ready for deployment?**

Yes. Under the baseline prompt, a single-log gate would have approved 56 of 60 rules for the 7b model, but 21 of those (37.5%) failed on hidden variants. The strict gate with hidden variants caught these narrow rules. Even with improved prompts, the strict gate still caught 1-3 additional narrow rules per configuration that a single-log test would have missed.

## 15. Test Suite

- 99 pytest tests in tests/ (all pass)
- 51 validator checks across 4 scripts (all pass)
- Frozen file hash verification via tools/check_frozen.py

## 16. Deliverable Status

| Deliverable | Status | Evidence |
|---|---|---|
| 1. Prototype | Complete | End-to-end pipeline: threat text in, Sigma rule out, gate verdict. Web dashboard with 5 views. |
| 2. ATT&CK Coverage Template | Complete | coverage.csv, coverage.html, COVERAGE.md across 44 techniques with official ATT&CK names. |
| 3. LLM Testing | Complete | 16 experiment runs, 360 Set 3 evaluations, full report in docs/FYP1_LLM_testing_report.md. |
