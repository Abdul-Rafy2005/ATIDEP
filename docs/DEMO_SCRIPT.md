# ATIDEP 5-Minute Live Demonstration Script

Project: Automated Threat-Informed Detection Engineering Platform (FYP-1)  
Target Audience: Evaluation Committee and Academic Supervisors  

---

## Before You Start Checklist

Complete these pre-flight checks before the presentation starts:

1. **Which PC**: Use the Dell Precision 3680 lab PC with Intel Core i7-14700, 32 GB RAM, and NVIDIA RTX 4000 Ada Generation (20 GB VRAM).
2. **Plug in power**: Ensure the workstation or laptop is plugged into mains power and not in a battery saving mode.
3. **Close other programs**: Close unnecessary browsers, IDEs, and background tasks to ensure full GPU VRAM and compute are dedicated to Ollama.
4. **Check Ollama**: In PowerShell, run `ollama ps` to ensure the local Ollama daemon is running and responsive.
5. **Pre-warm model**: Run `python demo/demo.py --file demo/samples/sample1.txt` once before the presentation so model weights are preloaded into GPU memory.

---

## 5-Minute Demonstration Plan

### 1. What the Project Is (30 seconds)
**Spoken line**:
> "ATIDEP takes plain threat descriptions, uses a local 14B LLM to draft Sigma rules, and validates every rule against synthetic logs before marking it ready."

**Three lines**:
- ATIDEP is an Automated Threat-Informed Detection Engineering Platform.
- It takes unstructured threat descriptions and produces Sigma detection rules with a local LLM.
- It tests every drafted rule on synthetic logs using an automated validation gate to reject broken or overfitted rules.

**Command**:
```powershell
python tools/check_frozen.py
```

---

### 2. End-to-End Pipeline Demo (90 seconds)
**Command**:
```powershell
python demo/demo.py --file demo/samples/sample1.txt
```

**Spoken line**:
> "A plain text report of privilege discovery goes in, our frozen 14B model drafts a Sigma rule, and the validation gate checks it against synthetic logs to award a PASS; note that the first invocation loads the model into GPU memory."

**What to point out on screen**:
- Step 1: Model extracts technique `T1033` and observed command `whoami.exe /priv`.
- Step 2: Frozen prompt v3b produces a clean Sigma YAML rule.
- Step 3: Automated validation gate checks pySigma SQLite syntax, caught status on shown line and hidden variant, and quiet status on harmless line.
- Step 4: Rule and metadata are saved to `demo/output/`.

---

### 3. Gate Demonstration: Rejecting Narrow Rules (90 seconds)
Demonstrate how the gate catches rules that copy command lines, contrasting a rejected rule with a passing rule.

**Command 1 (Rejected narrow rule)**:
```powershell
python demo/gate_demo.py --rule demo/sample_rules/rule_b_narrow_padded.yml --set 3 --technique T1564.004
```

**Spoken line**:
> "The gate rejects this rule as TOO_NARROW because it hardcoded padded flags '-b -f' and missed the hidden variant, which a single-log test would have missed."

**Command 2 (Passing generalised rule)**:
```powershell
python demo/gate_demo.py --rule demo/sample_rules/rule_a_pass.yml --set 3 --technique T1615
```

**Spoken line**:
> "In contrast, this passing rule generalises flag arguments with windash and catches both the original attack line and the hidden variant."

---

### 4. ATT&CK Coverage Template and Test Results (60 seconds)
**Command**:
```powershell
Start-Process coverage\coverage.html
```

**Spoken line**:
> "Our coverage template tracks 44 techniques across MITRE ATT&CK, where the frozen 14B model under prompt v3b achieved 19 of 20 strict passes on the clean Set 3 test set."

**What to point out on screen**:
- 29 of 44 techniques covered across all exploratory runs, and 27 of 32 on Sets 1 and 3 combined.
- Frozen configuration section: 14B v3b achieves 19 of 20 strict passes on Set 3 (clean final test) and 7 of 12 on Set 1 (practice set).
- Multi-tactic column showing standard MITRE tactic classifications.

---

### 5. Limits and Next Steps (30 seconds)
**Spoken line**:
> "Currently ATIDEP covers Windows process creation logs on 44 hand-authored templates; FYP-2 will extend coverage to registry, network, and file events with sandboxed malware execution."

**Key points**:
- Process creation (Sysmon Event 1) only in FYP-1.
- Flat synthetic logs rather than complex multi-stage event trees.
- FYP-2 will integrate malware sandboxing and multi-event log generation.

---

## If Something Fails

1. **If Ollama is slow**:
   - Explain to the evaluators: "Local quantization and GPU context initialization can take a few seconds on first execution."
2. **If a live inference stalls**:
   - Open and display the pre-generated output files in `demo/output/` (e.g., `20261111_143900.json` and `20261111_143900.yml`) to show identical pipeline results.
3. **If hardware or software environment fails**:
   - Play the backup video recording showing the entire 5-minute demonstration sequence.
