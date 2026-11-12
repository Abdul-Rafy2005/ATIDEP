# ATIDEP ATT&CK Coverage Summary

## Coverage Definition
A technique is defined as **covered** when at least one configuration achieves a strict pass in all of its repeats (3 of 3 for 3-repeat runs, or 1 of 1 for the single-repeat set 2 baseline).

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
- `T1059.001` (Command and Scripting Interpreter: PowerShell): Rules overfit to specific cmdlet flags or syntax.
- `T1547.001` (Boot or Logon Autostart Execution: Registry Run Keys): Rules overfit to specific registry value names.
- `T1136.001` (Create Account: Local Account): Rules overfit to specific net user parameters.
- `T1003.001` (OS Credential Dumping: LSASS Memory): Rules overfit to procdump flags or dump file paths.

### Set 2 (10 techniques)
Set 2 was evaluated only under prompt v1 as a single-repeat baseline (temperature 0). Ten techniques did not pass strict validation due to missing outside domain knowledge (e.g. net1.exe alias, port numbers, bcdedit tamper settings, forfiles syntax) or narrow command line matching:
- `T1218.001` (System Binary Proxy Execution: Compiled HTML File)
- `T1021.002` (Remote Services: SMB/Windows Admin Shares)
- `T1560.001` (Archive Collected Data: Archive via Utility)
- `T1222.001` (File and Directory Permissions Modification: Windows MACs)
- `T1489` (Service Stop)
- `T1482` (Domain Trust Discovery)
- `T1218.008` (System Binary Proxy Execution: Odbcconf)
- `T1090` (Proxy)
- `T1490` (Inhibit System Recovery)
- `T1059` (Command and Scripting Interpreter)

### Set 3 (1 technique)
- `T1529` (System Shutdown/Reboot): Requires generalising shutdown command arguments; models overfitted to specific timeout and comment flags.

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
