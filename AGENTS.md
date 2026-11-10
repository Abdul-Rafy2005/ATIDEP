# Project context: ATIDEP (FYP-1 prototype)

## What this project is
ATIDEP = Automated Threat-Informed Detection Engineering Platform. Final year project at the National University of Computer and Emerging Sciences (FAST), Fall 2026. Supervisor: Dr. Shahbaz Siddiqui.
Team: Abdul Rafy (backend and AI, owns this code), Muhammad Owais (malware sandbox, TTP ground truth), Abdul Ahad (governance, coverage template).
Idea: take a threat report, find the attacker behaviour, let a local LLM write a Sigma detection rule, and test every rule on synthetic logs before it is marked ready. The test step (we call it the gate) is our main research contribution (Module 3).

## FYP-1 deliverables (due about two months after early October 2026)
1. Prototype: a thin working slice. Technique in, rule out, pass or fail.
2. MITRE ATT&CK coverage template: technique, rule, validation status. Not built yet.
3. LLM testing: how well local LLMs write correct Sigma rules, measured with our gate. In progress.
This code covers deliverables 1 and 3 and will feed deliverable 2.
Research questions this code gives evidence for: RQ1 (can a local LLM write correct Sigma rules?) and RQ2 (does automated validation reduce broken rules?).

## Environment
Windows 11 lab PC (Dell Precision 3680, i7-14700, 32 GB RAM, RTX 4000 Ada 20 GB). Repo folder: C:\ATIDEP. Python 3.13, PowerShell.
Dependencies: pySigma, pysigma-backend-sqlite, PyYAML. No cloud APIs. Ollama runs locally at http://localhost:11434.
Models in Ollama: mistral-rules (jcordon5/Mistral-7B-cybersecurity-rules, converted by us to GGUF Q8_0), mistral:7b, qwen2.5-coder:7b, qwen2.5-coder:14b.

## Code map
- download_rules.py: downloads 12 real SigmaHQ rules (set 1) to data/sigmahq_rules/, real test logs for 7 of them to data/sigmahq_test_logs/, writes results/techniques.csv.
- download_rules_set2.py: same for set 2: data/sigmahq_rules_set2/, data/sigmahq_test_logs_set2/, results/techniques_set2.csv.
- generator/generate.py: BASE (default event fields), TECHNIQUES (set 1: image, malicious and benign command lines), build_event(), make_pair(tech) returns (malicious_event, benign_event). Running it writes data/synthetic_logs/.
- generator/techniques_set2.py: TECHNIQUES2 (image, malicious, variant, benign), DESCRIPTIONS2, make_triple(tech) returns (shown_event, variant_event, benign_event).
- validator/runner.py: FIELDS list (Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName, User, IntegrityLevel, Description, Product, Company). rule_to_sql(rule_yaml) uses the pySigma SQLite backend and raises on a bad rule. load_event(path). rule_matches(rule_yaml, event) runs the SQL on an in-memory SQLite table called logs.
- validator/gate.py: check_rule(rule_text, technique) returns (PASS or FAIL, reason) for set 1. Its main() checks the 12 real SigmaHQ rules and writes results/validation_results.csv.
- validator/test_real.py and validator/test_set2_real_rules.py: sanity tests. The real SigmaHQ rules must pass our logs.
- llm/compare_models.py: the set 1 experiment. Has DESCRIPTIONS, INSTRUCTIONS, EXAMPLES (this is prompt v1), build_prompt(), ask_ollama() (temperature 0, num_ctx 4096), extract_yaml(), evaluate(), safe(), main(). One repair retry when the syntax check fails. Saves each rule to results/model_outputs/<model name with : and / replaced by _>/<technique>.yml and writes a CSV.
- llm/compare_set2.py: wrapper. Points compare_models at set 2 and swaps in evaluate2.
- llm/rescore_saved.py: re-scores saved set 1 rule files without calling a model.
- results/: techniques*.csv, validation_results.csv, model_comparison*.csv, set2_comparison_*.csv, model_outputs/. Some CSVs were copied or renamed by hand, so look for them.

## How the gate works
Events are flat dictionaries using the FIELDS above (Sysmon event 1 style, Windows process creation only).
- syntax: pySigma can convert the rule to SQL.
- caught: set 1 means the rule fires on the shown malicious line. Set 2 means it fires on the shown line AND on a hidden variant of the same attack.
- quiet: the rule does not fire on a harmless near-miss line. A rule that never fires is also quiet, so quiet alone means nothing.
- PASS = syntax and caught and quiet.
Prompt v1: the model gets the technique id, a plain description, the process path and ONE observed command line, plus two example rules (T1016 and T1564.001). The goal is a rule that generalises, not one that copies the line.

