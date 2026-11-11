INSTRUCTIONS = """You write Sigma detection rules for Windows process creation logs.

Output:
- Start with two comment lines. The first starts with "# keep:" and lists the parts of the command line that make the behaviour dangerous. The second starts with "# ignore:" and lists the parts the attacker can change. Then write the Sigma rule as YAML, using only the "keep" parts. Write nothing else and no explanation.
- Required keys: title, status, logsource (category: process_creation, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName.

You are given ONE example of an attack. The attacker will run the same attack again with different details, so write a rule for the behaviour, not for this one command line.
- Match the program with Image|endswith.
- Use as few CommandLine values as possible. One is best. Use two only if one value alone would also match harmless use of the same program. Never use more than three.
- Each value is one word or one flag. A flag with its fixed name is fine, such as -type=txt. A value is never longer than two words.
- A value must be the option, sub-command or keyword that makes the behaviour dangerous. It must NOT be a file name, folder, drive letter, IP address, host name, URL, domain name, user name, password, task name, port or any number.
- Do not copy the whole command line. Do not put a space at the start or end of a value.
- Windows tools accept - and / for flags. To match both, add windash to the key name and write the flag with a dash. For a list of several values, put every modifier in the key name: CommandLine|contains|windash|all: followed by a list of plain text values. windash is never a list item and never a key inside a list.
- If the same tool exists under another name (for example wscript.exe and cscript.exe), list both in Image|endswith.
- The rule must catch the attack but not normal, harmless use of the same program.
"""

EXAMPLES = """
Example 1
Technique: T1071.004
Activity: nslookup is used to ask a DNS server for TXT records of a domain.
Process: C:\\Windows\\System32\\nslookup.exe
Observed command line: nslookup.exe -type=txt data.example.com 10.0.0.53
Rule:
# keep: -type=txt
# ignore: data.example.com, 10.0.0.53
title: Nslookup Used To Query TXT Records
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\nslookup.exe'
        CommandLine|contains|windash: '-type=txt'
    condition: selection
level: low
tags:
    - attack.command-and-control
    - attack.t1071.004

Example 2
Technique: T1059.007
Activity: Windows Script Host runs a JavaScript file in batch mode.
Process: C:\\Windows\\System32\\wscript.exe
Observed command line: wscript.exe //B //E:jscript C:\\Users\\Public\\a.js
Rule:
# keep: //B, //E:jscript
# ignore: C:\\Users\\Public\\a.js
title: Script Host Runs JavaScript In Batch Mode
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
            - '//B'
            - '//E:jscript'
    condition: all of selection_*
level: medium
tags:
    - attack.execution
    - attack.t1059.007

Example 3
Technique: T1070.004
Activity: sdelete is used to overwrite files so they cannot be recovered.
Process: C:\\Tools\\sdelete.exe
Observed command line: sdelete.exe -accepteula -p 3 C:\\Users\\student\\Documents
Rule:
# keep: -accepteula, -p
# ignore: 3, C:\\Users\\student\\Documents
title: Sdelete Used To Overwrite Files
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\sdelete.exe'
        CommandLine|contains|windash|all:
            - '-accepteula'
            - '-p'
    condition: selection
level: medium
tags:
    - attack.defense-evasion
    - attack.t1070.004
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech}\nActivity: {descriptions[tech]}\n"
            f"Process: {t['image']}\nObserved command line: {t['malicious']}\nRule:\n")

