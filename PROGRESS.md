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
