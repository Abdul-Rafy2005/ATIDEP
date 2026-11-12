# ATIDEP Progress Log

Antigravity started on 2026-11-06

## Differences between old Copilot notes (.github/copilot-instructions.md) and repository state
1. Team: Old text lists three team members (Abdul Rafy, Muhammad Owais, Abdul Ahad). Current project memory notes that only Abdul Rafy works on this codebase.
2. Code map: Old text omits several scripts and folders created during later development:
   - `llm/`: Contains additional scripts (`analyze_results.py`, `build_results_summary.py`, `compare_prompt_runs.py`, `diagnose_run.py`, `inspect_failures.py`, `probe_modifiers.py`, `rescore_archive.py`, `run_experiment.py`, `variance_report.py`).
   - `llm/prompts/`: Contains `v1.py` and `v2.py` (old code map did not list prompt modularisation). `v2_1.py` mentioned in the new text does not yet exist.
   - `tests/`: Directory exists with five test scripts (`test_analyze_results.py`, `test_diagnose_run.py`, `test_prompts.py`, `test_runner_options.py`, `test_strict_gate_sanity.py`), not listed in the old code map.
   - `validator/`: Contains `test_set1_variants.py`, not listed in the old code map.
   - `coverage/`: Directory exists at root (empty).
   - `results/`: Contains `RESULTS_SUMMARY.md`, `run_log.csv`, `variance_set1_v1_vs_v2.md`, `probe_modifiers.md`, `prompt_v1_vs_v2_set1.md`, and subdirectories under `results/runs/`.
3. Results: Old text initially describes single temperature 0 runs (Set 1: 10/12 for 7b, 11/12 for 14b). Later runs logged in `results/RESULTS_SUMMARY.md` and run directories reflect variance runs with temperature 0.2, 3 repeats, 36 rules per row.

## Task Log

### 2026-11-06: Task 0 - Set up project memory
- Status: DONE
- Files created or changed:
  - AGENTS.md (created)
  - PROGRESS.md (created)
  - .agent/rules/atidep.md (created)
- WARN lines: none

### 2026-11-06: Task 1 - Preflight, fixes and prompt v2.1
- Status: DONE
- Files created or changed:
  - results/runs/20261021_1534_set1_v2/INVALID_PARTIAL.txt (created)
  - results/runs/20261021_1536_set1_v2/INVALID_PARTIAL.txt (created)
  - llm/build_results_summary.py (fixed repeat filename resolution and final pass metric)
  - results/RESULTS_SUMMARY.md (regenerated with corrected metrics)
  - llm/run_experiment.py (repair hint updated for "Unsupported type", added prompt v2_1 support)
  - tests/test_runner_options.py (updated repair hint test, added test_prompt_v2_1_accepted)
  - llm/prompts/v2_1.py (created prompt v2.1, frozen)
  - tests/test_prompt_v2_1.py (created prompt v2.1 test suite)
- WARN lines: none

### 2026-11-06: Task 2 - Experiments A and B
- Status: DONE
- Files created or changed:
  - results/runs/20261106_1338_set1_v2/ (Run A folder)
  - results/runs/20261106_1344_set1_v2_1/ (Run B folder)
  - results/prompt_v2_vs_v2_1_set1.md (created comparison document)
  - llm/build_results_summary.py (added Run A and Run B to RUNS list)
  - results/RESULTS_SUMMARY.md (regenerated with Run A and Run B results)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-06: Task 3 - Build test set 3
- Status: DONE
- Files created or changed:
  - generator/techniques_set3.py (created)
  - download_rules_set3.py (created)
  - data/sigmahq_rules_set3/ (created, 20 rule files)
  - results/techniques_set3.csv (created)
  - validator/test_set3_real_rules.py (created)
  - tests/test_set3_sanity.py (created)
  - llm/run_experiment.py (updated with set 3 support and strict guard)
  - llm/analyze_results.py (updated with set 3 support)
  - tests/test_set3_guard.py (created)
  - SET3_REVIEW.md (created)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-06: Task 4 - Freeze the configuration
- Status: DONE
- Files created or changed:
  - FROZEN.md (created)
  - tools/check_frozen.py (created)
  - tests/test_check_frozen.py (created)
  - tools/lock_set3.py (created, not executed)
  - tests/test_set3_guard.py (updated test_guard_refuses_when_frozen_missing)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-06: Task 5 - ATT&CK coverage template
