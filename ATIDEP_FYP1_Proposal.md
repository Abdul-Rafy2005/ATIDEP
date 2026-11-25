# Page 1

Final Year Project Proposal

Automated Threat-Informed Detection Engineering Platform (ATIDEP)

A Closed-Loop CTI-to-Detection Pipeline with Live ATT&CK Coverage
Intelligence

Session Fall 2026

Department of Computer Science & Cyber Security FAST School of Computing

FAST National University, Karachi Campus 18-09-2026

# Page 2

Project Registration

Project ID (for office use)\
Type of project \[X\] Traditional \[ \] Industrial \[ \] Continuing
Nature of project \[\] Development \[X\] Research & Development \[ \]
Research Sustainable Development Goals (SDGs) \[X\] Industry,
Innovation, and Infrastructure \[ \] Good Health and Well- Being \[ \]
Quality Education \[ \] Gender Equality \[ \] Decent Work and Economic
Growth \[ \] Climate Action Area of specialization \[X\] Cybersecurity
\[X\] Artificial Intelligence (AI) \[ \] Data Science and Analytics \[
\] IoT \[ \] Blockchain \[ \] Mobile App Development \[ \] Web
Development \[ \] Game Development \[ \] NLP \[ \] Other Project Group
Members Sr.# Reg.# Student Name CGPA Email ID Phone \# Signature (i)
23P-0625 Abdul Ahad (Group Leader) 3.16 p230625@nu.edu.pk +92 332
2888634\
(ii) 23P-0560 Abdul Rafy 3.38 p230560@nu.edu.pk

+92 301 8004047\
(iii) 23K-5544 Muhammad Owais 2.43 k235544@nu.edu.pk

+92 313 6862290

Project Abstract Security teams today rely heavily on manual work to
convert cyber threat intelligence (CTI) into detection rules that can
actually be deployed in a SIEM. This process is slow, inconsistent, and
has no proper way to check whether a rule works before it goes live.
Recent industry reports highlight the scale of this problem: on average,
79% of MITRE ATT&CK techniques have no detection coverage at all in
enterprise SIEMs, around 13% of the rules that are deployed are broken
and never trigger, and it can take security teams over a week to write,
test, and deploy a single new rule in response to an emerging threat. At
present, no open-source tool addresses this entire pipeline in one
place. This project proposes ATIDEP (Automated Threat-Informed Detection
Engineering Platform), an open-source system that takes a CTI report as
input and automatically extracts threat actor behaviour, generates Sigma
and YARA detection rules using a locally hosted LLM, and tests those
rules against synthetic attack logs before they can be marked
production-ready. The platform also maintains a live dashboard showing
ATT&CK coverage. In addition, it builds behavioural detection profiles
for infostealer malware, one of the fastest- growing malware categories
in 2025, using an LSTM model trained on sandboxed API call sequences.
This allows it to detect malware behaviour rather than relying only on
static signatures, which modern infostealers are specifically designed
to evade.

# Page 3

The methodology combines CTI extraction using NLP, rule generation using
a local LLM, automated rule validation, and behavioural malware
profiling into a single pipeline. Two research questions guide the
evaluation: whether automated validation reduces the number of broken
rules reaching production compared to the 13% industry baseline, and
whether behavioural profiling can detect infostealer variants that were
not part of its training data. Expected outcomes include a working
platform, a method for measuring ATT&CK coverage, and results on how
well automated validation and behavioural profiling perform.
Introduction Detection engineering is the process of turning cyber
threat intelligence into detection rules that can be deployed in
security monitoring tools such as SIEMs. It plays a central role in how
modern Security Operations Centres (SOCs) function. As the number of
adversary techniques documented in the MITRE ATT&CK framework keeps
growing, security teams are under more pressure to keep up, but the way
detection rules are actually written and deployed has stayed largely
manual. This is a real problem because when the detection pipeline is
slow or unreliable, attacker techniques go undetected in production,
which directly leads to breaches. Industry reports show that the current
situation is weak in several ways: many ATT&CK techniques have no
detection coverage at all, a significant number of deployed rules do not
work correctly, and new rules take too long to write and deploy when a
new threat emerges. This is where AI and computational approaches become
useful. Each step of the detection engineering process, extracting
structured threat behaviour from unstructured CTI reports, generating
correct detection rules, testing whether those rules actually work, and
recognising malware behaviour that tries to evade static signatures, is
a task that recent progress in NLP, large language models, and sequence
models like LSTMs can help automate. However, this only works if the
output of these models is properly validated rather than trusted
directly. Problem Statement The process of turning a CTI report into a
tested and deployed detection rule is currently manual, spread across
disconnected tools, and has no proper way to continuously check whether
the rules still work. This is not simply a case of missing tools,
several individual tools already exist that solve parts of this problem
(see the gap analysis below). The real gap is methodological: there is
no published or open-source approach that combines CTI-driven rule
generation, automated functional testing of those rules, and behavioural
malware detection that can resist evasion, all within a single closed
-loop system. There is also no established way to measure how much such
automation actually improves on the current manual process, for example,
against the industry-reported figure that 13% of deployed rules are
broken. Motivation The motivation behind this project is to build a
practical, open-source solution for the disconnected and mostly manual
detection engineering workflow described above. The project aims to:

# Page 4

• Reduce the manual effort needed to convert threat intelligence into
deployable detection rules. • Improve the reliability of detection rules
by validating them automatically before deployment. • Automate
time-consuming tasks such as CTI extraction, rule drafting, and coverage
tracking. • Give security teams a single, easy-to-use dashboard for
managing detection rules and viewing ATT&CK coverage. • Improve
detection of infostealer malware, which often evades signature-based
tools, through behavioural profiling instead. • Provide centralised,
live tracking of detection coverage and rule health , instead of relying
on fragmented, manually updated records.

Aims and Objectives The goal of this project is to design and build
ATIDEP, an end-to-end, open-source detection engineering platform that
closes the gap between threat intelligence and validated, deployed
detection rules. The main objectives are: • To design an NLP pipeline
that extracts IOCs, TTPs, and threat actor behaviours from unstructured
CTI reports, including implicit TTPs that are not explicitly tagged with
ATT&CK IDs. • To build an LLM-based rule generator that produces
syntactically and semantically correct Sigma and YARA rules from
structured CTI data. • To implement an automated validation gate that
tests generated rules against synthetic logs before they can be marked
production-ready, and to measure how well this reduces broken rules
compared to the published 13% industry baseline.\
• To build a live dashboard that tracks MITRE ATT&CK coverage per
technique and shows how coverage changes over time. • To design and
train an LSTM-based behavioural profiling model that generates Sigma
rules for infostealer malware families from sandboxed API call
sequences, and to evaluate how well it detects variants not seen during
training. • To build a detection backlog prioritisation module that
ranks undetected techniques based on real-world attack prevalence rather
than CVSS score alone.

Scope of the Project This project covers the design and implementation
of all seven platform modules described in the Proposed Methodology
section: CTI ingestion and NLP extraction, LLM -based Sigma/YARA rule
generation, synthetic log generation and rule validation, live ATT&CK

# Page 5

coverage tracking, behavioural infostealer profiling, threat -informed
detection prioritisation, and a detection management dashboard. CTI
ingestion additionally includes a STIX/TAXII connector that pulls
technique and threat-group data from the MITRE ATT&CK TAXII 2.1
server; this identifies which techniques a given group uses so the
pipeline can generate rules for them. The command-line context needed
for rule generation (process image and arguments) comes from threat
reports or synthetic log templates, not from TAXII itself, since
STIX objects rarely carry observed command lines. Integration with
paid/commercial threat intelligence platforms remains out of scope. For
synthetic validation, the scope is limited to Windows Event Log and
Syslog data sources. For behavioural profiling, the scope is limited to
four infostealer malware families (LummaC2, Vidar, StealC, RedLine),
using publicly available samples from MalwareBazaar. Deployment on
commercial SIEM platforms, integration with them, and support for rule
formats beyond Sigma, YARA, Splunk SPL, KQL, and Elastic EQL export are
not part of this project's scope.

Proposed Methodology ATIDEP works as a closed-loop pipeline. A raw CTI
report, whether a narrative PDF/HTML document or structured intelligence
pulled via a STIX/TAXII connector (which maps threat groups to their
ATT&CK techniques), is ingested; structured threat behaviour is
extracted using NLP where the input is narrative text;
detection rules are generated by a locally hosted LLM, and those rules
are tested against synthetically generated attack logs before they are
allowed to reach deployment. A live ATT&CK coverage dashboard is updated
as this happens. In parallel, a separate behavioural profiling pipeline
submits infostealer malware samples to an isolated sandbox, extracts
their API call sequences, and trains an LSTM classifier to generate
detection rules based on behaviour rather than static signatures. The
methodology below is organised around the gap analysis and the seven
functional modules that make up the platform.

