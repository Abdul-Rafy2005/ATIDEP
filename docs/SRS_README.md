# ATIDEP Software Requirements Specification (SRS)

Project: Automated Threat-Informed Detection Engineering Platform (ATIDEP)
Session: Fall 2026, Final Year Project (Phase 1)
Department: Computer Science and Cyber Security, FAST-NUCES Karachi
Supervisor: Dr. Shahbaz Siddiqui
Team: Abdul Rafy (23P-0560), Abdul Ahad (23P-0625), Muhammad Owais (23K-5544)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the FYP-1 prototype of ATIDEP. It covers the functional and non-functional requirements that were implemented and tested during Phase 1. It is intended for the supervisor, external examiner, and development team.

### 1.2 Scope
ATIDEP is an open-source platform that automates the detection engineering workflow: it takes a threat report as input, extracts attacker behaviour, generates Sigma detection rules using a local LLM, and validates each rule against synthetic attack logs before marking it production-ready. A live dashboard tracks MITRE ATT&CK technique coverage.

FYP-1 delivers a working prototype covering:
- CTI ingestion from text reports and structured STIX/TAXII feeds
- LLM-based Sigma rule generation using local models (no cloud APIs)
- Automated multi-point validation gate on synthetic process creation logs
- MITRE ATT&CK coverage tracking across 44 techniques
- A web dashboard with five interactive views

FYP-1 does not cover: YARA rule generation, behavioural infostealer profiling (LSTM), threat-informed prioritisation, IOC extraction, multi-format rule export, or deployment on commercial SIEMs. These are planned for FYP-2.

### 1.3 Definitions and Abbreviations
- **ATIDEP**: Automated Threat-Informed Detection Engineering Platform
- **CTI**: Cyber Threat Intelligence
- **LLM**: Large Language Model
- **SIEM**: Security Information and Event Management
- **ATT&CK**: Adversarial Tactics, Techniques and Common Knowledge (MITRE framework)
- **Sigma**: An open detection rule format for SIEM systems
- **pySigma**: Python library for parsing and converting Sigma rules
- **STIX**: Structured Threat Information Expression (version 2.1)
- **TAXII**: Trusted Automated Exchange of Intelligence Information (version 2.1)
- **TTP**: Tactics, Techniques and Procedures
- **Strict gate**: Validation that requires the rule to catch both shown and hidden attack variants while staying quiet on benign commands
- **Single gate**: Validation that checks only the shown attack line and benign line (no hidden variant)

---

## 2. Overall Description

### 2.1 Product Perspective
ATIDEP addresses a gap identified in the literature: no open-source tool combines CTI extraction, LLM-based rule generation, automated functional testing of rules, and live ATT&CK coverage tracking in one pipeline. Existing tools (ThreatPilot, LLMCloudHunter, DetectionForge, RuleGenie, CardinalOps) each solve parts of the problem but none validates generated rules against synthetic logs before deployment.

Industry reports show that 79% of ATT&CK techniques have no detection coverage in enterprise SIEMs, 13% of deployed rules are broken, and new rules take over a week to write and deploy.

### 2.2 Product Functions (FYP-1 Scope)
1. Accept unstructured threat report text and extract technique, process image, and command line
2. Accept structured STIX/TAXII input to identify techniques associated with a threat group
3. Generate Sigma detection rules using a local LLM (Ollama, no cloud dependency)
4. Validate each rule through a four-check gate: syntax, shown attack, hidden variant, benign baseline
5. Track per-technique ATT&CK coverage and display it on an interactive dashboard
6. Store experiment results with full provenance (model, prompt version, temperature, seed, date)

### 2.3 User Classes
- **Detection Engineer**: Uses the pipeline to generate and validate Sigma rules from threat reports. Primary user of the Gate Validator and Pipeline views.
- **SOC Manager**: Reviews ATT&CK coverage and experiment results on the dashboard. Primary user of the Overview and Coverage Matrix views.
- **Researcher**: Runs experiments comparing models and prompts. Uses the CLI tools and reads the results files.

### 2.4 Operating Environment
- OS: Windows 11 Pro
- Hardware: Intel Core i7-14700, 32 GB RAM, NVIDIA RTX 4000 Ada 20 GB VRAM
- Runtime: Python 3.13, Ollama 0.40.7 (local LLM server), Node.js 18+
- Browser: Any modern browser for the dashboard

