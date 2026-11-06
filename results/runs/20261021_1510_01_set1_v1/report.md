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

qwen2.5-coder:7b T1136.001 repeat 1: SYNTAX_ERROR
Error: while parsing a block mapping
  in "<unicode string>", line 8, column 9:
            Image|endswith: '\net.exe'
            ^
expected <block end>, bu
Shown line: net.exe user hacker P@ssw0rd123 /add
Variant: 
Detection:
{}

