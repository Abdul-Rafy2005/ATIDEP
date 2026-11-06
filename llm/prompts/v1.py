INSTRUCTIONS = """You write Sigma detection rules for Windows process creation logs.
Rules:
- Output ONLY the Sigma rule as YAML. No explanation.
- Use only these fields: Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName.
- Use modifiers like |contains, |endswith, |contains|all.
- Required keys: title, status, logsource (category: process_creation, product: windows), detection (with condition), level, tags.
- The rule must catch the attacker activity but NOT normal harmless use of the same program.
"""

EXAMPLES = """
Example 1
Technique: T1016
Activity: ipconfig is used to list network settings.
Process: C:\\Windows\\System32\\ipconfig.exe
Observed command line: ipconfig.exe /all
Rule:
title: Network Configuration Discovery With Ipconfig
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\ipconfig.exe'
        CommandLine|contains: ' /all'
    condition: selection
level: low
tags:
    - attack.discovery
    - attack.t1016

Example 2
Technique: T1564.001
Activity: attrib is used to hide a file.
Process: C:\\Windows\\System32\\attrib.exe
Observed command line: attrib.exe +h C:\\Users\\student\\secret.exe
Rule:
title: File Hidden With Attrib
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\attrib.exe'
        CommandLine|contains: ' +h '
    condition: selection
level: medium
tags:
    - attack.defense-evasion
    - attack.t1564.001
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech}\nActivity: {descriptions[tech]}\n"
            f"Process: {t['image']}\nObserved command line: {t['malicious']}\nRule:\n")