### 2.5 Constraints
- All LLM inference is local. No cloud APIs are used at any point.
- Only Windows process creation logs (Sysmon Event ID 1) are supported.
- Only Sigma rules are generated (no YARA, SPL, KQL, or EQL in FYP-1).
- Synthetic logs are hand-written templates, not generated from real malware execution.

### 2.6 Assumptions and Dependencies
- Ollama is installed and running at http://localhost:11434 with the required models pulled
- Python dependencies are installed: pySigma, pysigma-backend-sqlite, PyYAML, Flask
- For TAXII features: taxii2-client and stix2 are installed
- MITRE's TAXII server (https://attack-taxii.mitre.org) is reachable for live ingestion; the local file is the fallback

---

## 3. Functional Requirements

### 3.1 CTI Ingestion (FR-01 to FR-04)

**FR-01**: The system shall accept free-text threat report input and extract the MITRE ATT&CK technique ID, process image path, and attack command line.
- Input: Plain text paragraph describing an attack
- Output: Technique ID (e.g. T1547.001), process image (e.g. \reg.exe), command line
- Implementation: `dashboard/pipeline_service.py:extract_technique_and_command()`
- Matching: Priority 1 is known scenario signatures (5 patterns), Priority 2 is binary name matching across 44 techniques, Priority 3 is a default fallback

**FR-02**: The system shall connect to MITRE's ATT&CK TAXII 2.1 server and fetch attack-pattern, intrusion-set, and relationship objects.
- Endpoint: https://attack-taxii.mitre.org/api/v21/, collection "Enterprise ATT&CK"
- Implementation: `data/taxii_connector.py:fetch_all_types()`
- Timeout: 60 seconds, configurable

**FR-03**: The system shall map threat group names to their associated ATT&CK technique IDs using STIX "uses" relationships.
- Input: Group name (e.g. "APT29")
- Output: List of technique IDs, each marked as supported or unsupported by the pipeline
- Implementation: `data/taxii_ingest.py:ingest_by_group()`

**FR-04**: If the TAXII server is unreachable, the system shall fall back to the local attack_lookup.json file and continue operating without blocking the pipeline.
- Implementation: `data/taxii_ingest.py` returns source="local_fallback"
- Minimum threshold: If TAXII returns fewer than 500 techniques, the result is rejected

### 3.2 LLM Rule Generation (FR-05 to FR-08)

**FR-05**: The system shall generate Sigma detection rules using a locally hosted LLM via the Ollama HTTP API.
- Models: qwen2.5-coder:14b (primary, prompt v3b), qwen2.5-coder:7b (comparison, prompt v3a)
- Temperature: 0.2, context window: 4096 tokens
- No cloud APIs, no internet required for generation

**FR-06**: Each generated rule shall target the logsource category "process_creation" and product "windows".

**FR-07**: The prompt shall include the technique ID, a plain-language description, the process image, and one observed command line. The prompt shall instruct the model to generalize rather than copy the exact command line.
- Frozen prompts: llm/prompts/v3a.py (SHA-256: 4c8dbea1...) and llm/prompts/v3b.py (SHA-256: cba7e60a...)

**FR-08**: If a generated rule fails pySigma syntax validation, the system shall attempt one repair retry with the error message included in the prompt.

### 3.3 Validation Gate (FR-09 to FR-14)

**FR-09**: The system shall convert each Sigma rule to SQL using the pySigma SQLite backend.
- Implementation: `validator/runner.py:rule_to_sql()`
- A rule that fails conversion receives verdict SYNTAX_ERROR

**FR-10**: The system shall test each rule against three synthetic events per technique:
1. Shown event: the attack command line given to the model
2. Variant event: a hidden attack variant with altered values, flags, or paths
3. Benign event: a harmless near-miss execution of the same program

**FR-11**: The gate shall assign one of five verdicts (first match):
1. SYNTAX_ERROR: rule fails pySigma conversion
2. MISSED_SHOWN: rule does not fire on the shown attack line
3. NOISY: rule fires on the benign baseline
4. TOO_NARROW: rule fires on shown line but misses the hidden variant
5. PASS: rule passes all four checks

**FR-12**: Only rules with verdict PASS shall be considered production-ready.

**FR-13**: The strict gate (with hidden variant) shall be the primary metric for all reported results.

**FR-14**: The gate shall complete within 1 second per rule (suitable for a CI-style workflow).
- Measured: average 0.02-0.05 seconds per gate evaluation on the test hardware

### 3.4 Coverage Tracking (FR-15 to FR-17)

**FR-15**: The system shall maintain per-technique coverage status across all 44 techniques in 3 test sets.
- Output: coverage.csv, coverage.html, COVERAGE.md
- Implementation: `coverage/build_coverage.py`

