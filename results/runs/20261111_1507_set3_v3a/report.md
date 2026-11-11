# Non-PASS first-try rules

qwen2.5-coder:7b T1202 repeat 1: TOO_NARROW
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

qwen2.5-coder:7b T1529 repeat 2: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: C:\Windows\System32\shutdown.exe /r /t 0
Variant: C:\Windows\System32\shutdown.exe /r /t 30
Detection:
selection:
  Image|endswith: \shutdown.exe
  CommandLine|contains|windash|all:
  - /r
  - /t: '0'
condition: selection