# Page 6

Gap Analysis -- Existing Tools The table below lists existing open
-source and commercial tools related to detection engineering and points
out what each one is missing. These gaps together are what ATIDEP is
designed to address. Existing Tool Gap ThreatPilot (2024) Extracts
ATT&CK TTPs from CTI reports, but does not generate detection rules,
infer implicit TTPs, or validate its output. LLMCloudHunter (2024)
Generates Sigma rules, but only from cloud-specific CTI. No synthetic
log testing, no ATT&CK coverage tracking, no malware profiling.
DetectionForge Generates Sigma/YARA rules from natural language using an
LLM, but has no CTI ingestion pipeline, no validation, and no coverage
measurement. RuleGenie (2025) Identifies redundant Sigma rules using
embeddings, but does not test whether rules actually work, does not
generate new rules from CTI, and has no infostealer module. CardinalOps
A commercial platform that measures ATT&CK coverage and broken rules,
but is closed source, costs \$50,000+ annually, and has no CTI-to-rule
pipeline or malware profiling MISP / OpenCTI CTI sharing and enrichment
platforms with no detection rule generation, testing, or coverage
tracking.

No open -source platform currently combines CTI extraction, LLM -based
rule generation, synthetic log validation, live ATT&CK coverage
tracking, and behavioural infostealer profiling into one pipeline.
ATIDEP is designed to close this gap.

# Page 7

Core Modules Module Description Module 1 CTI Ingestion & NLP Extraction.
Uses spaCy NER and a fine-tuned BERT model to extract IOCs, TTPs, threat
actor names, and affected platforms from PDF/HTML threat reports.
Structured threat intelligence can also be ingested directly via a
STIX/TAXII connector that maps threat groups to ATT&CK technique IDs;
the pipeline then generates rules for each supported technique. The
command-line context for rule generation comes from reports or
synthetic log templates, since STIX objects rarely include observed
command lines. An LLM reasoning layer is added on top to infer
implicit TTPs that are not explicitly tagged with ATT&CK IDs. Module 2
LLM Sigma & YARA Rule Generator. A locally hosted Mistral 7B model (run
through Ollama) generates detection rules from the structured extraction
output. Generated rules are checked for syntactic correctness using
pySigma and the YARA Python library. Module 3 Synthetic Log Generator &
Rule Validator (core research contribution). Generates synthetic attack
logs for each ATT&CK data source and runs the generated Sigma rules
against them. Rules that fail are quarantined and never reach
production. Module 4 Live ATT&CK Coverage Tracker. Keeps per-technique
coverage scores for all 200+ ATT&CK techniques and displays them as a
D3.js heat map, showing live coverage, how it changes over time, and
alerting on regressions. Module 5 Behavioural Infostealer Profiling
Engine. A Docker sandbox records API call sequences from malware
samples. An LSTM classifier learns behavioural profiles per malware
family and generates Sigma rules based on this behaviour rather than
static signatures. Module 6 Threat-Informed Detection Prioritisation.
Scores undetected ATT&CK techniques based on threat relevance, active
campaign data, and how much engineering effort each would take,
producing a prioritised detection backlog. Module 7 Detection Management
UI. A React dashboard for the rule library, version history, test
status, ATT&CK mapping, and exporting rules in multiple formats (Sigma
YAML, YARA, Splunk SPL, KQL, Elastic EQL).

Research Questions The project is guided by the following research
questions, each tied to a measurable outcome: • RQ1: Can a locally
deployed 7B-parameter LLM generate Sigma rules that are syntactically
and semantically correct from structured CTI extraction output, and how
does this compare to manually written ground truth? (Measured through
syntax pass rate, true-positive rate on synthetic logs, and
false-positive rate on benign logs.) • RQ2: Does automated synthetic log
validation reduce the number of broken detection rules that reach
production, compared to having no validation gate at all? This will be
measured against the 13% broken-rule baseline reported by CardinalOps. •
RQ3: Can behavioural profiling using LSTM models on sandbox API call
sequences generate YARA rules that detect infostealer variants not
present in the training data? (Measured through detection rate on
held-out Vidar and StealC samples.)

