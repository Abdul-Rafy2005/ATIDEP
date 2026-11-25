# ATIDEP: Automated Threat-Informed Detection Engineering Platform

ATIDEP is an Automated Threat-Informed Detection Engineering Platform developed as a final year project (FYP-1) at the National University of Computer and Emerging Sciences (FAST-NUCES), Fall 2026.

Supervisor: Dr. Shahbaz Siddiqui.
Team: Abdul Rafy (backend and AI), Muhammad Owais (malware sandbox), Abdul Ahad (governance and coverage template).

The system takes unstructured threat descriptions, uses a local LLM to draft Sigma detection rules, and evaluates each rule through an automated validation gate. The gate tests pySigma SQL conversion syntax, catches hidden attack variants, and blocks noisy or overly narrow detections on synthetic process creation logs.

---

## Key Results

| Configuration | Role | Strict Pass on Set 3 (/60) | Techniques Passed (>=2/3) |
|---|---|---|---|
| qwen2.5-coder:14b, prompt v3b | Primary | 57/60 (95.0%) | 19/20 |
| qwen2.5-coder:7b, prompt v3a | Comparison | 58/60 (96.7%) | 20/20 |
| qwen2.5-coder:14b, prompt v1 | Baseline | 47/60 (78.3%) | 16/20 |
| qwen2.5-coder:7b, prompt v1 | Baseline | 35/60 (58.3%) | 11/20 |

Prompt engineering improved the primary model (14b) from 78.3% to 95.0% strict pass rate, and the comparison model (7b) from 58.3% to 96.7%. Under baseline prompt v1, 37.5% of single-gate-approved rules for the 7b model failed on hidden variants. The improved prompts reduced that gap to under 5%.

Full results: [docs/FYP1_LLM_testing_report.md](docs/FYP1_LLM_testing_report.md) and [results/FINAL_set3_report.md](results/FINAL_set3_report.md).

---

## Installation

### Prerequisites
- Windows 11 with PowerShell
- Python 3.13
- Node.js 18+ (for the React frontend dashboard, optional)
- Local Ollama runtime (version 0.40.7 or later) with GPU support

### Setup Steps
```powershell
# Clone repository and change directory
cd C:\ATIDEP

# Install required Python dependencies
pip install pySigma pysigma-backend-sqlite pyyaml flask

# Pull required local models in Ollama
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b
```

### Building the ATT&CK Lookup (one-time)
```powershell
# Download MITRE ATT&CK STIX 2.1 bundle and build the lookup JSON
python data/build_attack_lookup.py

# This creates data/attack_lookup.json (706 techniques with names, tactics, URLs)
# The 55 MB STIX bundle (data/enterprise-attack.json) is gitignored
```

### STIX/TAXII Connector (optional, needs `pip install taxii2-client stix2`)
```powershell
# Refresh the ATT&CK technique lookup from MITRE's TAXII 2.1 server
python data/taxii_connector.py --check   # fetch and compare, write nothing
python data/taxii_connector.py           # fetch and update data/attack_lookup.json
```
If the server cannot be reached, or returns fewer than 500 techniques, the local `attack_lookup.json` is kept unchanged.

The connector also supports structured ingestion: given a threat group name (e.g. APT29), it pulls the group's techniques from TAXII and filters to the ones our pipeline has synthetic logs for. This is available:
- **From the dashboard:** Pipeline view, expand "STIX/TAXII Structured Ingestion", click "Load Threat Groups", then "Ingest" on a group.
- **From the API:** `POST /api/taxii/ingest {"group": "APT29"}` returns the group's techniques with support status.
- **From Python:** `from data.taxii_ingest import ingest_by_group; ingest_by_group("APT29")`

Command-line context for rule generation comes from threat reports or our synthetic log templates. STIX objects rarely carry observed command lines, so TAXII input drives which techniques to cover, not how to write the rule.

---

## Running the Demo

The end-to-end demo takes a threat report text snippet, identifies the technique, generates a rule using the frozen prompt, and tests it on the validation gate.

```powershell
# Run demo on a supported sample (whoami /priv)
python demo/demo.py --file demo/samples/sample1.txt

# Run demo with direct text input
python demo/demo.py --text "Adversaries executed whoami.exe /priv to discover privileges."

# Run demo on an unsupported sample (demonstrates clean refusal)
python demo/demo.py --file demo/samples/sample4.txt

# Run the standalone validation gate demonstration on sample rules
python demo/gate_demo.py --rule demo/sample_rules/rule_a_pass.yml --set 3 --technique T1615
python demo/gate_demo.py --rule demo/sample_rules/rule_b_narrow_padded.yml --set 3 --technique T1564.004
python demo/gate_demo.py --rule demo/sample_rules/rule_c_narrow_copy.yml --set 3 --technique T1220
python demo/gate_demo.py --rule demo/sample_rules/rule_d_syntax_error.yml --set 3 --technique T1529
```

