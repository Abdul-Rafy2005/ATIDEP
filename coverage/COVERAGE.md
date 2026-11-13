# ATIDEP ATT&CK Coverage Summary

## Coverage Definition
A technique is defined as **covered** when at least one configuration achieves a strict pass in all of its repeats (3 of 3 for 3-repeat runs, or 1 of 1 for the single-repeat set 2 baseline).

Covered means at least one of the tested configurations passed every repeat. Up to 10 configurations were tried per technique on set 1 and 6 on set 3, so this number is optimistic. The next section shows the frozen configurations alone.

## Frozen configurations only

Techniques with a strict pass in all 3 repeats under the frozen configurations:

- **qwen2.5-coder:14b with prompt v3b:**
  - Set 3 (clean final test): 19 of 20 (95.0%)
  - Set 1 (practice set used for tuning): 7 of 12 (58.3%)
- **qwen2.5-coder:7b with prompt v3a:**
  - Set 3 (clean final test): 18 of 20 (90.0%)
  - Set 1 (practice set used for tuning): 5 of 12 (41.7%)

| Model | Prompt | Set | Set Description | Strict Pass in All 3 Repeats | Total Techniques | Pass Percentage |
|---|---|---|---|---|---|---|
| qwen2.5-coder:14b | v3b | Set 3 | clean final test | 19 of 20 | 20 | 95.0% |
| qwen2.5-coder:14b | v3b | Set 1 | practice set used for tuning | 7 of 12 | 12 | 58.3% |
| qwen2.5-coder:7b | v3a | Set 3 | clean final test | 18 of 20 | 20 | 90.0% |
| qwen2.5-coder:7b | v3a | Set 1 | practice set used for tuning | 5 of 12 | 12 | 41.7% |

## Headline Metrics
- Total techniques in catalog: 44 (Set 1: 12, Set 2: 12, Set 3: 20)
- Techniques evaluated: 44 of 44 (100%)
- Techniques covered: 29 of 44 (65.9%)
- Development and final test sets (Sets 1 and 3): 27 of 32 (84.4%)

## Coverage Breakdown by Set
- **Set 1 (Development Set, 12 techniques):** 8 of 12 covered (66.7%)
- **Set 2 (Baseline Validation Set, 12 techniques):** 2 of 12 covered (16.7%)
- **Set 3 (Final Clean Test Set, 20 techniques):** 19 of 20 covered (95.0%)

## Covered Techniques (29 of 44)

| Technique ID | Set | Tactic | Reference Rule Title |
|---|---|---|---|
| `T1218.011` | Set 1 | Defense Evasion | Suspicious Rundll32 Activity Invoking Sys File |
| `T1218.005` | Set 1 | Defense Evasion | Suspicious JavaScript Execution Via Mshta.EXE |
| `T1218.010` | Set 1 | Defense Evasion | Potentially Suspicious Regsvr32 HTTP IP Pattern |
| `T1105` | Set 1 | Defense Evasion; Command and Control | Suspicious Download Via Certutil.EXE |
| `T1053.005` | Set 1 | Privilege Escalation; Execution; Persistence | Suspicious Scheduled Task Creation Involving Temp Folder |
| `T1197` | Set 1 | Persistence; Execution; Defense Evasion; Command and Control | File With Suspicious Extension Downloaded Via Bitsadmin |
| `T1047` | Set 1 | Execution | Process Creation Attempt via Wmic.EXE |
| `T1033` | Set 1 | Privilege Escalation; Discovery | Security Privileges Enumeration Via Whoami.EXE |
| `T1546.007` | Set 2 | Privilege Escalation; Persistence | Potential Persistence Via Netsh Helper DLL |
| `T1485` | Set 2 | Impact | Deleted Data Overwritten Via Cipher.EXE |
| `T1003.002` | Set 3 | Credential Access | HackTool - Pypykatz Credentials Dumping Activity |
| `T1021.006` | Set 3 | Lateral Movement | HackTool - WinRM Access Via Evil-WinRM |
| `T1040` | Set 3 | Credential Access; Discovery | Potential Network Sniffing Activity Using Network Tools |
| `T1053.002` | Set 3 | Persistence; Execution; Privilege Escalation | Interactive AT Job |
| `T1082` | Set 3 | Discovery | Suspicious Kernel Dump Using Dtrace |
| `T1112` | Set 3 | Persistence; Defense Evasion | Suspicious VBoxDrvInst.exe Parameters |
| `T1113` | Set 3 | Collection | Screen Capture Activity Via Psr.EXE |
| `T1123` | Set 3 | Collection | Audio Capture via SoundRecorder |
| `T1176.001` | Set 3 | Persistence | Chromium Browser Instance Executed With Custom Extension |
| `T1185` | Set 3 | Credential Access; Collection | Browser Started with Remote Debugging |
| `T1202` | Set 3 | Execution; Defense Evasion | Suspicious Runscripthelper.exe |
| `T1218` | Set 3 | Defense Evasion | Potential Password Spraying Attempt Using Dsacls.EXE |
| `T1219.002` | Set 3 | Command and Control; Persistence | Potential Amazon SSM Agent Hijacking |
| `T1220` | Set 3 | Defense Evasion | Remote XSL Execution Via Msxsl.EXE |
| `T1563.002` | Set 3 | Lateral Movement | Potential MSTSC Shadowing Activity |
| `T1564.004` | Set 3 | Command and Control; Defense Evasion | PrintBrm ZIP Creation of Extraction |
| `T1572` | Set 3 | Command and Control; Lateral Movement | Port Forwarding Activity Via SSH.EXE |
| `T1574` | Set 3 | Privilege Escalation; Persistence; Execution; Defense Evasion | DLL Execution Via Register-cimprovider.exe |
| `T1615` | Set 3 | Discovery | Gpresult Display Group Policy Information |