# Page 8

• RQ4: Does threat-intelligence-driven prioritisation produce a
detection backlog that aligns better with real-world attack techniques
than CVSS-sorted or random-order baselines? The system should provide
the following functional and non- functional requirements Functional
Requirements • Ingest CTI reports in PDF and HTML formats, and
structured threat intelligence via a STIX/TAXII connector (MITRE's
official ATT&CK TAXII 2.1 server), mapping threat groups to ATT&CK
technique IDs and extracting TTPs. IOC extraction (IPs, hashes,
domains) is future work, as IOCs are not used in process-creation
Sigma rules. • Automatically generate Sigma and YARA
detection rules from the extracted CTI data. • Automatically validate
generated rules automatically against synthetic attack logs before they
can be marked production-ready. • Show live, per-technique ATT&CK
coverage on an interactive dashboard. • Behaviourally profile
infostealer malware through sandboxed execution and generate
corresponding detection rules. • Prioritise the detection engineering
backlog based on threat relevance and engineering effort. • Export
validated rules in Sigma YAML, YARA, Splunk SPL, KQL, and Elastic EQL
formats. Non-Functional Requirements • The platform must run entirely on
open-source components at zero licensing cost, including local LLM
inference. • The synthetic log validation gate must complete within a
time budget suitable for a CI-style workflow. • Malware execution must
be isolated within a sandboxed environment to prevent any risk to the
host system or network. • The dashboard must remain responsive when
tracking coverage across the full set of 200+ ATT&CK techniques. • If an
external STIX/TAXII source is unreachable, the platform falls back to
manual PDF/HTML ingestion without blocking the pipeline. System
Architecture The proposed system follows a modular, service -oriented
architecture. The major layers/components are:

# Page 9

• Presentation Layer: A React.js dashboard for rule management, ATT&CK
coverage visualisation (using D3.js), and multi-format rule export. •
Application Layer: A Spring Boot orchestration API and Kafka event
pipeline that coordinates the STIX/TAXII ingestion connector (which
maps threat groups to techniques), NLP extraction, LLM rule
generation, synthetic log validation, and behavioural profiling
services (implemented in Python/Flask). • Data
Layer: PostgreSQL for persistent storage of CTI extractions, generated
rules, validation results, and coverage history, along with Redis for
caching and event-state management.

Individual Tasks The table below indicates individual tasks across the
three -member team, justifying the one - year effort split by role:
backend/ML integration (Abdul Rafy), governance and metrics (Abdul
Ahad), and malware/red-team analysis (Teammate B). Team Member Activity
Tentative Duration Abdul Rafy, Backend Developer Literature review of
CTI extraction and detection- rule generation approaches; design of the
Spring Boot orchestration API and Kafka event pipeline. Months 1 to 4
Abdul Rafy, Backend Developer Implementation of the pySigma/YARA
validation wrapper and the Module 3 synthetic log validator (primary
research contribution); prototype for CTI ingestion (PDF/HTML and
STIX/TAXII) and Sigma rule generation. Months 5 to 8

# Page 10

Abdul Rafy, Backend Developer React dashboard, Docker infrastructure, ML
service integration, and end-to-end testing. Months 9 to 12 Abdul Ahad,
Cyber Security Specialist Literature review of governance frameworks;
gap analysis documentation; Phase 1 proposal documentation. Months 1 to
4 Abdul Ahad, Cyber Security Specialist Development of the detection
prioritisation scoring rubric; mapping to NIST CSF and ISO 27001 A.12.4
controls; definition of coverage metrics (MTTD, rule decay rate). Months
5 to 10 Abdul Ahad, Cyber Security Specialist Detection lifecycle
governance policy; threat- informed prioritisation module; support for
thesis writing. Months 9 to 12 Muhammad Owais, Cyber Security Specialist
Manual TTP extraction to build the ground-truth corpus; study of ATT&CK
taxonomy for implicit TTP inference. Months 1 to 6 Muhammad Owais, Cyber
Security Specialist Infostealer sandbox analysis; preparation of LSTM
training data from the MalwareBazaar corpus; YARA correctness review.
Months 7 to 10 Muhammad Owais, Cyber Security Specialist Red-team
validation of generated rules against simulated attacks; support for the
final defence. Months 11 to 12

