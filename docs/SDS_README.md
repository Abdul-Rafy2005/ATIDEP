# ATIDEP Software Design Specification (SDS)

Project: Automated Threat-Informed Detection Engineering Platform (ATIDEP)
Session: Fall 2026, Final Year Project (Phase 1)
Department: Computer Science and Cyber Security, FAST-NUCES Karachi
Supervisor: Dr. Shahbaz Siddiqui
Team: Abdul Rafy (23P-0560), Abdul Ahad (23P-0625), Muhammad Owais (23K-5544)

---

## 1. Introduction

### 1.1 Purpose
This document describes the software design of the FYP-1 prototype of ATIDEP. It covers system architecture, module decomposition, data flow, component interfaces, and design decisions. It is a companion to the SRS and is intended for the supervisor, examiner, and any developer extending the system in FYP-2.

### 1.2 Design Philosophy
- **Local-first**: All LLM inference runs on consumer hardware via Ollama. No cloud APIs at any point.
- **Frozen experiments**: Prompts, test sets, and scoring logic are version-controlled with SHA-256 hashes. Results are reproducible.
- **Modular pipeline**: Each stage (ingestion, generation, validation, coverage) is an independent Python module that can be tested and run separately.
- **Fallback by default**: If a network resource (TAXII server, Ollama) is unavailable, the system degrades to local data rather than failing.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
                        +--------------------+
                        |   Presentation     |
                        |   Layer            |
                        |                    |
                        | React 19 + Vite 8  |
                        | TypeScript         |
                        | Tailwind CSS v4    |
                        | shadcn/ui          |
                        +--------+-----------+
                                 |
                            REST JSON API
                                 |
                        +--------+-----------+
                        |   Application      |
                        |   Layer            |
                        |                    |
                        | Flask (Python)     |
                        | Pipeline Service   |
                        | Data Loader        |
                        | TAXII Ingest       |
                        +--------+-----------+
                                 |
              +------------------+------------------+
              |                  |                   |
     +--------+-------+ +-------+--------+ +--------+-------+
     | LLM Layer      | | Validation     | | Data Layer     |
     |                | | Layer          | |                |
     | Ollama API     | | pySigma        | | ATT&CK Lookup  |
     | Prompt Builder | | SQLite Backend | | STIX/TAXII     |
     | YAML Extractor | | Scoring Module | | Synthetic Logs |
     +----------------+ +----------------+ | Coverage CSV   |
                                           +----------------+
```

### 2.2 Layer Description

**Presentation Layer** (dashboard/frontend/)
- React 19 single-page application with five views
- Communicates with the backend exclusively through REST JSON API calls
- Dark mode enabled by default, theme toggle for light mode
- Design system: 40+ CSS tokens, Geist font, cyan accent palette

**Application Layer** (dashboard/)
- Flask server with REST endpoints for data retrieval and pipeline execution
- Pipeline service orchestrates extraction, rule generation, and gate validation
- Data loader aggregates results from run folders, coverage CSVs, and technique definitions
- TAXII ingest module bridges the TAXII connector to the pipeline's technique set

**LLM Layer** (llm/)
- Prompt templates frozen as Python files with SHA-256 hashes
- Ollama HTTP client for local model inference (temperature, seed, context window)
- YAML extraction and syntax checking
- Experiment runner for batch evaluation across models, prompts, and sets

**Validation Layer** (validator/)
- pySigma SQLite backend converts Sigma rules to SQL
- In-memory SQLite table ("logs") evaluates each rule against synthetic events
- Scoring module returns structured results with verdict, timing, and error messages

**Data Layer** (data/, generator/, results/)
- ATT&CK technique lookup (706 entries from STIX 2.1 bundle)
- TAXII connector for live technique and group data
- Synthetic event generators for three test sets (44 techniques total)
- Experiment results stored in timestamped run folders

---

## 3. Module Design

### 3.1 CTI Ingestion Module

#### 3.1.1 Text Extraction (dashboard/pipeline_service.py)

```
extract_technique_and_command(text, supported_techs)
  Input:  text (str), supported_techs (dict)
  Output: (technique_id: str, command_line: str)
```

Design: Three-tier matching strategy.
1. Priority 1: Five hard-coded scenario signatures for common techniques (reg.exe+Run, procdump+lsass, net use+C$, gpresult, vssadmin). These handle the demo scenarios reliably.
2. Priority 2: Iterate all 44 supported techniques; match the binary name (basename of Image field) against the input text, then extract the command line via regex.
3. Priority 3: Default to T1547.001 as a safe fallback.

Rationale: A full NLP extraction pipeline (spaCy NER, BERT) is planned for FYP-2. The FYP-1 extractor is a pattern-based prototype sufficient for the demo and the 44 supported techniques.

#### 3.1.2 STIX/TAXII Connector (data/taxii_connector.py)

```
fetch_all_types(root, title, timeout)
  Output: {"attack-pattern": [...], "intrusion-set": [...], "relationship": [...]}