## Test sets and protocol
- Set 1 (12 techniques, generator/generate.py) is the development set. Use it for prompt and code work.
- Set 2 (12 techniques, generator/techniques_set2.py) is the validation set. It was run once with prompt v1 as a baseline. Do NOT tune prompts on set 2 failures. A set 2 log or variant may be changed only if it is shown to be unfair, and the change must be written down.
- Set 3 does not exist yet. It will be the final locked test set with fresh techniques, run once with the frozen prompt.
- Every reported result must say: model, quantisation, prompt version, set and date.

## Results so far (prompt v1, one run each, temperature 0)
Set 1 (shown line only): qwen2.5-coder:14b 11 of 12 pass, qwen2.5-coder:7b 10, mistral-rules 10, mistral:7b 3 (7 had invalid syntax: it wrote condition: CommandLine|contains|all(selection)).
Set 2 (also needs the hidden variant): qwen2.5-coder:7b 2 of 12, qwen2.5-coder:14b 2, mistral-rules 0. Valid syntax: 11, 12, 12. No model fired on the harmless line. Both Qwen models passed the same two techniques (T1546.007 and T1485), where the variant differs only in a path value.
Speed: about 6 seconds per rule for qwen (7b about 62 tokens per second, 14b about 34), about 20 seconds for mistral-rules (it writes long explanations after the rule).
Earlier observations about mistral-rules: it invents ids, authors and references (a wrong related type once broke syntax). In set 1 it padded values with spaces and repeated the same YAML key several times (YAML keeps only the last one), so rules for T1053.005, T1003.001 and T1047 missed the attack.

## Known weaknesses of our test
Logs are hand-written templates, not generated from ATT&CK. Only process creation is covered. Each set has 12 techniques and each model was run once. Set 1 has one attack line per technique, so a rule that copies the line passes. Some set 2 variants may need knowledge the prompt does not give (for example bcdedit settings, forfiles -c versus /c). Public models may have seen SigmaHQ rules in training.

## Working rules
- Write simple, plain English in comments, docs and messages. No em dashes. No buzzwords. Do not claim anything we have not measured.
- Prefer small changes. Do not rewrite working files. Do not change gate behaviour or existing files in results/ unless asked.
- Only use the standard library, PyYAML and pySigma. Ask before adding anything else.
- No real malware or secrets in the repo. The logs are harmless text.
- Commands are for Windows PowerShell and Python 3.13.
- After any change, run the relevant script or test and show the output.
- Report any difference between this file and the repo.

## Update 2026-10-21: analysis of prompt v1 results
- On set 2 (strict gate), a gate that only checks the shown line would have approved 10, 9 and 6 of 12 rules for qwen2.5-coder:7b, qwen2.5-coder:14b and mistral-rules. The strict gate approved 2, 2 and 0. Main failure type is TOO_NARROW (rule depends on details of the one example).
- 9 or 10 of 12 rules per model have values padded with spaces. qwen 14b did not beat qwen 7b on set 2.
- mistral-rules is dropped as a candidate (kept for the report). mistral:7b is dropped. Working model: qwen2.5-coder:7b. qwen2.5-coder:14b is the larger comparison model.
- Archive of all prompt v1 results is in results/archive/prompt_v1/.
- Some set 2 variants need knowledge the prompt does not give (T1489 net1.exe, T1090 which port matters, T1490 other bcdedit setting, T1059 -c versus /c). Do not edit set 2 for this. Use it when designing set 3.
- Protocol change: set 1 now also has hidden variants and is the development set under the strict gate. Set 2 is the baseline for prompt v1 only. It is no longer a clean test for prompt v2, because the v2 guidance was written after seeing set 2 failures. A new set 3 will be the only final clean test.
- Prompt versions live in llm/prompts/ (v1 = original text, v2 = new). Every run is saved in its own folder under results/runs/.

## Update: prompt v2 results on set 1 (run folder results/runs/20261021_1511_set1_v2)
- Single and strict gate gave the same numbers for every model on set 1 under prompt v1, so the set 1 variants did not catch any narrow rule. Set 1 is saturated and cannot separate good prompts.
- Prompt v1 on set 1: qwen2.5-coder:7b 10, qwen2.5-coder:14b 11. Prompt v2 on set 1: qwen2.5-coder:7b 12, qwen2.5-coder:14b 8 (4 syntax errors, cause not yet known).
- Prompt v2 was written after the set 2 failures were seen, so set 1 scores for v2 are development scores, not accuracy claims. The accuracy claim will come from set 3.
- Running v2 on set 2 is not allowed in this phase.