## Never-Covered Techniques (15 of 44)

The following 15 techniques did not achieve an all-repeat strict pass under any tested configuration:

### Set 1 (4 techniques)
- `T1059.001`: Blocking values in the saved rules were -nop, -w hidden and http://, which are in the shown line but not in the variant.
- `T1547.001`: Blocking value was the exact key path HKCU\Software\Microsoft\Windows\CurrentVersion\Run. The variant uses HKLM and RunOnce.
- `T1136.001`: The variant runs net1.exe instead of net.exe (alias). Needs outside knowledge. Left out of the "out of 30" numbers.
- `T1003.001`: The variant runs procdump64.exe instead of procdump.exe (alias). Needs outside knowledge. Left out of the "out of 30" numbers.

### Set 2 (10 techniques)
Set 2 was run once, with the basic prompt (v1), and never with the final prompts. Some of its variants need outside knowledge (T1489 net1.exe, T1090 which port, T1490 another bcdedit setting, T1059 -c versus /c). Do not read this list as a result about the final system.
- `T1218.001`: no cause recorded
- `T1021.002`: no cause recorded
- `T1560.001`: no cause recorded
- `T1222.001`: no cause recorded
- `T1489`: no cause recorded
- `T1482`: no cause recorded
- `T1218.008`: no cause recorded
- `T1090`: no cause recorded
- `T1490`: no cause recorded
- `T1059`: no cause recorded

### Set 3 (1 techniques)
- `T1529`: Known flaw in our test: the description says "immediate reboot" but the variant is a 30 second delay (/t 30), so rules that kept /t 0 failed.

## Configuration Strict Pass Totals

| Configuration | Label | Repeats | Strict Pass Ratio | Percentage | Source Folder |
|---|---|---|---|---|---|
| `mistral-rules|v1|2` | mistral-rules (prompt v1, set 2) | 1 | 0/12 | 0.0% | `results\archive\prompt_v1\model_outputs\mistral-rules` |
| `qwen2.5-coder:14b|v1|1` | qwen2.5-coder:14b (prompt v1, set 1) | 3 | 3/36 | 8.3% | `20261021_1528_set1_v1` |
| `qwen2.5-coder:14b|v1|2` | qwen2.5-coder:14b (prompt v1, set 2) | 1 | 2/12 | 16.7% | `results\archive\prompt_v1\model_outputs\qwen2.5-coder_14b` |
| `qwen2.5-coder:14b|v1|3` | qwen2.5-coder:14b (prompt v1, set 3) | 3 | 47/60 | 78.3% | `20261111_1449_set3_v1` |
| `qwen2.5-coder:14b|v2_1|1` | qwen2.5-coder:14b (prompt v2_1, set 1) | 3 | 8/36 | 22.2% | `20261106_1344_set1_v2_1` |
| `qwen2.5-coder:14b|v2|1` | qwen2.5-coder:14b (prompt v2, set 1) | 3 | 8/36 | 22.2% | `20261106_1338_set1_v2` |
| `qwen2.5-coder:14b|v3a|1` | qwen2.5-coder:14b (prompt v3a, set 1) | 3 | 19/36 | 52.8% | `20261111_1403_set1_v3a` |
| `qwen2.5-coder:14b|v3a|3` | qwen2.5-coder:14b (prompt v3a, set 3) | 3 | 55/60 | 91.7% | `20261111_1512_set3_v3a` |
| `qwen2.5-coder:14b|v3b|1` | qwen2.5-coder:14b (prompt v3b, set 1) | 3 | 21/36 | 58.3% | `20261111_1413_set1_v3b` |
| `qwen2.5-coder:14b|v3b|3` | qwen2.5-coder:14b (prompt v3b, set 3) | 3 | 57/60 | 95.0% | `20261111_1500_set3_v3b` |
| `qwen2.5-coder:7b|v1|1` | qwen2.5-coder:7b (prompt v1, set 1) | 3 | 7/36 | 19.4% | `20261021_1528_set1_v1` |
| `qwen2.5-coder:7b|v1|2` | qwen2.5-coder:7b (prompt v1, set 2) | 1 | 2/12 | 16.7% | `results\archive\prompt_v1\model_outputs\qwen2.5-coder_7b` |
| `qwen2.5-coder:7b|v1|3` | qwen2.5-coder:7b (prompt v1, set 3) | 3 | 35/60 | 58.3% | `20261111_1449_set3_v1` |
| `qwen2.5-coder:7b|v2_1|1` | qwen2.5-coder:7b (prompt v2_1, set 1) | 3 | 11/36 | 30.6% | `20261106_1344_set1_v2_1` |
| `qwen2.5-coder:7b|v2|1` | qwen2.5-coder:7b (prompt v2, set 1) | 3 | 9/36 | 25.0% | `20261104_1503_set1_v2` |
| `qwen2.5-coder:7b|v3a|1` | qwen2.5-coder:7b (prompt v3a, set 1) | 3 | 16/36 | 44.4% | `20261111_1403_set1_v3a` |
| `qwen2.5-coder:7b|v3a|3` | qwen2.5-coder:7b (prompt v3a, set 3) | 3 | 58/60 | 96.7% | `20261111_1507_set3_v3a` |
| `qwen2.5-coder:7b|v3b|1` | qwen2.5-coder:7b (prompt v3b, set 1) | 3 | 15/36 | 41.7% | `20261111_1413_set1_v3b` |
| `qwen2.5-coder:7b|v3b|3` | qwen2.5-coder:7b (prompt v3b, set 3) | 3 | 54/60 | 90.0% | `20261111_1518_set3_v3b` |