build_group_techniques(all_objects)
  Output: {"APT29": ["T1547.001", "T1059.001", ...], ...}
```

Design: Uses taxii2-client to connect to the MITRE TAXII 2.1 API root. Fetches three STIX object types with server-side pagination (500 per page). Builds group-to-technique mappings by walking "uses" relationships from intrusion-set source_ref to attack-pattern target_ref. Skips revoked and deprecated objects.

Fallback: Socket timeout of 60 seconds. If any network error occurs, callers receive an exception and fall back to local data.

#### 3.1.3 Structured Ingestion (data/taxii_ingest.py)

```
ingest_by_group(group_name, timeout)
  Output: {source, group, total_techniques, supported_techniques, techniques: [...]}
```

Design: Calls taxii_connector.fetch_all_types(), builds the group map, then filters the requested group's techniques against the pipeline's supported set (the union of T1, T2, T3 technique dictionaries). Returns each technique with its support status and set number.

Fallback: If list_groups() returns None (TAXII unreachable), returns all 44 supported techniques with source="local_fallback".

### 3.2 LLM Rule Generation Module (llm/)

#### 3.2.1 Prompt Architecture

Five frozen prompt versions exist. The two active prompts for FYP-1 are:

**v3a** (for qwen2.5-coder:7b): Concise prompt. Gives the technique ID, description, process image, and one command line. Instructs the model to pick one keyword or flag that separates the attack from normal use. Enforces a token budget to prevent verbose output.

**v3b** (for qwen2.5-coder:14b): Chain-of-thought scratchpad prompt. Instructs the model to write `# keep:` and `# ignore:` comment lines before the YAML, explicitly listing which parts of the command to generalize and which to drop. This forces the model to reason about generalization before writing the rule.

#### 3.2.2 Ollama Client (llm/compare_models.py)

```
ask_ollama(prompt, model, temperature, seed, num_ctx)
  Sends HTTP POST to http://localhost:11434/api/generate
  Streams response tokens and concatenates the full text
  Returns: (response_text, elapsed_seconds, tokens_per_second)
```

Design decisions:
- Streaming mode for accurate timing measurement
- Temperature 0.2 (not 0) to allow minor variation across repeats while keeping output mostly deterministic
- Seed 100 as the default for reproducibility
- Context window 4096 tokens (sufficient for Sigma rules, which are typically 20-40 lines)

#### 3.2.3 YAML Extraction (llm/compare_models.py)

```
extract_yaml(response_text)
  Strips markdown fences, comments, and non-YAML text
  Returns: clean YAML string or None
```

Design: Models sometimes wrap output in markdown code fences or add explanatory text. The extractor finds the first `title:` line and takes everything from there to the end, stripping fences and leading/trailing whitespace.

#### 3.2.4 Experiment Runner (llm/run_experiment.py)

```
python llm/run_experiment.py --set 3 --prompt v3b --models qwen2.5-coder:14b
    --repeats 3 --temperature 0.2 --seed 100 --final --reason "FYP-1 evaluation"
```

Design: Unified CLI for all experiment runs. Creates a timestamped folder (e.g. results/runs/20261124_0900_set3_v3b/). Iterates over models x techniques x repeats. Saves each rule YAML, scores it, and writes a summary CSV. The --final flag is required for Set 3 access and logs the run to set3_use_log.csv.

### 3.3 Validation Gate Module (validator/)

#### 3.3.1 Rule-to-SQL Translation (validator/runner.py)

```
rule_to_sql(rule_yaml)
  Uses pySigma SigmaSQLiteBackend to convert Sigma YAML to SQL
  Returns: list of SQL query strings
  Raises: on syntax error

rule_matches(rule_yaml, event)
  Creates in-memory SQLite table "logs" with FIELDS columns
  Inserts the event as one row
  Runs the SQL queries from rule_to_sql
  Returns: True if any query returns a row
```

Design: The SQLite backend was chosen because it needs no external database, runs in-memory, and provides deterministic results. The 10 FIELDS (Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName, User, IntegrityLevel, Description, Product, Company) match Sysmon Event ID 1 process creation.

#### 3.3.2 Scoring Module (llm/scoring.py)

