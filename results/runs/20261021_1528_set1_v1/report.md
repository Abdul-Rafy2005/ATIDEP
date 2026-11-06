# Non-PASS first-try rules

qwen2.5-coder:7b T1218.011 repeat 1: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\rundll32.exe'
            ^
expected <block end
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: 
Detection:
{}

qwen2.5-coder:7b T1218.011 repeat 2: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\rundll32.exe'
            ^
expected <block end
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: 
Detection:
{}

qwen2.5-coder:7b T1218.011 repeat 3: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\rundll32.exe'
            ^
expected <block end
Shown line: rundll32.exe C:\Windows\Temp\driver.sys,Run
Variant: 
Detection:
{}

qwen2.5-coder:7b T1053.005 repeat 1: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\schtasks.exe'
            ^
expected <block end
Shown line: schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00
Variant: 
Detection:
{}

qwen2.5-coder:7b T1547.001 repeat 1: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\reg.exe'
            ^
expected <block end>, bu
Shown line: reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe
Variant: 
Detection:
{}

qwen2.5-coder:7b T1136.001 repeat 1: SYNTAX_ERROR
Error: while scanning a block scalar
  in "<unicode string>", line 9, column 40:
     ...  CommandLine|contains: ' user ' |contains: ' /add '
               
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: 
Detection:
{}

qwen2.5-coder:7b T1136.001 repeat 2: SYNTAX_ERROR
Error: while scanning a block scalar
  in "<unicode string>", line 9, column 40:
     ...  CommandLine|contains: ' user ' |contains: ' /add '
               
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: 
Detection:
{}

qwen2.5-coder:7b T1136.001 repeat 3: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\net.exe'
            ^
expected <block end>, bu
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: 
Detection:
{}

qwen2.5-coder:14b T1136.001 repeat 1: MISSED_SHOWN
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: 
Detection:
selection:
  Image|endswith: \net.exe
  CommandLine|contains|all:
  - ' user '
  - ' /add '
condition: selection

