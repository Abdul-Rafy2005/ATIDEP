"""Registry event techniques for multi-logsource support.

Each technique has shown, variant, and benign events as registry writes
(Sysmon Event ID 12/13). The logsource category is registry_set.

These techniques test whether the LLM can write Sigma rules for a log
type other than process_creation.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from logsources import BASE_REGISTRY

LOGSOURCE_CATEGORY = "registry_set"

DESCRIPTIONS_REGISTRY = {
    "T1547.001-reg": "A program adds an executable to the Windows Run key so it starts on every logon.",
    "T1562.001-reg": "A program disables Windows Defender real-time protection via registry.",
    "T1112-reg": "A program hides a file extension by changing registry settings.",
    "T1546.001-reg": "A program changes the default handler for .txt files to run a script.",
    "T1574.011-reg": "A program registers a malicious DLL as a known DLL in the registry.",
    "T1037.001-reg": "A program sets a logon script via the UserInitMprLogonScript registry value.",
    "T1546.015-reg": "A program registers a COM object to hijack execution when a legitimate app starts.",
    "T1562.004-reg": "A program disables the Windows Firewall via registry.",
}

TECHNIQUES_REGISTRY = {
    "T1547.001-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\Updater",
            "Details": r"C:\Users\Public\malware.exe",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\SyncTask",
            "Details": r"C:\ProgramData\beacon.exe",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\SecurityHealth",
            "Details": r"C:\Program Files\Windows Defender\MSASCuiL.exe",
            "Image": r"C:\Windows\System32\msiexec.exe",
        },
    },
    "T1562.001-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection\DisableRealtimeMonitoring",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection\DisableBehaviorMonitoring",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\powershell.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Reporting\DisableGenericRePorts",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\reg.exe",
        },
    },
    "T1112-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\HideFileExt",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Hidden",
            "Details": "DWORD (0x00000002)",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\ShowSuperHidden",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\explorer.exe",
        },
    },
    "T1546.001-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\txtfile\shell\open\command\(Default)",
            "Details": r"C:\Users\Public\backdoor.exe %1",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\htmlfile\shell\open\command\(Default)",
            "Details": r"C:\ProgramData\loader.exe %1",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\txtfile\shell\open\command\(Default)",
            "Details": r"C:\Program Files\Notepad++\notepad++.exe %1",
            "Image": r"C:\Program Files\Notepad++\notepad++.exe",
        },
    },
    "T1574.011-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs\payload",
            "Details": r"payload.dll",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs\helper",
            "Details": r"helper.dll",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\TEMP",
            "Details": r"C:\Windows\Temp",
            "Image": r"C:\Windows\System32\SystemPropertiesAdvanced.exe",
        },
    },
    "T1037.001-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\Environment\UserInitMprLogonScript",
            "Details": r"C:\Users\Public\logon.bat",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\Environment\UserInitMprLogonScript",
            "Details": r"C:\ProgramData\startup.cmd",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\Environment\TEMP",
            "Details": r"C:\Users\student\AppData\Local\Temp",
            "Image": r"C:\Windows\System32\SystemPropertiesAdvanced.exe",
        },
    },
    "T1546.015-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\CLSID\{b5f8350b-0548-48b1-a6ee-88bd00b4a5e7}\InprocServer32\(Default)",
            "Details": r"C:\Users\Public\evil.dll",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\CLSID\{42aedc87-2188-41fd-b9a3-0c966feabec1}\InprocServer32\(Default)",
            "Details": r"C:\ProgramData\hijack.dll",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKCU\SOFTWARE\Classes\CLSID\{b5f8350b-0548-48b1-a6ee-88bd00b4a5e7}\InprocServer32\ThreadingModel",
            "Details": "Apartment",
            "Image": r"C:\Windows\System32\explorer.exe",
        },
    },
    "T1562.004-reg": {
        "shown": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\EnableFirewall",
            "Details": "DWORD (0x00000000)",
            "Image": r"C:\Windows\System32\reg.exe",
        },
        "variant": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile\EnableFirewall",
            "Details": "DWORD (0x00000000)",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "benign": {
            "EventType": "SetValue",
            "TargetObject": r"HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\DoNotAllowExceptions",
            "Details": "DWORD (0x00000001)",
            "Image": r"C:\Windows\System32\netsh.exe",
        },
    },
}


def build_registry_event(overrides):
    """Build a registry event dict from a base template plus overrides."""
    ev = dict(BASE_REGISTRY)
    ev.update(overrides)
    return ev


def make_triple_registry(technique):
    """Return (shown, variant, benign) registry events for a technique."""
    t = TECHNIQUES_REGISTRY[technique]
    return (
        build_registry_event(t["shown"]),
        build_registry_event(t["variant"]),
        build_registry_event(t["benign"]),
    )