- Status: DONE
- Files created or changed:
  - coverage/build_coverage.py (created)
  - coverage/coverage.csv (generated)
  - coverage/coverage.html (generated)
  - coverage/README.md (created)
  - tests/test_coverage.py (created)
  - PROGRESS.md (updated)
- WARN lines: none


### 2026-11-06: Task 6 - End-to-end demo
- Status: DONE
- Files created or changed:
  - demo/demo.py (created)
  - demo/__init__.py (created)
  - demo/samples/sample1.txt (created)
  - demo/samples/sample2.txt (created)
  - demo/samples/sample3.txt (created)
  - demo/samples/sample4.txt (created)
  - demo/output/ (generated, 8 json + 8 yml)
  - tests/test_demo.py (created)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-10: Task 3b - Fix Set 3 after review, and tidy
- Status: DONE
- Files created or changed:
  - results/archive/set3_before_review/ (created archive of techniques_set3.py, download_rules_set3.py, SET3_REVIEW.md, techniques_set3.csv)
  - download_rules_set3.py (replaced T1036 and T1127 with T1563.002 and T1218)
  - data/sigmahq_rules_set3/proc_creation_win_mstsc_rdp_hijack_shadowing.yml (added)
  - data/sigmahq_rules_set3/proc_creation_win_dsacls_password_spray.yml (added)
  - results/techniques_set3.csv (regenerated)
  - generator/techniques_set3.py (updated techniques, added variant_image support to make_triple3, 12 values / 8 order_or_prefix)
  - SET3_REVIEW.md (regenerated with review reasons for all 9 modified techniques)
  - FROZEN.md (updated techniques_set3.py sha256 hash, added review update note, added Q4_K_M quantizations from ollama show)
  - llm/build_results_summary.py (added final strict pass after repair column, renamed single gate column, updated superseded row)
  - results/RESULTS_SUMMARY.md (regenerated with 13 columns)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-10: Task 3c: fix strict gate in run pipeline, rescore, and redo freeze decision
- Status: DONE
- Files created or changed:
  - llm/scoring.py (created unified scoring module with score_rule supporting sets 1, 2, and 3)
  - llm/run_experiment.py (routed single_score, result_row, and repairs through score_rule; added --results-dir)
  - llm/analyze_results.py (routed analyze_rule through score_rule for all sets)
  - llm/compare_set2.py (encapsulated global state mutation in point_at_set2)
  - llm/build_results_summary.py (updated columns to standard format, scored rules directly from disk using score_rule)
  - tools/rescore_all.py (created rescore utility)
  - results/rescore_strict_all.md (created full rescore report for complete runs and archives with regression assertions)
  - results/archive/RESULTS_SUMMARY_before_task3c.md (archived previous summary)
  - results/RESULTS_SUMMARY.md (regenerated with true strict gate numbers and updated footnote)
  - FROZEN.md (redone freeze decision to prompt v2_1 for both models; updated hashes for run_experiment.py, analyze_results.py, and added scoring.py)
  - AGENTS.md (updated set 1 numbers with true strict numbers, added working rule 8, recorded known bug fixed)
  - tests/test_scoring_pipeline.py (created pipeline test suite covering sets 1, 2, and 3 with mocked Ollama and isolated results dir)
  - tests/test_demo.py (updated test_read_frozen_config to expect prompt v2_1)
  - tests/test_prompts.py (isolated global state mutation during set 2 test)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-10: Task 3d - Set 1 failure analysis
- Status: DONE
- Files created or changed:
  - llm/analyze_failure_modes.py (created: extracts line differences, finds blocking conditions, classifies failure modes)
  - results/set1_strict_summary.md (created: strict summary tables and technique breakdown across all complete set 1 evaluations)
  - results/set1_failure_modes.md (created: 3 sections covering technique changes, classification tables, and extra observations)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-11: Task 3e - Prompt round 3 on set 1, failure analysis, and freeze update