```
score_rule(set_num, technique_id, rule_yaml)
  Loads the three synthetic events for the technique
  Runs rule_matches three times (shown, variant, benign)
  Returns: ScoreResult(syntax_ok, fires_shown, fires_variant, fires_benign,
           single_pass, strict_pass, verdict, error)
```

Verdict logic (first match):
1. syntax_ok == False -> SYNTAX_ERROR
2. fires_shown == False -> MISSED_SHOWN
3. fires_benign == True -> NOISY
4. fires_variant == False -> TOO_NARROW
5. All checks pass -> PASS

#### 3.3.3 Synthetic Event Generation (generator/)

Each test set defines techniques as Python dictionaries:

```python
TECHNIQUES3 = {
    "T1615": {
        "image": "C:\\Windows\\System32\\gpresult.exe",
        "malicious": "gpresult.exe /z /user student",
        "variant": "gpresult.exe -z -user admin",
        "benign": "gpresult.exe /r",
        "rule_file": "proc_creation_win_gpresult_discovery.yml",
    },
    ...
}
```

The `make_triple3(tech_id)` function builds three complete Sysmon-style events from each technique's fields, filling in default values for ParentImage, User, IntegrityLevel, etc.

Design decisions:
- Variants alter flag format (-z vs /z), argument values (student vs admin), or program aliases (net.exe vs net1.exe)
- Benign events use the same program but harmless arguments (gpresult.exe /r is a normal query)
- One benign event per technique (a known limitation; real environments would need many more)

### 3.4 Coverage Module (coverage/)

#### 3.4.1 Coverage Builder (coverage/build_coverage.py)

```
Reads: results/runs/ (experiment CSVs), data/attack_lookup.json
Writes: coverage.csv, coverage.html, COVERAGE.md, README.md
```

Design: Scans all experiment run folders. For each technique, finds the best verdict across all configurations. Joins with the ATT&CK lookup for official names and tactics. Outputs three formats:
- CSV: Machine-readable, 44 rows with technique ID, name, tactics, sets, best verdict
- HTML: Visual report with colored verdict badges, grouped by tactic
- Markdown: Text summary with covered and uncovered technique lists

### 3.5 Dashboard Module (dashboard/)

#### 3.5.1 Backend (dashboard/app.py)

