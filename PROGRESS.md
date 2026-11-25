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

### 2026-11-13: Task 9b - Fix reasons and add frozen-configuration view
- Status: DONE
- Files created or changed:
  - coverage/build_coverage.py (replaced speculative never-covered reasons with dictionary-driven verified text, added compute_frozen_stats, added frozen configurations view to COVERAGE.md, coverage.html, and README.md, added coverage definition note)
  - coverage/COVERAGE.md (regenerated with dictionary reasons, coverage definition note, and frozen configurations section)
  - coverage/coverage.html (regenerated with dictionary reasons, coverage definition note, and frozen configurations section)
  - coverage/README.md (updated with coverage definition note and frozen configurations section; removed overfit text)
  - tests/test_coverage.py (added tests for T1529 containing 'flaw', absence of 'overfit' in generated files, and frozen configuration numbers: 14b v3b 19/20 on set 3 and 7/12 on set 1; 7b v3a 18/20 on set 3 and 5/12 on set 1)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-13: Task 10 - Gate demo and demo script update
- Status: DONE
- Files created or changed:
  - demo/gate_demo.py (created: standalone CLI tool to demonstrate gate evaluations with rule text, test logs, checklist, and explanation)
  - demo/sample_rules/rule_a_pass.yml (copied: T1615 repeat 1 from 14b v3b set 3, verdict PASS)
  - demo/sample_rules/rule_b_narrow_padded.yml (copied: T1564.004 repeat 1 from 7b v1 set 3, verdict TOO_NARROW)
  - demo/sample_rules/rule_c_narrow_copy.yml (copied: T1220 repeat 1 from 7b v1 set 3, verdict TOO_NARROW)
  - demo/sample_rules/rule_d_syntax_error.yml (copied: T1529 repeat 2 from 7b v3a set 3, verdict SYNTAX_ERROR)
  - demo/sample_rules/README.md (created: documentation of the four real model output sample rules)
  - tests/test_gate_demo.py (created: unit tests for gate_demo across all four sample rules and results/ immutability check)
  - docs/DEMO_SCRIPT.md (updated: 5-minute presentation plan with exact PowerShell commands, spoken talking points, checklist, and contingency steps)
  - README.md (updated: added gate demo commands and updated folder map)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-16: Task 11 - Web dashboard prototype (Flask + D3.js)
- Status: DONE
- Files created or changed:
  - dashboard/__init__.py, dashboard/app.py (created: Flask application with HTML routes and REST JSON APIs)
  - dashboard/data_loader.py (created: data extraction and aggregation across results, coverage, and generator)
  - dashboard/templates/ (created: base.html, overview.html, coverage_map.html, technique.html, runs.html, run_detail.html, gate_tester.html, pipeline.html)
  - dashboard/static/ (created: js/radar.js, js/barchart.js, css/custom.css)
  - tests/test_dashboard.py (created: automated unit tests covering data loader, web views, and REST endpoints)
  - README.md (updated with web dashboard execution instructions and folder map)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-20: Task 11b - Modern React + Vite Dashboard overhaul and color synchronization
- Status: DONE
- Files created or changed:
  - dashboard/frontend/ (created: React 19, Vite, Tailwind CSS v4, shadcn/ui frontend workbench)
  - dashboard/frontend/src/views/ (CoverageMatrixView.tsx, OverviewView.tsx, RunsView.tsx, GateValidatorView.tsx, PipelineView.tsx)
  - dashboard/frontend/src/data/ (all_runs.json, all_techniques.json, fallback.ts)
  - dashboard/templates/ (updated: coverage_map.html, gate_tester.html, overview.html, pipeline.html, runs.html, technique.html, base.html)
  - dashboard/app.py (updated with SPA routing to frontend dist)
  - .gitignore (created: root ignore for node_modules, dist, .agents, and pycache)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-23: Task 11c - Enterprise design system: dark mode, tokens, data density