Demo output artifacts (JSON summary and YAML rule) are saved to `demo/output/`.

---

## Running the Web Dashboard

ATIDEP includes two dashboard interfaces.

### React Frontend (recommended)

Built with React 19, Vite 8, TypeScript, Tailwind CSS v4, and shadcn/ui. Dark mode enabled by default.

```powershell
# Start the Flask API backend
python dashboard/app.py

# In a second terminal, start the Vite dev server
cd dashboard/frontend
npm install
npm run dev

# Open in browser: http://localhost:5173
```

To build for production:
```powershell
cd dashboard/frontend
npm run build
# Then open http://127.0.0.1:5000/app/ (Flask serves the built files)
```

### Flask HTML Dashboard (legacy)

```powershell
python dashboard/app.py
# Open in browser: http://127.0.0.1:5000
```

### Dashboard Features
- **Overview:** Metric cards, SVG ATT&CK tactic radar chart, Set 3 benchmark comparison bars.
- **Coverage Matrix:** Interactive tactic-grouped matrix across 44 techniques with ATT&CK official names.
- **Experiment Runs:** Sortable table of all recorded runs with strict/single pass metrics.
- **Gate Validator:** Live interactive Sigma rule validator against synthetic logs.
- **Pipeline Studio:** End-to-end extraction, drafting, and validation pipeline interface.

---

## Running the Tests

All tests run locally without requiring live GPU inference.

```powershell
# Run the full pytest suite (110 tests)
python -m pytest tests/ -v

# Run the validator scripts (SigmaHQ reference rules against synthetic logs)
$env:PYTHONPATH = "c:\ATIDEP;c:\ATIDEP\validator;c:\ATIDEP\generator"
python validator/test_real.py
python validator/test_set1_variants.py
python validator/test_set2_real_rules.py
python validator/test_set3_real_rules.py

# Verify all frozen files match pre-registered SHA-256 hashes
python tools/check_frozen.py
```

---

## Generating the ATT&CK Coverage Template

```powershell
# Build the HTML, CSV, and markdown coverage reports across 44 techniques
python coverage/build_coverage.py

# Open the visual coverage report
Start-Process coverage\coverage.html
```

Coverage pulls official technique names and tactics from the ATT&CK STIX lookup (`data/attack_lookup.json`).

---

## Reproducing the Experiments

See [docs/FYP1_LLM_testing_report.md](docs/FYP1_LLM_testing_report.md) Section 9 for step-by-step reproduction commands. The short version:

```powershell
# Verify frozen files are unmodified
python tools/check_frozen.py

# Run Set 1 experiments (development set, safe to repeat)
python llm/run_experiment.py --set 1 --prompt v3a --models qwen2.5-coder:7b qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100

# Run Set 3 final test (requires --final and --reason flags)
python llm/run_experiment.py --set 3 --final --reason "reproduction run" --prompt v3b --models qwen2.5-coder:14b --repeats 3 --temperature 0.2 --seed 100
```

---

## Folder Map

