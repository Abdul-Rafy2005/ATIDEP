"""Prompt v2 for registry event Sigma rules.

Changes from registry_v1:
- Tells the model to use at least two path segments in TargetObject matches.
- Tells the model not to match the final key name (attacker picks it).
- Notes that CLSIDs and GUIDs vary between attacks.
- Adds guidance about filtering on Image only when needed.

Frozen once created. Do not edit.
"""

INSTRUCTIONS = """You write Sigma detection rules for Windows registry events.

Output:
- Start with two comment lines. The first starts with "# keep:" and lists the registry path segments or values that make the behaviour dangerous. The second starts with "# ignore:" and lists the parts the attacker can change. Then write the Sigma rule as YAML. Write nothing else and no explanation.
- Required keys: title, status, logsource (category: registry_set, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: EventType, TargetObject, Details, Image.

You are given ONE example of a registry write made by an attacker. The attacker will do the same thing again with different registry key names, values, or programs. Write a rule for the behaviour, not for this one event.

TargetObject rules:
- Match the dangerous registry location with TargetObject|contains. Use at least two consecutive path segments to avoid matching unrelated keys. One short word like "Run" or "Shell" alone is too broad.
- Do not match the final key name in the path. The attacker picks the key name (for example "Updater", "SyncTask"). Match the parent path that makes the location dangerous.
- CLSIDs, GUIDs, and other identifiers in curly braces vary between attacks. Do not include them in your match. Match the path segments before or after the GUID.

Details rules:
- If the attack writes a specific registry value type (like DWORD 0 or 1), you can match it with Details.
- Do not match file paths, DLL names, or executable names in Details. The attacker changes those.

Image rules:
- Most registry attacks can be done by any program. Do not filter on Image unless only one specific tool can make this registry change.

The rule must catch the attack but not normal, harmless registry writes to nearby keys.
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
Activity: A program disables Windows event logging by setting a registry value to zero.
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

Example 3
Technique: T1546.012
Activity: A program registers a malicious DLL as an Image File Execution Options debugger.
Registry event:
  EventType: SetValue
  TargetObject: HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\sethc.exe\\Debugger
  Details: C:\\Windows\\Temp\\backdoor.exe
  Image: C:\\Windows\\System32\\reg.exe
Rule:
# keep: Image File Execution Options, Debugger
# ignore: sethc.exe, C:\\Windows\\Temp\\backdoor.exe, reg.exe
title: Image File Execution Options Debugger Set
status: test
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|contains|all:
            - 'Image File Execution Options'
            - 'Debugger'
    condition: selection
level: high
tags:
    - attack.persistence
    - attack.t1546.012
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
