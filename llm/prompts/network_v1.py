"""Prompt v1 for network connection event Sigma rules.

Frozen once created. Do not edit.
"""

INSTRUCTIONS = """You write Sigma detection rules for Windows network connection events.

Output:
- Start with two comment lines. The first starts with "# keep:" and lists the network attributes that make the connection suspicious. The second starts with "# ignore:" and lists the parts the attacker can change. Then write the Sigma rule as YAML. Write nothing else and no explanation.
- Required keys: title, status, logsource (category: network_connection, product: windows), detection (with condition), level, tags.
- Do not add id, author, date, modified, references, related, description or falsepositives.
- Use only these fields: Image, DestinationPort, Initiated, Protocol.

You are given ONE example of a suspicious network connection. The attacker will make similar connections from different programs or to different addresses. Write a rule for the behaviour, not for this one connection.

Important rules:
- NEVER match on DestinationIp or DestinationHostname. IP addresses and hostnames change between attacks. Use Image, DestinationPort, and Protocol instead.
- Match the suspicious program with Image|endswith. If the suspicious part is the folder (like a file running from Temp), use Image|contains.
- Match suspicious ports with DestinationPort when the port is what makes the connection unusual.
- Use Initiated: 'true' to match only outbound connections when that matters.
- If a legitimate program makes the same kind of connection, add a filter to exclude it.

The rule must catch the attack but not normal, harmless network activity from the same program or port.
"""

EXAMPLES = """
Example 1
Technique: T1059.001
Activity: PowerShell makes an outbound HTTP connection to download a payload.
Network event:
  Image: C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe
  DestinationIp: 185.141.27.100
  DestinationPort: 443
  DestinationHostname: cdn-update.example.com
  Initiated: true
  Protocol: tcp
Rule:
# keep: powershell.exe making outbound connection
# ignore: 185.141.27.100, cdn-update.example.com, 443
title: PowerShell Outbound Network Connection
status: test
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        Image|endswith: '\\powershell.exe'
        Initiated: 'true'
    condition: selection
level: medium
tags:
    - attack.execution
    - attack.t1059.001

Example 2
Technique: T1048.002
Activity: A process from a temporary folder connects outbound on an unusual port.
Network event:
  Image: C:\\Users\\student\\AppData\\Local\\Temp\\exfil.exe
  DestinationIp: 91.234.56.78
  DestinationPort: 8443
  DestinationHostname:
  Initiated: true
  Protocol: tcp
Rule:
# keep: Temp folder process, outbound
# ignore: exfil.exe, 91.234.56.78, 8443
title: Process In Temp Folder Makes Outbound Connection
status: test
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        Image|contains: '\\Temp\\'
        Initiated: 'true'
    condition: selection
level: high
tags:
    - attack.exfiltration
    - attack.t1048.002
"""


def build_prompt(tech, techniques, descriptions):
    t = techniques[tech]
    shown = t["shown"]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech.replace('-net', '')}\n"
            f"Activity: {descriptions[tech]}\n"
            f"Network event:\n"
            f"  Image: {shown['Image']}\n"
            f"  DestinationIp: {shown['DestinationIp']}\n"
            f"  DestinationPort: {shown['DestinationPort']}\n"
            f"  DestinationHostname: {shown.get('DestinationHostname', '')}\n"
            f"  Initiated: {shown['Initiated']}\n"
            f"  Protocol: {shown['Protocol']}\n"
            f"Rule:\n")