```text
C:\ATIDEP/
├── coverage/                 # ATT&CK coverage template builder and outputs
│   ├── build_coverage.py     # Generates coverage matrix from results and ATT&CK data
│   ├── coverage.csv          # Machine-readable coverage matrix (44 techniques)
│   ├── coverage.html         # Visual HTML coverage report
│   ├── COVERAGE.md           # Coverage summary with frozen-only metrics
│   └── README.md             # Coverage template documentation
├── dashboard/                # Web dashboard application
│   ├── app.py                # Flask server, REST API endpoints, SPA routing
│   ├── data_loader.py        # Data aggregator for runs, coverage, and techniques
│   ├── pipeline_service.py   # Production pipeline service (extract, draft, validate)
│   ├── frontend/             # React 19 + Vite + TypeScript + Tailwind + shadcn/ui
│   │   └── src/views/        # OverviewView, CoverageMatrixView, RunsView, GateValidatorView, PipelineView
│   ├── templates/            # Legacy Flask HTML views
│   └── static/               # Legacy D3.js visualizers and styles
├── data/                     # Reference rules, synthetic logs, and ATT&CK lookup
│   ├── attack_lookup.json    # 706 ATT&CK techniques (name, tactics, URL)
│   ├── attack_lookup.py      # Accessor: get_technique, get_name, get_tactics
│   ├── build_attack_lookup.py# Parses STIX 2.1 bundle into attack_lookup.json
│   ├── taxii_connector.py    # STIX/TAXII connector: pulls techniques, groups and relationships from MITRE TAXII 2.1
│   ├── taxii_ingest.py       # Structured ingestion: maps threat groups to pipeline-supported techniques
│   ├── sigmahq_rules/        # Reference SigmaHQ rules for Set 1
│   ├── sigmahq_rules_set2/   # Reference SigmaHQ rules for Set 2
│   ├── sigmahq_rules_set3/   # Reference SigmaHQ rules for Set 3
│   └── synthetic_logs/       # Generated synthetic logs for Set 1
├── demo/                     # End-to-end interactive prototype and gate demo
│   ├── demo.py               # Main demo driver (technique -> rule -> gate -> save)
│   ├── gate_demo.py          # Standalone gate evaluation demonstration
│   ├── sample_rules/         # Four real model rules (PASS, TOO_NARROW, SYNTAX_ERROR)
│   ├── samples/              # Synthetic test paragraphs (samples 1-4)
│   └── output/               # Saved demonstration rules and JSON summaries
├── docs/                     # Project documentation and reports
│   ├── DEMO_SCRIPT.md        # 5-minute evaluation presentation plan
│   └── FYP1_LLM_testing_report.md  # Full FYP-1 testing report with all results
├── generator/                # Synthetic event generation and technique definitions
│   ├── generate.py           # Set 1 techniques (12) and make_triple generator
│   ├── techniques_set2.py    # Set 2 techniques (12) and make_triple generator
│   └── techniques_set3.py    # Set 3 techniques (20) and make_triple3 generator
├── llm/                      # Prompt templates, Ollama runner, and scoring
│   ├── prompts/              # Frozen prompt templates (v1, v2, v2_1, v3a, v3b)
│   ├── analyze_failure_modes.py       # Failure mode classifier for Set 1
│   ├── analyze_failure_modes_set3.py  # Failure mode classifier for Set 3
│   ├── compare_models.py     # Set 1 evaluation driver
│   ├── run_experiment.py     # Unified multi-set experiment execution pipeline
│   └── scoring.py            # Unified rule scoring and gate verification module
├── results/                  # Evaluation outputs, summaries, and run artifacts
│   ├── runs/                 # Timestamped experiment folders (16 runs)
│   ├── archive/              # Archived prompt v1 and earlier results
│   ├── FINAL_set3_report.md  # Final evaluation report on locked Set 3
│   ├── RESULTS_SUMMARY.md    # Multi-round summary table across experiments
│   ├── set1_prompt_round3.md # Round 3 prompt comparison on Set 1
│   ├── set1_failure_modes.md # Set 1 failure mode breakdown
│   └── set3_use_log.csv      # Audit log of Set 3 executions
├── tests/                    # Automated regression test suite (110 tests)
│   ├── test_attack_lookup.py # ATT&CK STIX lookup module tests (12 tests)
│   ├── test_taxii_connector.py # TAXII connector tests, offline (4 tests)
│   ├── test_taxii_ingest.py  # TAXII ingestion tests, offline (7 tests)
│   ├── test_coverage.py      # Coverage template builder tests (16 tests)
│   ├── test_dashboard.py     # Flask API and data loader tests (13 tests)
│   ├── test_demo.py          # End-to-end demo prototype tests (9 tests)
│   ├── test_gate_demo.py     # Gate demo sample rules tests (5 tests)
│   ├── test_scoring_pipeline.py # Scoring pipeline across all sets (13 tests)
│   ├── test_prompts.py       # Prompt v1/v2 tests (2 tests)
│   ├── test_prompts_v3.py    # Prompt v3a/v3b tests (5 tests)
│   ├── test_prompt_v2_1.py   # Prompt v2_1 tests (2 tests)
│   ├── test_runner_options.py# CLI runner options tests (4 tests)
│   ├── test_strict_gate_sanity.py  # Gate correctness tests (2 tests)
│   ├── test_set3_sanity.py   # Set 3 structure tests (4 tests)
│   ├── test_set3_guard.py    # Set 3 access guard tests (4 tests)
│   ├── test_check_frozen.py  # Frozen file hash tests (2 tests)
│   ├── test_analyze_results.py     # Result analyzer tests (4 tests)
│   └── test_diagnose_run.py  # Run diagnostics tests (2 tests)
├── validator/                # Gate validation engine and reference rule tests
│   ├── runner.py             # pySigma SQLite gate: rule_to_sql, rule_matches
│   ├── gate.py               # Set 1 gate: check_rule returns PASS or FAIL
│   ├── test_real.py          # Set 1 reference rules against attack logs
│   ├── test_set1_variants.py # Set 1 strict gate on variants
│   ├── test_set2_real_rules.py # Set 2 reference rules against attack logs
│   └── test_set3_real_rules.py # Set 3 reference rules against attack logs
├── tools/                    # Operational and verification utilities
│   ├── check_frozen.py       # Verifies SHA-256 hashes against FROZEN.md
│   ├── lock_set3.py          # Hashes and locks Set 3 techniques and rules
│   └── rescore_all.py        # Rescores saved rule files using scoring.py
├── AGENTS.md                 # Core project context, guidelines, and history
├── FROZEN.md                 # Pre-registered models, prompts, and file hashes
├── PROGRESS.md               # Chronological task progress log
├── SET3_LOCK.md              # Cryptographic lock of Test Set 3 files
└── README.md                 # This file
```
