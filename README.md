# ATIDEP: Automated Threat-Informed Detection Engineering Platform

ATIDEP is an Automated Threat-Informed Detection Engineering Platform developed as a final year project at FAST.
It takes unstructured threat descriptions, uses a local LLM to draft Sigma rules, and evaluates each rule through an automated validation gate.
The gate tests pySigma SQL conversion syntax, catches hidden attack variants, and blocks noisy or overly narrow detections on synthetic process creation logs.

---

## Installation

### Prerequisites
- Windows 11 with PowerShell
- Python 3.13
- Local Ollama runtime (version 0.40.7 or later) with GPU support

### Setup Steps
```powershell
# Clone repository and change directory
cd C:\ATIDEP

# Install required Python dependencies
pip install pySigma pysigma-backend-sqlite pyyaml

# Pull required local models in Ollama
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b
```

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

## Running the Tests

All tests run locally using standard library unit testing and mocked models without requiring live GPU inference.

```powershell
# Run full unit test suite
python -m unittest discover -s tests -p "test_*.py"

# Verify all frozen files match pre-registered SHA-256 hashes
python tools/check_frozen.py
```

---

## Generating the ATT&CK Coverage Template

```powershell
# Build the HTML and CSV coverage matrices across 44 techniques
python coverage/build_coverage.py

# Open the visual coverage dashboard
Start-Process coverage\coverage.html
```

---

## Folder Map

```text
C:\ATIDEP/
├── coverage/                 # ATT&CK coverage template builder and outputs
│   ├── build_coverage.py     # Generates coverage matrix from CSVs and runs
│   ├── coverage.csv          # Machine-readable coverage matrix (44 techniques)
│   ├── coverage.html         # Interactive visual HTML coverage dashboard
│   ├── COVERAGE.md           # Detailed coverage summary and frozen-only metrics
│   └── README.md             # Coverage template documentation
├── data/                     # Reference SigmaHQ rules and synthetic logs
│   ├── sigmahq_rules/        # Reference rules for Set 1
│   ├── sigmahq_rules_set2/   # Reference rules for Set 2
│   ├── sigmahq_rules_set3/   # Reference rules for Set 3
│   └── synthetic_logs/       # Generated synthetic logs for Set 1
├── demo/                     # End-to-end interactive prototype and gate demo
│   ├── demo.py               # Main demo driver (technique -> rule -> gate -> save)
│   ├── gate_demo.py          # Standalone gate evaluation demonstration
│   ├── sample_rules/         # Four real model rules for gate testing
│   ├── samples/              # Synthetic test paragraphs (samples 1-4)
│   └── output/               # Saved demonstration rules and JSON summaries
├── docs/                     # Project documentation and reports
│   ├── DEMO_SCRIPT.md        # 5-minute evaluation presentation plan
│   └── FYP1_LLM_testing_report.md  # Comprehensive FYP-1 testing report
├── generator/                # Synthetic event generation and technique definitions
│   ├── generate.py           # Set 1 techniques and make_pair generator
│   ├── techniques_set2.py    # Set 2 techniques and make_triple generator
│   └── techniques_set3.py    # Set 3 techniques and make_triple3 generator
├── llm/                      # Prompt templates, Ollama runner, and scoring
│   ├── prompts/              # Frozen prompt templates (v1, v2, v2_1, v3a, v3b)
│   ├── analyze_failure_modes.py       # Failure mode classifier for Set 1
│   ├── analyze_failure_modes_set3.py  # Failure mode classifier for Set 3
│   ├── compare_models.py     # Set 1 evaluation driver
│   ├── run_experiment.py     # Unified multi-set experiment execution pipeline
│   └── scoring.py            # Unified rule scoring and gate verification module
├── results/                  # Evaluation outputs, summaries, and run artifacts
│   ├── runs/                 # Full timestamped experiment run folders
│   ├── FINAL_set3_report.md  # Final evaluation report on locked Set 3
│   ├── RESULTS_SUMMARY.md    # Multi-round summary table across experiments
│   ├── set1_prompt_round3.md # Round 3 evaluation comparison on Set 1
│   ├── set1_strict_summary.md# Set 1 strict gate summary
│   ├── set1_failure_modes.md # Set 1 failure mode breakdown
│   └── set3_use_log.csv      # Audit log of Set 3 executions
├── tests/                    # Automated regression test suite
│   ├── test_coverage.py      # Unit tests for coverage template builder
│   ├── test_demo.py          # Unit tests for end-to-end demo prototype
│   ├── test_prompts_v3.py    # Unit tests for prompts v3a and v3b
│   ├── test_runner_options.py# Unit tests for CLI runner options and flags
│   └── test_scoring_pipeline.py # Unit tests for scoring pipeline across sets
├── tools/                    # Operational and verification utilities
│   ├── check_frozen.py       # Verifies SHA-256 hashes against FROZEN.md
│   ├── lock_set3.py          # Hashes and locks Set 3 techniques and rules
│   └── rescore_all.py        # Rescores saved rule files using scoring.py
├── AGENTS.md                 # Core project context, guidelines, and history
├── FROZEN.md                 # Pre-registered models, prompts, and file hashes
├── PROGRESS.md               # Chronological task progress log
├── SET3_LOCK.md              # Cryptographic lock of Test Set 3 files
└── README.md                 # Project introduction, quickstart, and folder map
```
