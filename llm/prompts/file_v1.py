"""Prompt v1 for file creation event Sigma rules.

Frozen once created. Do not edit.
"""

INSTRUCTIONS = """You write Sigma detection rules for Windows file creation events.

Output:
- Start with two comment lines. The first starts with "# keep:" and lists the file path segments or patterns that make the file drop suspicious. The second starts with "# ignore:" and lists the parts the attacker can change. Then write the Sigma rule as YAML. Write nothing else and no explanation.
- Required keys: title, status, logsource (category: file_event, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: TargetFilename, Image.

You are given ONE example of a suspicious file being written to disk. The attacker will do the same thing again with different file names, paths, or programs. Write a rule for the behaviour, not for this one event.

TargetFilename rules:
- Match the suspicious file location or extension with TargetFilename|contains or TargetFilename|endswith. Use the path segment or extension that makes the file drop dangerous.
- Do not match the exact file name. The attacker picks the file name. Match the folder or extension pattern.
- For double extensions (invoice.pdf.vbs), match the dangerous final extension, not the decoy extension.
- For files dropped in user-writable temp folders, match the folder path, not the file name.

Image rules:
- If only certain programs dropping files in this location are suspicious, filter on Image|endswith. If any program doing it is suspicious, do not filter on Image.
- Do not match the exact file path of the creating process.

The rule must catch the attack but not normal, harmless file creation.
"""

EXAMPLES = """
Example 1
Technique: T1204.002
Activity: An email client writes an executable attachment to the user's download folder.
File event:
  TargetFilename: C:\\Users\\student\\Downloads\\invoice.exe
  Image: C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE
Rule:
# keep: .exe in Downloads folder via Office
# ignore: invoice.exe, student
title: Office Application Drops Executable File
status: test
logsource:
    category: file_event
    product: windows
detection:
    selection_ext:
        TargetFilename|endswith: '.exe'
    selection_img:
        Image|contains: '\\Office'
    condition: all of selection_*
level: high
tags:
    - attack.execution
    - attack.t1204.002

Example 2
Technique: T1055.001
Activity: A process writes a DLL into another process's directory for DLL injection.
File event:
  TargetFilename: C:\\Windows\\Temp\\inject.dll
  Image: C:\\Users\\student\\AppData\\Local\\Temp\\loader.exe
Rule:
# keep: .dll in Windows\\Temp from a Temp folder process
# ignore: inject.dll, loader.exe
title: DLL Written To Windows Temp Directory
status: test
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|contains: '\\Windows\\Temp\\'
        TargetFilename|endswith: '.dll'
    condition: selection
level: medium
tags:
    - attack.defense-evasion
    - attack.t1055.001
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    shown = t["shown"]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech.replace('-file', '')}\n"
            f"Activity: {descriptions[tech]}\n"
            f"File event:\n"
            f"  TargetFilename: {shown['TargetFilename']}\n"
            f"  Image: {shown['Image']}\n"
            f"Rule:\n")