Gantt Chart The chart below graphically represents the tentative task
schedule across the 12-month project duration, showing which activities
run in parallel and which run in series. Task M1 M2 M3 M4 M5 M6 M7 M8 M9
M10 M11 M12 Literature review & gap analysis\
System architecture & methodology design\
Prototype: CTI ingestion, NLP extraction, first Sigma rule\
Phase 1 defence\
Full NLP pipeline & LLM rule generator\
Synthetic log validation gate (Module 3)\
Infostealer sandbox module & LSTM training\
ATT&CK coverage tracker & heat map\
React dashboard & prioritisation module\
Integration testing, red-team validation, thesis, final defence

# Page 11

Tools and Technologies Category Stack Backend Java 21, Spring Boot 3.x,
Apache Kafka, PostgreSQL, Redis ML / NLP Python 3.11, spaCy, HuggingFace
Transformers (BERT), PyTorch (LSTM), FastAPI LLM Inference Ollama
(local), Mistral 7B --- no paid API, runs on a laptop GPU Rule Tooling
pySigma, YARA-Python, Sigma specification v2.0; pySigma backends for
Splunk SPL, Microsoft Sentinel KQL, and Elastic EQL export Sandbox
Docker (isolated), Cuckoo-compatible API call extraction Frontend
React.js 18, D3.js (ATT&CK heat map) DevOps Docker, GitHub Actions (CI
for rule tests) Data Sources MalwareBazaar (malware samples), MITRE
ATT&CK TAXII feed, public CTI reports; taxii2-client and stix2 (Python)
for STIX/TAXII ingestion

Expected Deliverables • A working end-to-end ATIDEP platform covering
all seven modules, deployable through Docker Compose. • A locally hosted
LLM-based Sigma/YARA rule generation pipeline with automated syntactic
and functional (synthetic log) validation. • A live MITRE ATT&CK
coverage dashboard with per-technique tracking and drift alerts.\
• An LSTM-based behavioural infostealer detection module, evaluated
against held-out malware variants. • A threat-informed detection backlog
prioritisation module, aligned to NIST CSF and ISO 27001 A.12.4 control
mapping. • Empirical results for RQ1 to RQ4, including the broken-rule
interception rate measured against the published 13% industry baseline.
• A completed FYP thesis document, along with Phase 1 and Phase 2
defence presentations.

References \[1\] CardinalOps, "State of SIEM Detection Risk," 5th Annual
Report, Jun. 2025. \[Online\]. Available:
https://cardinalops.com/wp-content/uploads/2025/06/25-CardinalOps-2025-State-
of-SIEM-Report.pdf

# Page 12

\[2\] Anvilogic and SANS Institute, "2025 State of Detection Engineering
Report," Feb. 2025. \[Online\]. Available:
https://www.anvilogic.com/report/state-of-detection-engineering\
\[3\] IBM, "IBM X -Force Threat Intelligence Index 2025," IBM
Corporation, Armonk, NY, USA, Apr. 2025. \[4\] Recorded Future, "2025
Identity Threat Landscape Report," Recorded Future, Somerville, MA, USA,
Mar. 2026. \[Online\]. Available:
https://www.recordedfuture.com/blog/identity- trend-report-march-blog
\[5\] Vectra AI, "What Is Infostealer Malware and How Does It Work?"
Vectra AI, San Jose, CA, USA. \[Online\]. Available:
https://www.vectra.ai/topics/infostealers \[6\] "CTI-REALM: Benchmark to
Evaluate Agent Performance on Security Detection Rule Generation
Capabilities," arXiv:2603.13517, Mar. 2026. \[7\] M. Xu, H. Wang, J.
Liu, X. Li, Z. Yu, W. Han, H. W. Lim, J. S. Dong, and J. Zhang,
"ThreatPilot: Attack-Driven Threat Intelligence Extraction,"
arXiv:2412.10872, Dec. 2024. \[8\] Y. Schwartz, L. Ben-Shimol, D.
Mimran, Y. Elovici, and A. Shabtai, "LLMCloudHunter: Harnessing LLMs for
Automated Extraction of Detection Rules from Cloud -Based CTI,"
arXiv:2407.05194, 2024. \[9\] A. Shukla, P. A. Gandhi, Y. Elovici, and
A. Shabtai, "RuleGenie: SIEM Detection Rule Set Optimization,"
arXiv:2505.06701, May 2025.