- Status: DONE
- Files created or changed:
  - dashboard/frontend/src/index.css (rewritten: 34 custom CSS tokens, dark-first theme with light opt-in, verdict and brand tokens, always-dark sidebar tokens)
  - dashboard/frontend/src/App.tsx (updated: theme state with localStorage, data-theme attribute, dark class toggle, theme props to Header)
  - dashboard/frontend/src/components/Header.tsx (updated: theme toggle with Sun/Moon icons, token-based classes)
  - dashboard/frontend/src/components/Sidebar.tsx (updated: always-dark sidebar with fixed zinc/cyan, tighter w-52 width, cyan accent)
  - dashboard/frontend/src/components/ui/metric-card.tsx (updated: token-based colors, monospace tabular values)
  - dashboard/frontend/src/components/ui/verdict-badge.tsx (updated: token-based verdict colors with muted/edge variants, role badges)
  - dashboard/frontend/src/components/ui/skeleton.tsx (created: loading skeleton component)
  - dashboard/frontend/src/views/OverviewView.tsx (rewritten: token-based colors, SVG radar uses CSS vars, loading pulse, brand-muted hero card)
  - dashboard/frontend/src/views/CoverageMatrixView.tsx (rewritten: token-based colors, loading state, verdict badges, always-dark code blocks)
  - dashboard/frontend/src/views/GateValidatorView.tsx (rewritten: token-based colors, always-dark YAML editor, focus rings, verdict tokens)
  - dashboard/frontend/src/views/RunsView.tsx (rewritten: token-based colors, sortable columns with sort indicators, sticky headers, loading state)
  - dashboard/frontend/src/views/PipelineView.tsx (rewritten: token-based colors, always-dark code blocks, brand stepper)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-24: Task 12 - MITRE ATT&CK STIX lookup (file-only, no TAXII)
- Status: DONE
- Files created or changed:
  - data/enterprise-attack.json (downloaded: 55 MB STIX 2.1 bundle from MITRE GitHub, gitignored)
  - data/build_attack_lookup.py (created: parses STIX bundle into small lookup JSON, maps stealth and defense-impairment slugs to Defense Evasion)
  - data/attack_lookup.json (created: 706 techniques with official name, tactics, and URL)
  - data/attack_lookup.py (created: accessor module with get_technique, get_name, get_tactics, get_url)
  - coverage/build_coverage.py (updated: imports attack_lookup, adds attack_name column to CSV/HTML/MD, uses ATT&CK tactics when available)
  - coverage/coverage.csv (regenerated with attack_name column and ATT&CK tactics)
  - coverage/coverage.html (regenerated with ATT&CK Name column and official tactic names)
  - coverage/COVERAGE.md (regenerated with ATT&CK names in covered and never-covered lists)
  - coverage/README.md (regenerated)
  - dashboard/data_loader.py (updated: reads attack_name from coverage.csv, uses it as display title)
  - .gitignore (updated: added enterprise-attack.json)
  - tests/test_attack_lookup.py (created: 12 tests covering file structure, accessor functions, tactic mapping, and all 44 techniques present)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-23: Task 11c - Comprehensive feature audit, interactive API wiring, and inter-view handoffs
- Status: DONE
- Files created or changed:
  - dashboard/pipeline_service.py (created: production pipeline service for TTP extraction, rule drafting, and strict SQLite gate verification across all 44 techniques without crash or exit)
  - dashboard/app.py (updated: added /api/pipeline/run and /api/pipeline POST routes with dual payload schema, hardened /api/gate with string-to-int set parsing, error handling, reason explanation, and added /app/ route)
  - dashboard/frontend/src/App.tsx (updated: wired cross-page state handoffs for gateInitialData and selectedRunFolder)
  - dashboard/frontend/src/views/GateValidatorView.tsx (updated: fixed noisy sample from invalid T1082 to real T1547.001 Reg Add, added initialData hook to auto-load and evaluate rules passed from ATT&CK matrix)
  - dashboard/frontend/src/views/CoverageMatrixView.tsx (updated: wired Test in Gate Validator button to hand off technique and rule YAML to gate validator, added NOISY and SYNTAX_ERROR status filter options)
  - dashboard/frontend/src/views/RunsView.tsx (updated: fixed ATT&CK Matrix View button navigation target from invalid matrix to coverage, added initialFolder support)
  - dashboard/frontend/src/views/OverviewView.tsx (updated: made all run rows in Latest Evaluation Batches interactive with direct navigation to deep-dive inspector in Runs tab)
  - tests/test_dashboard.py (updated: added automated test cases for /api/pipeline/run, /api/pipeline, /api/gate noisy/syntax-error, and /app /app/ routes)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-23: Task 11d - Vector security logo emblem, arrow removal, and browser back/forward history routing