- Status: DONE
- Files created or changed:
  - results/set1_v2_1_failure_examples.md (created: repeat 1 detection blocks, marked blockers, shown and variant lines for 6 techniques)
  - llm/prompts/v3a.py (created: minimal concise instructions with 2 examples)
  - llm/prompts/v3b.py (created: chain-of-thought instructions with keep/ignore scratchpad comments)
  - tests/test_prompts_v3.py (created: unit tests for v3 prompts covering all 3 sets, pySigma validity, quietness, sensitive values, program names, diff)
  - llm/run_experiment.py (updated to accept --prompt v3a and --prompt v3b, save raw responses to rules_raw)
  - tests/test_runner_options.py (updated: added test_prompts_v3a_v3b_accepted)
  - results/runs/20261111_1403_set1_v3a/ (created: run outputs for prompt v3a on set 1)
  - results/runs/20261111_1413_set1_v3b/ (created: run outputs for prompt v3b on set 1)
  - llm/analyze_failure_modes.py (updated to include v3a and v3b in failure mode analysis)
  - results/set1_strict_summary.md (regenerated with v3a and v3b strict metrics)
  - results/set1_failure_modes.md (regenerated with v3a and v3b failure mode breakdowns)
  - results/set1_prompt_round3.md (created: comprehensive comparison across prompt versions v1, v2, v2_1, v3a, v3b)
  - FROZEN.md (updated: freeze decision to qwen2.5-coder:14b under v3b as primary model and qwen2.5-coder:7b under v3a as comparison model; added v3a.py and v3b.py hashes)
  - AGENTS.md (updated: added dated prompt round 3 results and closing statement for set 1 tuning)
  - tests/test_demo.py (updated: test_read_frozen_config updated for new primary model and prompt)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-11: Task 7 - Final test on Set 3
- Status: DONE
- Files created or changed:
  - SET3_LOCK.md (generated by tools/lock_set3.py)
  - FROZEN.md (appended pre-registration section before runs)
  - results/set3_use_log.csv (logged the 5 executed runs)
  - results/runs/20261111_1449_set3_v1/ (Run 1: baseline prompt v1 for 14b and 7b)
  - results/runs/20261111_1500_set3_v3b/ (Run 2: 14b primary under prompt v3b)
  - results/runs/20261111_1507_set3_v3a/ (Run 3: 7b primary under prompt v3a)
  - results/runs/20261111_1512_set3_v3a/ (Run 4: 14b exploratory under prompt v3a)
  - results/runs/20261111_1518_set3_v3b/ (Run 5: 7b exploratory under prompt v3b)
  - llm/analyze_failure_modes_set3.py (created: Set 3 failure mode analysis and report generator)
  - results/FINAL_set3_report.md (created: comprehensive evaluation report for Set 3)
  - coverage/coverage.csv, coverage/coverage.html, coverage/README.md (updated via build_coverage.py)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-11: Task 8 - FYP-1 final testing report, demo script, and documentation
- Status: DONE
- Files created or changed:
  - docs/FYP1_LLM_testing_report.md (created: full FYP-1 testing report covering goals, setup, results across sets 1, 2, and 3, findings, trade-offs, limitations, and reproduction steps)
  - docs/DEMO_SCRIPT.md (created: 5-minute live demonstration plan with exact commands and presenter talking points)
  - README.md (updated: 3-line project summary, installation, demo instructions, test instructions, and complete folder map)
  - tests/test_coverage.py (updated: asserted coverage row consistency across dynamic set 3 runs)
  - tests/test_scoring_pipeline.py (updated: preserved set3_use_log.csv mtime during pipeline tests)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-12: Task 9 - Fix the ATT&CK coverage grid
- Status: DONE
- Files created or changed:
  - coverage/build_coverage.py (updated: scores rules directly from rules_first and archive using score_rule, never reads stored strict_pass flag, loads Set 2 baseline from archive, dynamically formats header, maps multi-tactic tags)
  - coverage/coverage.csv (regenerated with true strict pass verdicts and Set 2 baseline columns)
  - coverage/coverage.html (regenerated with dynamic header, true strict numbers, and Set 2 baseline)
  - coverage/COVERAGE.md (created: detailed coverage metrics, covered techniques breakdown, never-covered list, and configuration totals)
  - coverage/README.md (updated with coverage definition, summary metrics, and never-covered list)
  - tests/test_coverage.py (updated with assertions for strict totals, Set 2 baseline numbers, dynamic header, no all-NOT_TESTED rows, and multi-tactic formatting)
  - PROGRESS.md (updated)
- WARN lines: none
