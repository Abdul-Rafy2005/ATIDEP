"""Network connection event techniques for multi-logsource support.

Each technique has shown, variant, and benign events as network
connections (Sysmon Event ID 3). The logsource category is network_connection.

These techniques test whether the LLM can write Sigma rules for
suspicious outbound connections.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from logsources import BASE_NETWORK

LOGSOURCE_CATEGORY = "network_connection"

DESCRIPTIONS_NETWORK = {
    "T1071.001-net": "A non-browser process makes an outbound HTTP connection to a remote server.",
    "T1571-net": "A process connects to an external host on a non-standard port commonly used by attackers.",
    "T1572-net": "A process tunnels traffic through a local SSH port forward.",
    "T1021.002-net": "A process connects to a remote host over SMB for lateral movement.",
    "T1090.001-net": "A process connects to a known proxy port on an internal host to relay traffic.",
    "T1048.003-net": "A process exfiltrates data by connecting to an external host on a DNS port.",
    "T1095-net": "A non-standard process communicates over raw TCP to a remote command and control server.",
    "T1219-net": "A remote access tool connects outbound to its relay server for remote control.",
}

TECHNIQUES_NETWORK = {
    "T1071.001-net": {
        "shown": {
            "Image": r"C:\Windows\System32\rundll32.exe",
            "DestinationIp": "185.141.27.100",
            "DestinationPort": "443",
            "DestinationHostname": "cdn-update.example.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Windows\System32\regsvr32.exe",
            "DestinationIp": "91.234.56.78",
            "DestinationPort": "80",
            "DestinationHostname": "api.example.org",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "DestinationIp": "142.250.80.46",
            "DestinationPort": "443",
            "DestinationHostname": "www.google.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1571-net": {
        "shown": {
            "Image": r"C:\Users\student\AppData\Local\Temp\beacon.exe",
            "DestinationIp": "45.33.32.100",
            "DestinationPort": "8443",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Users\Public\agent.exe",
            "DestinationIp": "198.51.100.42",
            "DestinationPort": "4444",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\PuTTY\putty.exe",
            "DestinationIp": "10.0.0.5",
            "DestinationPort": "22",
            "DestinationHostname": "devserver.local",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1572-net": {
        "shown": {
            "Image": r"C:\Windows\System32\OpenSSH\ssh.exe",
            "DestinationIp": "203.0.113.50",
            "DestinationPort": "22",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Program Files\Git\usr\bin\ssh.exe",
            "DestinationIp": "198.51.100.10",
            "DestinationPort": "22",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\PuTTY\putty.exe",
            "DestinationIp": "10.0.0.5",
            "DestinationPort": "22",
            "DestinationHostname": "devserver.local",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1021.002-net": {
        "shown": {
            "Image": r"C:\Windows\System32\net.exe",
            "DestinationIp": "10.0.0.8",
            "DestinationPort": "445",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Windows\System32\cmd.exe",
            "DestinationIp": "192.168.1.50",
            "DestinationPort": "445",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Windows\explorer.exe",
            "DestinationIp": "10.0.0.2",
            "DestinationPort": "445",
            "DestinationHostname": "fileserver.local",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1090.001-net": {
        "shown": {
            "Image": r"C:\Users\student\AppData\Local\Temp\proxy.exe",
            "DestinationIp": "10.0.0.100",
            "DestinationPort": "8080",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Users\Public\relay.exe",
            "DestinationIp": "10.0.0.200",
            "DestinationPort": "3128",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "DestinationIp": "10.0.0.100",
            "DestinationPort": "8080",
            "DestinationHostname": "proxy.corp.local",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1048.003-net": {
        "shown": {
            "Image": r"C:\Users\student\AppData\Local\Temp\exfil.exe",
            "DestinationIp": "185.141.27.100",
            "DestinationPort": "53",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "udp",
        },
        "variant": {
            "Image": r"C:\Users\Public\sender.exe",
            "DestinationIp": "91.234.56.78",
            "DestinationPort": "53",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "udp",
        },
        "benign": {
            "Image": r"C:\Windows\System32\svchost.exe",
            "DestinationIp": "10.0.0.1",
            "DestinationPort": "53",
            "DestinationHostname": "dns.corp.local",
            "Initiated": "true",
            "Protocol": "udp",
        },
    },
    "T1095-net": {
        "shown": {
            "Image": r"C:\Users\student\AppData\Local\Temp\implant.exe",
            "DestinationIp": "45.33.32.100",
            "DestinationPort": "443",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Users\Public\c2agent.exe",
            "DestinationIp": "198.51.100.42",
            "DestinationPort": "8443",
            "DestinationHostname": "",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\Slack\slack.exe",
            "DestinationIp": "54.230.100.50",
            "DestinationPort": "443",
            "DestinationHostname": "slack.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
    "T1219-net": {
        "shown": {
            "Image": r"C:\Users\student\AppData\Local\Temp\anydesk.exe",
            "DestinationIp": "80.209.241.3",
            "DestinationPort": "7070",
            "DestinationHostname": "relay.anydesk.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "variant": {
            "Image": r"C:\Users\Public\teamviewer.exe",
            "DestinationIp": "185.188.32.1",
            "DestinationPort": "5938",
            "DestinationHostname": "router.teamviewer.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
        "benign": {
            "Image": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
            "DestinationIp": "52.96.100.50",
            "DestinationPort": "443",
            "DestinationHostname": "outlook.office365.com",
            "Initiated": "true",
            "Protocol": "tcp",
        },
    },
}


def build_network_event(overrides):
    """Build a network connection event dict from a base template plus overrides."""
    ev = dict(BASE_NETWORK)
    ev.update(overrides)
    return ev


def make_triple_network(technique):
    """Return (shown, variant, benign) network connection events for a technique."""
    t = TECHNIQUES_NETWORK[technique]
    return (
        build_network_event(t["shown"]),
        build_network_event(t["variant"]),
        build_network_event(t["benign"]),
    )