- Status: DONE
- Files created or changed:
  - dashboard/frontend/src/components/AtidepLogo.tsx (created: vector cyber defense shield emblem with gradient precision geometry and detection interceptor glyph)
  - dashboard/frontend/src/components/Sidebar.tsx (updated: replaced generic square with AtidepLogo)
  - dashboard/frontend/src/views/OverviewView.tsx (updated: removed ArrowRight from Launch Pipeline Studio button and ArrowUpRight from View All 14 Runs button)
  - dashboard/frontend/src/views/PipelineView.tsx (updated: removed ArrowRight from Execute Detection Pipeline button)
  - dashboard/frontend/src/App.tsx (updated: integrated URL hash history synchronization with popstate/hashchange listeners so browser Back and Forward buttons navigate cleanly between tabs without routing away)
  - PROGRESS.md (updated)
- WARN lines: none

### 2026-11-23: Task 12 - Enterprise UI polish (5-phase frontend transformation)
- Status: DONE
- Summary: Transformed the React dashboard from AI-generated appearance to polished enterprise-grade design through systematic audit, design system definition, and component-level implementation across all views.
- Design decisions:
  - Primary accent: indigo-600 (replacing generic blue-600)
  - Verdict palette: PASS=emerald, TOO_NARROW=amber, NOISY=orange, SYNTAX_ERROR/MISSED_SHOWN=rose
  - Role badges: primary=indigo, baseline=slate
  - Typography: semibold headers (not extrabold), normal case labels, font-mono for data values only
  - Removed: fake SOC chrome, spotlight animation, excessive uppercase/tracking-wider, font-extrabold overuse, animate-pulse decorations, hardcoded stat values
- Files created or changed:
  - dashboard/frontend/src/components/ui/metric-card.tsx (created: reusable KPI card component replacing repeated inline card patterns)
  - dashboard/frontend/src/components/ui/verdict-badge.tsx (created: shared VerdictBadge component with semantic verdict and role badge color utilities)
  - dashboard/frontend/src/index.css (updated: removed spotlight animation keyframes and .animate-spotlight class)
  - dashboard/frontend/src/components/AtidepLogo.tsx (rewritten: simplified from complex gradient SVG to clean flat shield with currentColor)
  - dashboard/frontend/src/components/Sidebar.tsx (rewritten: removed SOC Sentinel branding, PROTOTYPE badge, SYSTEM HEALTHY pulse, Lead Detection Engineer title; simplified nav labels and group names)
  - dashboard/frontend/src/components/Header.tsx (rewritten: removed ATIDEP Operations label, RTX chip, animate-pulse Ollama dot, FAST FYP-1 badge; simplified page titles)
  - dashboard/frontend/src/views/OverviewView.tsx (rewritten: removed Spotlight hero, used MetricCard for KPIs, semantic benchmark colors, cleaner radar inspector)
  - dashboard/frontend/src/views/CoverageMatrixView.tsx (rewritten: imported VerdictBadge for semantic verdict colors, used MetricCard for stats, indigo selection states, cleaner matrix tiles and inspector)
  - dashboard/frontend/src/views/GateValidatorView.tsx (rewritten: semantic checklist colors emerald/rose, semantic verdict banner via getVerdictStyle, indigo primary button)
  - dashboard/frontend/src/views/RunsView.tsx (rewritten: computed stats from data, imported shared badge styles, semantic indigo progress bars, cleaner analytics cards)
  - dashboard/frontend/src/views/PipelineView.tsx (rewritten: indigo stepper and buttons, semantic verdict display via getVerdictStyle, cleaner architecture cards)
  - PROGRESS.md (updated)
- Build: npm run build passes clean (485.94 kB JS, 44.50 kB CSS)
- Tests: 13/13 pytest tests pass
- WARN lines: none

### 2026-11-24: Task 13 - Full system unit test run
- Status: DONE
- What: Ran all 20 test files across the system (16 in tests/, 4 in validator/) individually and as a full suite.
- Results:
  - tests/ (pytest): 99/99 passed (after fixing one stale assertion, see below)
  - validator/test_real.py: 7/7 real SigmaHQ rules fire correctly on attack logs
  - validator/test_set2_real_rules.py: 12/12 set 2 rules pass strict gate (attack + variant + no harmless)
  - validator/test_set1_variants.py: 12/12 set 1 rules pass strict gate
  - validator/test_set3_real_rules.py: 20/20 set 3 rules pass strict gate
- Fix applied: tests/test_set3_guard.py::test_no_log_or_folder_created assumed set3_use_log.csv never exists. After the actual set 3 experiment was run, this file legitimately exists. Changed the assertion to verify the guard does not modify the file (mtime check) rather than asserting it does not exist.
- Files changed:
  - tests/test_set3_guard.py (updated: test_no_log_or_folder_created now checks mtime instead of non-existence)
  - PROGRESS.md (updated)