Flask application with two routing groups:
1. HTML page routes (legacy Flask templates, still accessible at /)
2. REST JSON API routes (/api/*) consumed by the React frontend

The React SPA is served from dashboard/frontend/dist/ at /app/.

#### 3.5.2 Data Loader (dashboard/data_loader.py)

Aggregates data from multiple sources into the JSON structures the API returns:
- Scans results/runs/ for experiment metadata and results
- Reads coverage.csv for per-technique coverage
- Reads attack_lookup.json for official ATT&CK names and tactics
- Reads technique definitions from generator modules for event data

#### 3.5.3 Frontend Architecture (dashboard/frontend/)

```
src/
  App.tsx          - Router, sidebar, header, theme toggle
  index.css        - Design system: 40+ CSS tokens, dark/light themes
  types/index.ts   - TypeScript interfaces for all API responses
  components/
    Header.tsx     - Top bar with search, Ollama status, theme toggle
    Sidebar.tsx    - Navigation with always-dark zinc-950 sidebar
    ui/
      metric-card.tsx   - Reusable metric display card
      verdict-badge.tsx - Verdict-colored badge and accent utilities
  views/
    OverviewView.tsx       - Radar chart, metric cards, benchmark bars
    CoverageMatrixView.tsx - Tactic-grouped technique grid
    RunsView.tsx           - Sortable experiment table
    GateValidatorView.tsx  - Interactive rule testing workbench
    PipelineView.tsx       - Full pipeline with TAXII ingestion panel
```

Design system tokens (defined in index.css):
- Surfaces: --panel, --panel-inset, --panel-hover
- Text: --fg, --fg-secondary, --fg-muted
- Borders: --edge, --edge-hover, --subtle
- Brand: --brand, --brand-hover, --brand-fg, --brand-muted, --brand-edge
- Verdicts: --pass, --narrow, --noisy, --critical (each with -muted and -edge variants)
- Code blocks: --code-bg, --code-fg, --code-edge, --code-muted

---

## 4. Data Flow Diagrams

### 4.1 Text Report Pipeline

```
User enters threat report text
        |
        v
[Extract Technique & Command]  -->  technique_id, process_image, command_line
        |
        v
[Generate Sigma Rule via LLM]  -->  rule_yaml (from Ollama)
        |
        v
[Validate via Gate]
  |-- rule_to_sql(rule_yaml)        -->  SQL queries
  |-- rule_matches(rule, shown)     -->  fires_shown (bool)
  |-- rule_matches(rule, variant)   -->  fires_variant (bool)
  |-- rule_matches(rule, benign)    -->  fires_benign (bool)
        |
        v
[Assign Verdict]  -->  PASS / TOO_NARROW / NOISY / MISSED_SHOWN / SYNTAX_ERROR
        |
        v
[Return Result]  -->  JSON to dashboard or CSV to run folder
```

### 4.2 TAXII Ingestion Pipeline

```
User selects threat group (e.g. APT29) in dashboard
        |
        v
[Fetch from TAXII]  -->  attack-patterns, intrusion-sets, relationships
        |
        v
[Build Group Map]   -->  {"APT29": ["T1547.001", "T1059.001", ...]}
        |
        v
[Filter to Supported]  -->  techniques with synthetic logs in sets 1/2/3
        |
        v
[Return to Dashboard]  -->  technique list with support status and set numbers
```

### 4.3 Experiment Batch Pipeline

```
CLI: run_experiment.py --set 3 --prompt v3b --models 14b --repeats 3
        |
        v
[Create Run Folder]  -->  results/runs/20261124_0900_set3_v3b/
        |
        v
For each model x technique x repeat:
  |-- [Build Prompt]       -->  technique + description + command + examples
  |-- [Call Ollama]        -->  raw LLM response text
  |-- [Extract YAML]      -->  clean Sigma rule
  |-- [Score Rule]         -->  ScoreResult with verdict
  |-- [Save Rule File]    -->  model_name/technique_repeat.yml
        |
        v
[Write Summary CSV]  -->  all results with verdicts, timing, tokens/sec
        |
        v
[Print Summary]  -->  strict pass count, single pass count, syntax errors
```

---

## 5. Database and Storage Design

FYP-1 uses file-based storage only. No relational database is used.

### 5.1 Storage Layout

| Path | Format | Contents | Persistence |
|---|---|---|---|
| data/attack_lookup.json | JSON | 706 ATT&CK techniques | Checked in, rebuilt from STIX |
| data/enterprise-attack.json | JSON | 55 MB STIX 2.1 bundle | Gitignored, downloaded once |
| data/enterprise-attack-taxii.json | JSON | TAXII fetch cache | Gitignored, rebuilt on refresh |
| coverage/coverage.csv | CSV | 44-row coverage matrix | Regenerated by build_coverage.py |
| results/runs/{timestamp}/ | Folder | Per-run YAML rules and CSV | Append-only, never modified |
| results/set3_use_log.csv | CSV | Audit log of Set 3 runs | Append-only |
| FROZEN.md | Markdown | Pre-registered SHA-256 hashes | Never modified after creation |
| SET3_LOCK.md | Markdown | Cryptographic lock of Set 3 files | Never modified |

### 5.2 In-Memory Storage

The validation gate uses an in-memory SQLite database created fresh for each rule evaluation. The table schema:

```sql
CREATE TABLE logs (
    Image TEXT,
    CommandLine TEXT,
    ParentImage TEXT,
    ParentCommandLine TEXT,
    OriginalFileName TEXT,
    "User" TEXT,
    IntegrityLevel TEXT,
    Description TEXT,
    Product TEXT,
    Company TEXT
);
```

One row is inserted per evaluation (the shown, variant, or benign event). The pySigma-generated SQL query runs against this table. The database is discarded after each evaluation.

---

## 6. Interface Design

### 6.1 API Contract

All API responses are JSON. Error responses use HTTP status codes:
- 200: Success
- 400: Missing or invalid request body
- 404: Resource not found
- 500: Internal server error
- 503: External service unavailable (TAXII)

Example request/response for the gate endpoint:

```
POST /api/gate
Content-Type: application/json

{
    "rule_yaml": "title: Test\nlogsource:\n  category: process_creation\n  product: windows\ndetection:\n  selection:\n    Image|endswith: '\\gpresult.exe'\n  condition: selection\nlevel: low",
    "set": 3,
    "technique": "T1615"
}

Response:
{
    "syntax_ok": true,
    "fires_shown": true,
    "fires_variant": false,
    "fires_benign": true,
    "single_pass": false,
    "strict_pass": false,
    "verdict": "NOISY",
    "error": null,
    "reason": "Fired on harmless near-miss baseline commands"
}
```

### 6.2 TAXII Ingestion API

```
POST /api/taxii/ingest
Content-Type: application/json

{"group": "APT29"}

Response:
{
    "source": "taxii",
    "group": "APT29",
    "total_techniques": 42,
    "supported_techniques": 8,
    "techniques": [
        {"id": "T1547.001", "name": "Registry Run Keys / Startup Folder", "supported": true, "set": 1},
        {"id": "T1583.001", "name": "Domains", "supported": false, "set": null},
        ...
    ]
}
```

---

## 7. Design Decisions and Rationale

### 7.1 Why SQLite for validation instead of a real SIEM?
pySigma can target many backends (Splunk, Elastic, Sentinel). We chose SQLite because:
- Zero external dependencies (Python standard library)
- Deterministic results (no network, no indexing delays)
- Sub-millisecond execution (measured 0.02-0.05s per rule)
- Sufficient for process creation field matching, which is our only log type

### 7.2 Why local LLMs instead of cloud APIs?
- Zero cost (runs on the lab GPU)
- Reproducible (same model weights, same seed, same output)
- No data leaves the machine (important for security research)
- Demonstrates that consumer hardware is sufficient for detection engineering

### 7.3 Why frozen prompts with SHA-256 hashes?
Prompt engineering is iterative. Without version control, it is easy to accidentally change a prompt and invalidate earlier results. Freezing prompts as named files with hashes ensures:
- Any modification is detected by tools/check_frozen.py
- Results always reference a specific, verifiable prompt version
- Set 3 results cannot be improved by post-hoc prompt tuning

### 7.4 Why three test sets instead of one?
- Set 1 (development): Used freely for prompt iteration. Scores are practice numbers.
- Set 2 (baseline): Run once with prompt v1 to establish a baseline. Locked afterward because prompt v2 guidance was written after seeing Set 2 failures.
- Set 3 (final test): Fresh techniques, pre-registered, run once. The only clean accuracy claim.

This prevents the common research mistake of tuning on the test set and reporting inflated scores.

### 7.5 Why file-based storage instead of PostgreSQL?
FYP-1 is a prototype with 44 techniques and 16 experiment runs. The data volume is small (under 100 MB total). Files are:
- Easy to inspect (CSV, JSON, YAML)
- Easy to version control (git tracks changes)
- Easy to reproduce (copy the folder)
- Sufficient for the prototype scope

PostgreSQL is planned for FYP-2 when the system handles hundreds of techniques and persistent rule management.

### 7.6 Why React + Vite instead of Flask templates?
The legacy Flask templates served the initial prototype. The React frontend was built for:
- Interactive features (live gate testing, sortable tables, expandable details)
- Dark/light theme toggle with CSS token system
- Responsive layout (phone to widescreen)
- Component reuse (verdict badges, metric cards)

Both interfaces remain available: React at /app/ and legacy Flask at /.

---

## 8. Security Considerations

- No real malware or secrets are stored in the repository. Synthetic logs are harmless text strings.
- No authentication on the dashboard (it runs on localhost only).
- TAXII connections use HTTPS to MITRE's public server. No authentication tokens are needed.
- Ollama runs on localhost:11434 with no authentication.
- The .gitignore excludes large STIX bundles and TAXII cache files.
- Frozen file hashes prevent tampering with experimental configurations.

---

## 9. Known Limitations and FYP-2 Scope

| Limitation | FYP-2 Plan |
|---|---|
| Only process creation logs | Add registry, file, network event types |
| Pattern-based text extraction | Replace with spaCy NER and BERT |
| Hand-written synthetic logs | Generate from ATT&CK procedure examples |
| One benign event per technique | Multiple benign baselines |
| No YARA rules | Add YARA generation and testing |
| No IOC extraction | Extract IPs, hashes, domains from reports |
| No obfuscation testing | Add encoded, renamed, and obfuscated variants |
| File-based storage | Migrate to PostgreSQL |
| No authentication | Add user authentication for the dashboard |
| No multi-format export | Export Sigma, Splunk SPL, KQL, Elastic EQL |
| No behavioural profiling | LSTM on sandbox API call sequences |
| No prioritisation | Threat-informed detection backlog ranking |

---

## 10. Deployment

### 10.1 Development Setup
```powershell
cd C:\ATIDEP
pip install pySigma pysigma-backend-sqlite pyyaml flask
pip install taxii2-client stix2    # for TAXII features
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b
python data/build_attack_lookup.py
cd dashboard/frontend && npm install && npm run build
```

### 10.2 Running
```powershell
# Terminal 1: Flask backend
python dashboard/app.py

# Terminal 2: Vite dev server (or use the built files)
cd dashboard/frontend && npm run dev

# Browser: http://localhost:5173 (dev) or http://127.0.0.1:5000/app/ (production)
```

### 10.3 Testing
```powershell
python -m pytest tests/ -v         # 110 tests
python tools/check_frozen.py       # Verify frozen file hashes
python validator/test_real.py      # Reference rules against logs
```
