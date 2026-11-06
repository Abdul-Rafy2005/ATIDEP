# Run diagnosis

## A) Syntax errors, first try

qwen2.5-coder:14b T1059.001
Error: Unsupported type: <class 'dict'>
Final fixed syntax: no
Detection block:
detection:
    selection_img:
        Image|endswith: '\powershell.exe'
    selection_cli:
        CommandLine|contains|all:
            - windash: '-nop'
            - windash: '-w hidden'
            - windash: '-c IEX'
            - 'New-Object Net.WebClient'
            - 'DownloadString'
    condition: all of selection_*

qwen2.5-coder:14b T1218.010
Error: Unsupported type: <class 'dict'>
Final fixed syntax: no
Detection block:
detection:
    selection_img:
        Image|endswith: '\regsvr32.exe'
    selection_cli:
        CommandLine|contains|all:
            - windash: '-s'
            - windash: '-u'
            - windash: '-i:http://'
    condition: all of selection_*

qwen2.5-coder:14b T1105
Error: Unsupported type: <class 'dict'>
Final fixed syntax: no
Detection block:
detection:
    selection_img:
        Image|endswith: '\certutil.exe'
    selection_cli:
        CommandLine|contains|all:
            - windash: '-urlcache'
            - windash: '-f'
            - 'http://'
    condition: all of selection_*

qwen2.5-coder:14b T1003.001
Error: Unsupported type: <class 'dict'>
Final fixed syntax: no
Detection block:
detection:
    selection_img:
        Image|endswith: '\procdump.exe'
    selection_cli:
        CommandLine|contains|all:
            - windash: '-ma'
            - 'lsass.exe'
    condition: all of selection_*

## B) Error groups

4 | Unsupported type: <class 'dict'>

## C) Modifier chains

| Chain | Rules used | Converted | Failed | Only failing |
| --- | ---: | ---: | ---: | --- |
| CommandLine|contains|all | 22 | 18 | 4 | no |
| CommandLine|contains|windash | 2 | 2 | 0 | no |
| Image|endswith | 24 | 20 | 4 | no |

## D) Example leakage


## E) Shape of the rules

| Model | Average CommandLine parts | More than 3 | Padded values | Uses windash | More than one Image |
| --- | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:14b | 1.92 | 0 | 0 | 1 | 0 |
| qwen2.5-coder:7b | 2.42 | 0 | 1 | 1 | 1 |