- WARN lines: none

## 2026-11-24: Task 16 -- Frontend visual polish
- Status: DONE
- Summary: Comprehensive visual improvement pass on the React dashboard frontend. All changes are in dashboard/frontend/src/.
- Changes:
  - index.css: Added 6 new design tokens (code-bg, code-fg, code-edge, code-muted, bar-secondary, bar-tertiary) for both dark and light themes. Added selection color, focus-visible outline, and smooth scroll to base layer.
  - components/ui/metric-card.tsx: Added cyan left accent bar, hover border transition, improved spacing.
  - components/Header.tsx: Improved padding, wider search input, animated Ollama status dot (ping animation), rounded-lg buttons, focus-visible ring.
  - components/Sidebar.tsx: Bumped 9px text to 10px, uppercase group labels, larger nav items (py-2, w-4 icons), added ring on avatar, inner glow on active tab, 150ms transitions.
  - views/OverviewView.tsx: Radar chart now shows short tactic names (Recon, Priv Esc, C2) instead of IDs. Fixed bar chart opacity hack (bg-brand opacity-60 to bg-bar-secondary token). Hero section gets gradient overlay and rounded-xl. Buttons use rounded-lg and transition-all.
  - views/CoverageMatrixView.tsx: Code block uses token-based colors (bg-code-bg, etc.) instead of hardcoded zinc. Technique tiles get rounded-lg, hover shadow, 150ms transition. Bumped set badge from 9px to 10px.
  - views/GateValidatorView.tsx: Code editor textarea uses token-based colors. Checklist items get bordered cards with colored circle indicators. Verdict box is larger with tracking-wide. Run button gets rounded-lg, disabled state, 150ms transition.
  - views/PipelineView.tsx: Code block uses token-based colors. Stepper shows checkmarks for completed steps, animate-pulse for active step. Execute button gets rounded-lg, disabled state.
  - views/RunsView.tsx: Fixed 2 opacity-60 bar hacks to use bar-secondary/bar-tertiary tokens. Buttons get rounded-lg and transitions.
  - App.tsx: Main content padding from p-3/p-5 to p-4/p-6, added max-w-[1600px] constraint, smooth scroll.
- Build: clean (0 errors, 0 warnings)
- Tests: 99/99 passed
- WARN lines: none

