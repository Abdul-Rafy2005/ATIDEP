INSTRUCTIONS = """You write Sigma detection rules for Windows process creation logs.

Output:
- Output ONLY the Sigma rule as YAML. No explanation and no comments.
- Required keys: title, status, logsource (category: process_creation, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName.

You are given ONE example of an attack. The attacker will run the same attack again with different details, so write a rule for the behaviour, not for this one command line:
- Match the program with Image|endswith, then add the one to three parts of the command line that make it malicious.
- Do not copy the whole command line. Do not use values that can change: file names, folders, drive letters, IP addresses, host names, URLs, passwords, user names or numbers.
- Do not put a space at the start or end of a value. Use short pieces such as 'delete shadows', not ' delete shadows '.
- Windows tools accept - and / for flags. To match both, add windash to the key name and write the flag with a dash, for example CommandLine|contains|windash: '-all'. For a list of several parts, put every modifier in the key name: CommandLine|contains|windash|all: followed by a list of plain text values. windash is never a list item and never a key inside a list.
- If the same tool exists under another name (for example wscript.exe and cscript.exe), list both in Image|endswith.
- To require several parts, use CommandLine|contains|all with a list. Never write the same key twice in one block.
- The rule must catch the attack but not normal, harmless use of the same program.
"""

EXAMPLES = """
Example 1
Technique: T1016
Activity: ipconfig is used to list network settings.
Process: C:\\Windows\\System32\\ipconfig.exe
Observed command line: ipconfig.exe /all
Rule:
title: Network Settings Listed With Ipconfig
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\ipconfig.exe'
        CommandLine|contains|windash: '-all'
    condition: selection
level: low
tags:
    - attack.discovery
    - attack.t1016

Example 2
Technique: T1059.005
Activity: Windows Script Host runs a script from the Public user folder.
Process: C:\\Windows\\System32\\wscript.exe
Observed command line: wscript.exe C:\\Users\\Public\\update.vbs
Rule:
title: Script Host Runs Script From Public Folder
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection_img:
        Image|endswith:
            - '\\wscript.exe'
            - '\\cscript.exe'
    selection_cli:
        CommandLine|contains|all:
            - '\\Users\\Public\\'
            - '.vbs'
    condition: all of selection_*
level: medium
tags:
    - attack.execution
    - attack.t1059.005

Example 3
Technique: T1497.003
Activity: ping is used to wait before running the next step.
Process: C:\\Windows\\System32\\ping.exe
Observed command line: ping.exe 127.0.0.1 -n 30
Rule:
title: Ping Used As A Delay
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\ping.exe'
        CommandLine|contains|windash|all:
            - '127.0.0.1'
            - '-n'
    condition: selection
level: low
tags:
    - attack.defense-evasion
    - attack.t1497.003
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech}\nActivity: {descriptions[tech]}\n"
            f"Process: {t['image']}\nObserved command line: {t['malicious']}\nRule:\n")