**FR-16**: Each technique shall show: technique ID, official ATT&CK name, tactic(s), sets it appears in, best verdict across all tested configurations.
- ATT&CK names from: data/attack_lookup.json (706 techniques from MITRE STIX 2.1 bundle)

**FR-17**: The coverage template shall include both covered (PASS) and uncovered (non-PASS) techniques, with links to ATT&CK URLs.

### 3.5 Dashboard (FR-18 to FR-23)

**FR-18**: The system shall serve a web dashboard accessible at http://127.0.0.1:5000/app/.
- Backend: Flask (Python), REST JSON API
- Frontend: React 19, Vite 8, TypeScript, Tailwind CSS v4, shadcn/ui

**FR-19**: Overview view shall display: total techniques, coverage percentage, total rules tested, most recent run summary, SVG radar chart of tactic coverage, Set 3 benchmark bars.

**FR-20**: Coverage Matrix view shall display an interactive tactic-grouped grid of all 44 techniques with verdict badges, coverage progress bars per tactic, and expandable technique detail.

**FR-21**: Experiment Runs view shall list all recorded experiment runs with sortable columns: date, set, prompt, model, strict pass, single pass, syntax errors.

**FR-22**: Gate Validator view shall provide an interactive editor where users can paste a Sigma rule, select a test set and technique, and run the validation gate with live checklist results.

**FR-23**: Pipeline view shall provide: (a) a text input for threat reports with sample scenarios, (b) a STIX/TAXII structured ingestion panel with group loading, filtering, and technique ingestion, and (c) a four-stage stepper showing extraction, mapping, drafting, and validation.

### 3.6 Experiment Infrastructure (FR-24 to FR-27)

**FR-24**: The system shall support batch experiment runs across multiple models, prompts, sets, repeats, and temperatures via a single CLI command.
- Implementation: `llm/run_experiment.py`

**FR-25**: Each experiment run shall be saved to a timestamped folder under results/runs/ with the full CSV, individual YAML rule files, and a summary.

**FR-26**: Every reported result shall state: model, quantisation, prompt version, set number, gate type, temperature, number of repeats, and date.

**FR-27**: Set 3 access shall require the --final flag and a --reason string. Each Set 3 run shall be logged to results/set3_use_log.csv.

---

## 4. Non-Functional Requirements

### 4.1 Performance (NFR-01 to NFR-03)

**NFR-01**: Rule generation shall complete within 10 seconds per rule on the reference hardware (measured: 4-6 seconds for 7b, 5-10 seconds for 14b).

**NFR-02**: Gate validation shall complete within 1 second per rule (measured: 0.02-0.05 seconds).

**NFR-03**: The dashboard shall load and render within 3 seconds.

### 4.2 Reliability (NFR-04 to NFR-06)

**NFR-04**: The validation gate shall produce deterministic results for the same rule, technique, and set combination.

**NFR-05**: Identical seeds and temperatures shall produce identical LLM outputs (verified: runs 20261104_1503 and 20261106_1338 produced identical results).

**NFR-06**: If the TAXII server is unreachable, the system shall continue operating using local data without crashing.

### 4.3 Integrity (NFR-07 to NFR-09)

**NFR-07**: Frozen files (prompts, test sets, scoring logic) shall be verifiable against pre-registered SHA-256 hashes in FROZEN.md.
- Verification: `python tools/check_frozen.py`

**NFR-08**: Prompt files in llm/prompts/ shall never be modified after creation. New prompt versions get new files.

**NFR-09**: Set 3 techniques and rules shall be cryptographically locked in SET3_LOCK.md before any evaluation run.

### 4.4 Portability (NFR-10)

**NFR-10**: The system shall run on Windows 11 with Python 3.13, with no dependency on cloud services, paid APIs, or Docker (Docker is optional and not used in FYP-1).

### 4.5 Testability (NFR-11)

**NFR-11**: The system shall maintain an automated test suite covering all major components.
- Current: 110 pytest tests across 18 test files, all passing
- Categories: gate logic, scoring pipeline, prompt structure, dashboard API, coverage builder, demo scripts, TAXII connector, frozen file verification, Set 3 guards

### 4.6 Cost (NFR-12)

**NFR-12**: The entire platform shall run on open-source components at zero licensing cost. All LLM inference is local on consumer hardware.

---

## 5. Data Requirements

