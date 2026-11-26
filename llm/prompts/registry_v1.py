"""Prompt v1 for registry event Sigma rules.

Frozen once created. Do not edit.
"""

INSTRUCTIONS = """You write Sigma detection rules for Windows registry events.

Output:
- Start with two comment lines. The first starts with "# keep:" and lists the registry path segments or values that make the behaviour dangerous. The second starts with "# ignore:" and lists the parts the attacker can change. Then write the Sigma rule as YAML. Write nothing else and no explanation.
- Required keys: title, status, logsource (category: registry_set, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: EventType, TargetObject, Details, Image.

You are given ONE example of a registry write made by an attacker. The attacker will do the same thing again with different registry key names, values, or programs. Write a rule for the behaviour, not for this one event.
- Match the dangerous registry path with TargetObject|contains. Use the path segment that identifies the attack, not the full path and not the final key name (the attacker picks the key name).
- If the attack writes a specific value like a DWORD, match it with Details.
- If the attack can be done by any program, do not filter on Image. If only certain programs are suspicious, use Image|endswith.
- Do not copy the full TargetObject path. Use the shortest substring that identifies the dangerous location.
- The rule must catch the attack but not normal, harmless registry writes.
"""

EXAMPLES = """
Example 1
Technique: T1547.009
Activity: A program adds a shortcut to the Windows Startup folder via registry.
Registry event:
  EventType: SetValue
  TargetObject: HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders\\Startup
  Details: C:\\Users\\Public\\evil_startup
  Image: C:\\Windows\\System32\\reg.exe
Rule:
# keep: User Shell Folders\\Startup
# ignore: C:\\Users\\Public\\evil_startup, reg.exe
title: Startup Folder Path Modified Via Registry
status: test
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|contains: 'User Shell Folders\\Startup'
    condition: selection
level: medium
tags:
    - attack.persistence
    - attack.t1547.009

Example 2
Technique: T1562.002
Activity: A program disables Windows event logging by setting a registry value.
Registry event:
  EventType: SetValue
  TargetObject: HKLM\\SYSTEM\\CurrentControlSet\\Services\\EventLog\\Security\\Enabled
  Details: DWORD (0x00000000)
  Image: C:\\Windows\\System32\\reg.exe
Rule:
# keep: Services\\EventLog, DWORD (0x00000000)
# ignore: Security\\Enabled, reg.exe
title: Event Log Disabled Via Registry
status: test
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|contains: 'Services\\EventLog'
        Details: 'DWORD (0x00000000)'
    condition: selection
level: high
tags:
    - attack.defense-evasion
    - attack.t1562.002
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    shown = t["shown"]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech.replace('-reg', '')}\n"
            f"Activity: {descriptions[tech]}\n"
            f"Registry event:\n"
            f"  EventType: {shown['EventType']}\n"
            f"  TargetObject: {shown['TargetObject']}\n"
            f"  Details: {shown['Details']}\n"
            f"  Image: {shown['Image']}\n"
            f"Rule:\n")
