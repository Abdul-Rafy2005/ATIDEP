# ATIDEP 5-Minute Live Demonstration Script

Project: Automated Threat-Informed Detection Engineering Platform (FYP-1)
Target Audience: Evaluation Committee and Academic Supervisors

---

## What to Say (3 Key Statements)

1. "ATIDEP takes a plain text threat report, identifies the attacker technique using a local LLM, and drafts a Sigma detection rule in seconds."
2. "Every generated rule must pass an automated validation gate on synthetic logs that checks pySigma SQL syntax, catches hidden attack variants, and stays quiet on harmless commands."
3. "If an attack is unsupported or overly narrow, our platform stops the rule from entering the repository, preventing false alarms and broken detections."

---

## 5-Minute Demonstration Plan

### Minute 1: Platform Overview and Preflight Verification
Show the evaluation environment running locally without external cloud dependencies.

**Command**:
```powershell
ollama ps
python tools/check_frozen.py
```
**Presenter note**: State that models run entirely offline on an RTX 4000 GPU, and all frozen hashes are verified before demonstration.

---

### Minute 2: End-to-End Rule Generation and Strict Gate Pass
Demonstrate the complete slice from unstructured report text to a validated detection rule using `demo/samples/sample1.txt` (T1033 privilege discovery: `whoami.exe /priv`).

**Command**:
```powershell
python demo/demo.py --file demo/samples/sample1.txt
```

**Expected output highlights**:
- STEP 1 (TECHNIQUE): Identifies technique `T1033` and extracts `whoami.exe /priv`.
- STEP 2 (RULE): Builds prompt using frozen prompt v3b and calls Ollama. Generates valid Sigma YAML.
- STEP 3 (GATE): Runs SQLite gate. Result: `PASS` (caught extracted attack line and hidden variant `whoami /all`, quiet on benign `whoami`).
- STEP 4 (SAVE): Writes JSON metadata and YAML rule to `demo/output/`.

---

### Minute 3: Clean Refusal on Unsupported Technique
Demonstrate robust guardrails when presented with an out-of-scope report (`demo/samples/sample4.txt` describing network port scanning via `nmap`).

**Command**:
```powershell
python demo/demo.py --file demo/samples/sample4.txt
```

**Expected output**:
- Prints `Result: no supported technique found` and exits cleanly with exit code 2.
- No invalid or hallucinated rule is produced.

---

### Minute 4: ATT&CK Coverage Template
Show the generated MITRE ATT&CK coverage matrix linking techniques, SigmaHQ references, and test outcomes across all 44 evaluated techniques.

**Command**:
```powershell
python coverage/build_coverage.py
Start-Process coverage\coverage.html
```

**Presenter note**: Show the generated HTML report displaying the 44 techniques across Tactics, reference validation statuses, and LLM pass rates.

---

### Minute 5: Fast Unit Test Suite Verification
Demonstrate that the full automated regression test suite passes in under 3 seconds.

**Command**:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

**Expected output**:
- Ran 36 tests: `OK`.