## Update after variance runs
- Prompt v2 raised qwen 7B from 28 to 36 of 36 and lowered qwen 14B from 35 to 26 of 36 (temperature 0.2, 3 repeats, set 1).
- The 14B failures are YAML values read as a mapping (error "Unsupported type dict").
- Set 1 is at its ceiling and cannot show generalisation.
- A new set 3 will be the only clean final test.
- Only one run at a time.

## READ FIRST (added 2026-11-06)
- Read PROGRESS.md at the start of every task. When a task ends, add an entry: date, task name, DONE or BLOCKED, files created or changed, any WARN lines. If you stop because of quota or a crash, write exactly where you stopped.
- Only one person works on this code: Abdul Rafy. Antigravity replaced GitHub Copilot, whose quota ran out. Treat old Copilot notes as history.

## Where we are (2026-11-06, FYP-1 about 45 to 50% done)
Deliverables: 1 prototype (about 65%), 2 ATT&CK coverage template (about 10%), 3 LLM testing (about 65%).
Remaining: freeze prompt and model, build and run set 3 once, end-to-end demo, coverage template, results write-up and README.
Out of scope for FYP-1: dashboard, Kafka, Spring Boot, malware sandbox and LSTM, prioritisation, YARA, other log types, automatic log generation from ATT&CK, training our own model, real SIEM use.

## Results so far (our own runs)
- Set 1, temperature 0.2, 3 repeats, 36 rules per row, first-try strict gate (corrected 2026-11-10): qwen 7b prompt v1 7/36, v2 9/36, v2_1 11/36 (first-try single gate: 28, 36, 36). qwen 14b prompt v1 3/36, v2 8/36, v2_1 8/36 (first-try single gate: 35, 26, 36). Run 20261106_1338 (qwen 14b, v2 with repair hint): first-try strict 8/36, final strict 11/36.
- Cause of the 14b v2 failures: it wrote windash as a list item inside a contains|all list (error "Unsupported type: <class 'dict'>"). The right form is CommandLine|contains|windash|all: with a plain list. The retry could not fix it because the error gives no clue.
- The test suite now verifies that a copy of the shown line gives TOO_NARROW, and the corrected strict gate separates prompt versions on set 1.
- Set 2 (prompt v1, strict gate): qwen 7b 2/12, qwen 14b 2/12, mistral-rules 0/12. A gate checking only the shown line would have approved 10, 9 and 6. Most failures: rules that depend on details of the one example. Some set 2 variants need outside knowledge (T1489 net1.exe, T1090, T1490, T1059). Known, and not to be fixed by editing set 2.
- mistral-rules and mistral:7b are dropped as candidates (kept for the report). Models in use: qwen2.5-coder:7b (working model) and qwen2.5-coder:14b (comparison).
- Known bug in RESULTS_SUMMARY.md: the "final pass after repair" column could be lower than the first-try pass. Correct definition: final pass = first-try passes + repairs that fixed a first-try syntax failure.
- Known bug fixed 2026-11-10: set 1 strict gate was not applied in run summaries before this fix. Rescored in results/rescore_strict_all.md.

## Protocol
- Set 1 = development set (strict gate). Set 2 = baseline for prompt v1 only, never run again. Set 3 = the only clean final test: build it, do not run it, until Task 7.
- Prompt v2 and v2_1 guidance was written after seeing set 2 failures, so set 2 cannot validate them.
- Every reported result states: model, quantisation, prompt version, set, gate, temperature, repeats, date.

## WORKING RULES
1. Plain English. No em dashes. No buzzwords. Say only what we measured.
2. Small changes. New code goes in new files. Do not rewrite working files. Never delete anything. Do not overwrite files in results/ except results/RESULTS_SUMMARY.md and files inside a new run folder.
3. Files in llm/prompts/ are frozen once created. Never edit v1.py, v2.py or v2_1.py. If a prompt scores badly, report it. Never change a prompt, the gate or test data to improve a score.
4. One model process at a time. Before any model run: check no other run_experiment.py is running and run "ollama ps". If a run crashes or stalls, do not start another on top. Add INVALID_PARTIAL.txt to that folder and ask me.
5. Do not install anything without asking. Allowed: standard library, PyYAML, pySigma, pysigma-backend-sqlite.
6. Commands are for Windows PowerShell and Python 3.13. Do not push to git. No destructive commands.
7. After every task: run the tests, print a self-check table (EXPECTED, ACTUAL, PASS or WARN), and update PROGRESS.md. A WARN does not stop the task, but never hide it.
8. A metric counts only if a test drives the same code path that produces the reported numbers. For every gate, a copy-the-line rule must come out TOO_NARROW in the pipeline's own run summary.

## STOP RULES (ask me in chat and wait)
- A model is missing in "ollama list".
- A test fails and the only fix would touch a prompt, the gate or test data.
- A step would run set 2 or set 3 outside Task 7.
- Anything conflicts with this file.

