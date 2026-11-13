# ATT&CK Coverage Template

## What this template is
This template tracks which MITRE ATT&CK techniques have passing Sigma detection rules in ATIDEP. It displays the reference SigmaHQ rules, their validation status against our synthetic logs, and the performance of each LLM configuration.

## Coverage definition
A technique is defined as **covered** when at least one configuration has a strict pass in all of its repeats (3 of 3 for 3-repeat runs, or 1 of 1 for the set 2 baseline).

Covered means at least one of the tested configurations passed every repeat. Up to 10 configurations were tried per technique on set 1 and 6 on set 3, so this number is optimistic. The next section shows the frozen configurations alone.

Across all 44 evaluated techniques:
- **29 of 44 techniques are covered** across all sets (65.9%).
- **27 of 32 techniques are covered** across Sets 1 and 3 (84.4%).

## Frozen configurations only

Techniques with a strict pass in all 3 repeats under the frozen configurations:

- **qwen2.5-coder:14b with prompt v3b:**
  - Set 3 (clean final test): 19 of 20 (95.0%)
  - Set 1 (practice set used for tuning): 7 of 12 (58.3%)
- **qwen2.5-coder:7b with prompt v3a:**
  - Set 3 (clean final test): 18 of 20 (90.0%)
  - Set 1 (practice set used for tuning): 5 of 12 (41.7%)

Never-covered techniques:
- **Set 1 (4 techniques):** T1059.001, T1547.001, T1136.001, T1003.001
- **Set 2 (10 techniques):** T1218.001, T1021.002, T1560.001, T1222.001, T1489, T1482, T1218.008, T1090, T1490, T1059
- **Set 3 (1 technique):** T1529

Full details, reasons, and technique breakdown are recorded in [COVERAGE.md](COVERAGE.md).

## What the columns mean

| Column | Meaning |
|---|---|
| technique_id | The MITRE ATT&CK technique or sub-technique ID (for example T1059.001). |
| tactic | The ATT&CK tactics from the reference SigmaHQ rule's tags, separated by semicolons (for example Privilege Escalation; Discovery). |
| reference_rule_title | Title of the real SigmaHQ rule used as the ground-truth reference. |
| reference_rule_file | File name of the reference rule in data/sigmahq_rules*/. |
| reference_rule_status | Whether the real SigmaHQ rule passes our synthetic logs (PASS or FAIL). |
| model\|prompt\|set | The strict-gate result of the first-try LLM-generated rule for that configuration. |

## Verdict values

| Verdict | Meaning |
|---|---|
| PASS | The rule has valid syntax, fires on the shown attack and hidden variant, and stays quiet on benign logs. |
| NARROW | The rule fires on the shown attack but misses the hidden variant (fires on shown example only). |
| MISSED | The rule fails to fire on the shown attack line. |
| SYNTAX | The rule contains a YAML or pySigma syntax error that cannot convert to SQL. |
| NOISY | The rule fires on harmless benign logs (false positive). |
| NOT_TESTED | No run has evaluated this technique under this configuration. |
| N/M | For runs with repeats: N passes out of M repeats (for example 2/3). |

## How to add a new technique

1. Pick a technique: Select an ATT&CK technique and find a suitable SigmaHQ process creation rule from rules/windows/process_creation.
2. Add to generator: In generator/techniques_set3.py (or the current set file), add the technique entry with:
   - image: full path to the executable
   - malicious: the command line shown to the model
   - variant: the hidden attack variant (different flag, path, or syntax)
   - benign: a harmless command line using the same program
   - variant_type, rule_file, rule_id
   - Add a plain-English description to DESCRIPTIONS3.
3. Download the reference rule: Place the SigmaHQ rule YAML file into data/sigmahq_rules_set3/ and add a row to results/techniques_set3.csv.
4. Verify the reference rule: Run python validator/test_set3_real_rules.py to confirm the reference rule passes your synthetic logs.
5. Rebuild coverage: Run python coverage/build_coverage.py to update coverage.csv, coverage.html, and COVERAGE.md.