### 2026-11-24: Task 17 - Coverage Matrix tile redesign and TAXII connector
- Status: DONE
- Coverage Matrix (dashboard/frontend/src/views/CoverageMatrixView.tsx, components/ui/verdict-badge.tsx): tiles have a verdict-colored left border, columns have a coverage progress bar, better empty state. Build clean.
- TAXII: user approved adding taxii2-client 2.3.0 and stix2 3.0.2 (installed with pip).
- Files created or changed:
  - data/taxii_connector.py (created: pulls attack-pattern objects from https://attack-taxii.mitre.org/api/v21/ collection "Enterprise ATT&CK", reuses build_lookup from build_attack_lookup.py; --check compares without writing; keeps local attack_lookup.json if server is down or result has fewer than 500 techniques)
  - tests/test_taxii_connector.py (created: 4 offline tests, server down, too few results, good update, check mode)
  - .gitignore (added data/enterprise-attack-taxii.json)
  - README.md (TAXII section, file map, test count 103)
- Self-check:
  | EXPECTED | ACTUAL | RESULT |
  | Live TAXII fetch works | 867 attack-pattern objects, 706 active techniques | PASS |
  | TAXII result equals local lookup | 0 new, 0 gone, 0 changed | PASS |
  | Server down keeps local file | test_server_down_keeps_local_lookup | PASS |
  | Full pytest suite | 103 passed (99 before plus 4 new) | PASS |
- Not done: TAXII is not called automatically by the pipeline or dashboard. It is a manual refresh command. attack_lookup.json was not rewritten (check mode only).
- WARN lines: none

### 2026-11-24: Task 18 - TAXII structured ingestion into pipeline
- Status: DONE
- What was built:
  - TAXII connector expanded to fetch intrusion-sets and relationships (group-to-technique mapping) in addition to attack-patterns.
  - New ingestion module (data/taxii_ingest.py) maps threat groups to pipeline-supported techniques.
  - 4 new Flask API endpoints: /api/taxii/status, /api/taxii/groups, /api/taxii/ingest, /api/taxii/refresh.
  - Dashboard Pipeline view has a collapsible "STIX/TAXII Structured Ingestion" panel: load groups, filter, ingest a group's techniques, refresh the ATT&CK lookup.
  - Proposal reworded: TAXII maps groups to techniques; command lines come from reports/templates, not TAXII; IOC extraction is future work; Flask replaces FastAPI.
- Files created or changed:
  - data/taxii_connector.py (expanded: fetch_all_types, build_group_techniques)
  - data/taxii_ingest.py (created: ingest_by_group, ingest_all_groups, list_groups)
  - dashboard/app.py (added 4 TAXII endpoints)
  - dashboard/frontend/src/views/PipelineView.tsx (TAXII ingestion panel)
  - tests/test_taxii_ingest.py (created: 7 offline tests)
  - ATIDEP_FYP1_Proposal.md (reworded TAXII sections at lines 154, 167, 211, 259, 287)
  - README.md (TAXII section expanded, file map updated, test count 110)
  - PROGRESS.md (this entry)
- Self-check:
  | EXPECTED | ACTUAL | RESULT |
  | Frontend builds clean | 0 errors | PASS |
  | New tests pass | 7/7 | PASS |
  | Full suite | 110 passed | PASS |
  | TAXII panel renders in dashboard | Build succeeds, component compiles | PASS |
  | Proposal matches implementation | Reworded 5 TAXII sections | PASS |
- Limitations:
  - TAXII maps groups to technique IDs. It does not provide command lines. Rule generation still needs a threat report or synthetic log template for the command context.
  - IOC extraction (IPs, hashes, domains) is not built. IOCs are not used in process-creation Sigma rules.
  - The "Ingest" button shows the group's techniques but does not auto-run the LLM pipeline on each one (that would need Ollama and would take minutes per technique).
- WARN lines: none

### 2026-11-25: Task 20 - Multi-format rule export (SPL, KQL)
- Status: DONE
- What was built:
  - Export module (export/rule_export.py) converts Sigma YAML to Splunk SPL, Microsoft Defender KQL, and SQLite SQL using pySigma backends.
  - 2 Flask API endpoints: POST /api/export (convert a rule to a format) and GET /api/export/formats (list available formats).
  - Dashboard Gate Validator view has a new "Export Rule" panel: pick a format, click Convert, see the output, copy to clipboard.
  - 20 unit tests for the export module (test_rule_export.py) and 6 API endpoint tests added to test_dashboard.py.
- Dependencies installed: pysigma-backend-splunk, pysigma-backend-microsoft365defender.
- Supported formats: Sigma YAML (passthrough), Splunk SPL, Microsoft Defender KQL, SQLite (gate query).
- Files created or changed:
  - export/rule_export.py (created: to_splunk, to_kql, to_sqlite, convert, convert_all, FORMATS)
  - dashboard/app.py (added /api/export and /api/export/formats endpoints)
  - dashboard/frontend/src/views/GateValidatorView.tsx (added Export Rule panel with format selector, convert button, output display, copy button)
  - tests/test_rule_export.py (created: 20 tests)
  - tests/test_dashboard.py (added 6 export API tests)
  - PROGRESS.md (this entry)
- Self-check:
  | EXPECTED | ACTUAL | RESULT |
  | Splunk SPL output contains field names | CommandLine="/priv*" Image="*\\whoami.exe" | PASS |
  | KQL output uses contains operator | CommandLine contains "/priv" and Image endswith "\\whoami.exe" | PASS |
  | Bad rule returns error | ValueError raised | PASS |
  | Unknown format returns 400 | HTTP 400 with error message | PASS |
  | Frontend builds clean | 0 TypeScript errors, 0 build errors | PASS |
  | Full test suite | 136 passed (110 + 26 new) | PASS |
- WARN lines: none

### 2026-11-25: Task 21 - Threat-informed prioritisation
- Status: DONE
- What was built:
  - Prioritisation module (export/prioritisation.py) ranks all ATT&CK techniques by how many active threat groups use them, using MITRE TAXII 2.1 group-to-technique mappings.
  - Techniques are sorted: uncovered-in-pipeline first (by group count desc), then not-in-pipeline, then covered. Each entry includes group count, top group names, pipeline membership, coverage status, and set number.
  - Coverage check reads run CSV verdicts directly (fast, no re-scoring from disk).
  - Falls back to local-only mode (no group counts) when TAXII is unreachable.
  - Flask API endpoint: GET /api/priority-backlog with optional ?filter= (all, uncovered, in_pipeline) and ?limit= query params.
  - React dashboard view: "Priority Backlog" with metric cards (ATT&CK technique count, threat group count, pipeline count, uncovered gap), filter buttons, search bar, sortable table with threat-level bar, group count with expand, pipeline/coverage status badges.
  - New sidebar entry under Engineering: "Priority Backlog" with Shield icon.
  - 17 unit tests: 3 for _invert_groups, 2 for _supported_technique_ids, 8 for build_priority_backlog (including mock TAXII), 4 for the API endpoint.
- Files created or changed:
  - export/prioritisation.py (created: _invert_groups, _supported_technique_ids, _which_set, _covered_techniques, build_priority_backlog)
  - dashboard/app.py (added GET /api/priority-backlog endpoint)
  - dashboard/frontend/src/views/PriorityBacklogView.tsx (created: full priority backlog view)
  - dashboard/frontend/src/components/Sidebar.tsx (added Priority Backlog nav item)
  - dashboard/frontend/src/App.tsx (added priority tab and PriorityBacklogView import)
  - tests/test_prioritisation.py (created: 17 tests)
  - PROGRESS.md (this entry)
- Self-check:
  | EXPECTED | ACTUAL | RESULT |
  | 44 pipeline techniques flagged | 44 in_pipeline entries | PASS |
  | Covered count matches summary | covered_in_backlog == result["covered"] | PASS |
  | Uncovered techniques sorted first | first uncovered idx < last covered idx | PASS |
  | Mock TAXII returns group counts | T1059.001 group_count=3 with 3 mock groups | PASS |
  | API filter=uncovered returns only uncovered | all entries have covered=false | PASS |
  | API filter=in_pipeline returns only pipeline | all entries have in_pipeline=true | PASS |
  | Frontend builds clean | 0 TypeScript errors, 0 build errors | PASS |
  | Full test suite | 153 passed (136 + 17 new) | PASS |
- WARN lines: none

### 2026-11-25: Task 22 - IOC extraction from reports
- Status: DONE
- What was built:
  - IOC extraction module (export/ioc_extract.py) pulls IPv4 addresses, domain names, URLs, and file hashes (MD5, SHA1, SHA256) from raw threat report text using regex.
  - Handles defanged indicators: hxxp://, [.], [dot], [:] are re-fanged before extraction.
  - Filters out common false positives (loopback IPs, well-known domains like microsoft.com, attack.mitre.org).
  - Deduplicates results. SHA256 substrings are not also reported as MD5/SHA1. Domains already in a URL are not duplicated.
  - Integrated into pipeline_service.py: run_pipeline() now returns an "iocs" field alongside technique/rule/verdict.
  - Flask API endpoint: POST /api/ioc/extract (standalone IOC extraction from any text).
  - Pipeline view updated: IOC panel shows extracted IPs, domains, URLs, and hashes with type badges. Appears only when IOCs are found. SMB sample scenario enriched with IOC data (IPs, hash, defanged URL).
  - 29 unit tests: 5 for _refang, 5 for IPv4, 4 for domains, 3 for URLs, 4 for hashes, 3 for has_iocs, 1 mixed report, 4 for API endpoints (including pipeline integration).
- Files created or changed:
  - export/ioc_extract.py (created: _refang, extract_iocs, has_iocs)
  - dashboard/pipeline_service.py (added IOC extraction to run_pipeline output)
  - dashboard/app.py (added POST /api/ioc/extract endpoint)
  - dashboard/frontend/src/types/index.ts (added IocHash, IocResult interfaces, iocs field on PipelineExecutionResult)
  - dashboard/frontend/src/views/PipelineView.tsx (added IOC display panel with Fingerprint icon, type badges for hashes)
  - tests/test_ioc_extract.py (created: 29 tests)
  - PROGRESS.md (this entry)
- Self-check:
  | EXPECTED | ACTUAL | RESULT |
  | IPv4 extraction works | "10.0.0.5" found in result["ipv4"] | PASS |
  | Defanged indicators re-fanged | "evil[.]com" becomes "evil.com" | PASS |
  | SHA256 not also reported as MD5 | 1 hash entry with type "sha256" | PASS |
  | Loopback excluded | 127.0.0.1 not in results | PASS |
  | URL domains not duplicated | domain in URLs only, not in domains list | PASS |
  | Pipeline returns IOCs | /api/pipeline/run includes iocs field with IPs | PASS |
  | Standalone API works | POST /api/ioc/extract returns IOCs | PASS |
  | Frontend builds clean | 0 TypeScript errors, 0 build errors | PASS |
  | Full test suite | 182 passed (153 + 29 new) | PASS |
- WARN lines: none