### 5.1 Input Data
- Threat report text (free-form English paragraphs)
- STIX 2.1 objects from MITRE ATT&CK TAXII server (attack-patterns, intrusion-sets, relationships)
- Local ATT&CK STIX 2.1 bundle (enterprise-attack.json, 55 MB, gitignored)

### 5.2 Generated Data
- Sigma rules in YAML format (one per technique per model per repeat)
- Experiment CSVs with per-rule verdicts and timing
- Coverage reports in CSV, HTML, and Markdown

### 5.3 Reference Data
- 44 MITRE ATT&CK technique definitions with synthetic events (3 sets)
- 36 reference SigmaHQ rules (12 per set) for sanity testing
- 706-technique ATT&CK lookup (data/attack_lookup.json)

---

## 6. External Interface Requirements

### 6.1 Ollama LLM API
- Protocol: HTTP POST to http://localhost:11434/api/generate
- Input: JSON with model name, prompt text, temperature, seed, num_ctx
- Output: Streamed JSON with generated text

### 6.2 MITRE TAXII 2.1 Server
- Endpoint: https://attack-taxii.mitre.org/api/v21/
- Protocol: TAXII 2.1 over HTTPS
- Library: taxii2-client (Python)
- Authentication: None (public server)

### 6.3 Dashboard REST API
| Endpoint | Method | Description |
|---|---|---|
| /api/overview | GET | Dashboard metrics |
| /api/tactics | GET | Tactic coverage breakdown |
| /api/techniques | GET | All 44 techniques with verdicts |
| /api/technique/{id} | GET | Technique detail with events and rules |
| /api/runs | GET | Experiment run list |
| /api/run/{folder} | GET | Experiment run detail |
| /api/gate | POST | Run validation gate on a rule |
| /api/pipeline/run | POST | Run full pipeline on threat text |
| /api/taxii/status | GET | TAXII server connectivity check |
| /api/taxii/groups | GET | Threat group list with coverage counts |
| /api/taxii/ingest | POST | Ingest techniques for a threat group |
| /api/taxii/refresh | POST | Refresh ATT&CK lookup from TAXII |
| /api/sets | GET | Available sets and technique lists |

---

## 7. Test Sets and Protocol

### 7.1 Set Definitions
| Set | Techniques | Purpose | Prompt Tuning | Status |
|---|---|---|---|---|
| Set 1 | 12 | Development and tuning | Yes | Closed after round 3 |
| Set 2 | 12 | Baseline (prompt v1 only) | No | Locked, never re-run |
| Set 3 | 20 | Final clean test | No | Pre-registered, run once |

### 7.2 Pre-Registration
All frozen configurations (models, prompts, scoring logic, test set definitions) are recorded with SHA-256 hashes in FROZEN.md before any Set 3 evaluation. This prevents post-hoc tuning on the final test.

---

## 8. Research Questions Addressed by FYP-1

**RQ1**: Can a local LLM write syntactically valid and effective Sigma rules from a single attack example?
- Evidence: Set 3 strict pass rates of 95.0% (14b) and 96.7% (7b) with improved prompts, versus 78.3% and 58.3% with baseline prompt v1.

**RQ2**: Does automated validation on synthetic logs reduce the number of broken and overly narrow rules marked ready for deployment?
- Evidence: Under baseline prompt v1, 37.5% of single-gate-approved rules for the 7b model failed on hidden variants. The strict gate caught these. Improved prompts reduced the gap to under 5%.

---

## 9. Traceability Matrix

| Requirement | Implementation | Test |
|---|---|---|
| FR-01 | pipeline_service.py | test_demo.py |
| FR-02 | taxii_connector.py | test_taxii_connector.py |
| FR-03 | taxii_ingest.py | test_taxii_ingest.py |
| FR-04 | taxii_ingest.py (fallback) | test_taxii_ingest.py:test_fallback_when_taxii_down |
| FR-05 | compare_models.py, run_experiment.py | test_prompts_v3.py |
| FR-09 | runner.py:rule_to_sql | test_scoring_pipeline.py |
| FR-10 | scoring.py:score_rule | test_scoring_pipeline.py |
| FR-11 | scoring.py:ScoreResult.verdict | test_strict_gate_sanity.py |
| FR-15 | build_coverage.py | test_coverage.py |
| FR-18 | app.py | test_dashboard.py |
| FR-22 | app.py:/api/gate | test_dashboard.py |
| FR-27 | run_experiment.py --final | test_set3_guard.py |
| NFR-07 | check_frozen.py | test_check_frozen.py |
| NFR-11 | tests/ (110 tests) | pytest |
