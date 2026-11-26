"""File creation event techniques for multi-logsource support.

Each technique has shown, variant, and benign events as file creation
events (Sysmon Event ID 11). The logsource category is file_event.

These techniques test whether the LLM can write Sigma rules for
suspicious file drops and writes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from logsources import BASE_FILE_CREATE

LOGSOURCE_CATEGORY = "file_event"

DESCRIPTIONS_FILE = {
    "T1105-file": "An attacker tool drops a payload executable into a user-writable folder.",
    "T1027-file": "A process writes an obfuscated script file with a double extension to disk.",
    "T1036.005-file": "A process drops an executable that mimics a legitimate Windows binary name in a non-standard location.",
    "T1059.001-file": "PowerShell writes a script file to a temporary folder for later execution.",
    "T1053.005-file": "A process creates an XML task file in the Windows Tasks folder to set up persistence.",
    "T1547.001-file": "A process drops an executable into the user's Startup folder so it runs on logon.",
    "T1074.001-file": "A process stages collected data into a single archive file before exfiltration.",
    "T1570-file": "A process writes an executable to a remote admin share for lateral movement.",
}

TECHNIQUES_FILE = {
    "T1105-file": {
        "shown": {
            "TargetFilename": r"C:\Users\Public\payload.exe",
            "Image": r"C:\Windows\System32\certutil.exe",
        },
        "variant": {
            "TargetFilename": r"C:\Users\student\AppData\Local\Temp\dropper.exe",
            "Image": r"C:\Windows\System32\bitsadmin.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Users\student\Downloads\setup.exe",
            "Image": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        },
    },
    "T1027-file": {
        "shown": {
            "TargetFilename": r"C:\Users\student\AppData\Local\Temp\invoice.pdf.vbs",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "variant": {
            "TargetFilename": r"C:\Users\Public\report.docx.js",
            "Image": r"C:\Windows\System32\wscript.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Users\student\Documents\notes.txt",
            "Image": r"C:\Windows\System32\notepad.exe",
        },
    },
    "T1036.005-file": {
        "shown": {
            "TargetFilename": r"C:\Users\Public\svchost.exe",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "variant": {
            "TargetFilename": r"C:\ProgramData\csrss.exe",
            "Image": r"C:\Windows\System32\powershell.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Program Files\MyApp\myapp.exe",
            "Image": r"C:\Windows\System32\msiexec.exe",
        },
    },
    "T1059.001-file": {
        "shown": {
            "TargetFilename": r"C:\Users\student\AppData\Local\Temp\update.ps1",
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        },
        "variant": {
            "TargetFilename": r"C:\Windows\Temp\stage2.ps1",
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Scripts\backup.ps1",
            "Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        },
    },
    "T1053.005-file": {
        "shown": {
            "TargetFilename": r"C:\Windows\System32\Tasks\Updater",
            "Image": r"C:\Windows\System32\schtasks.exe",
        },
        "variant": {
            "TargetFilename": r"C:\Windows\System32\Tasks\SyncAgent",
            "Image": r"C:\Windows\System32\schtasks.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Windows\System32\Tasks\Microsoft\Windows\Defrag\ScheduledDefrag",
            "Image": r"C:\Windows\System32\svchost.exe",
        },
    },
    "T1547.001-file": {
        "shown": {
            "TargetFilename": r"C:\Users\student\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\updater.exe",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "variant": {
            "TargetFilename": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\helper.bat",
            "Image": r"C:\Windows\System32\powershell.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Users\student\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\desktop.ini",
            "Image": r"C:\Windows\explorer.exe",
        },
    },
    "T1074.001-file": {
        "shown": {
            "TargetFilename": r"C:\Users\student\AppData\Local\Temp\exfil.zip",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "variant": {
            "TargetFilename": r"C:\Windows\Temp\data.rar",
            "Image": r"C:\Windows\System32\powershell.exe",
        },
        "benign": {
            "TargetFilename": r"C:\Users\student\Documents\backup.zip",
            "Image": r"C:\Program Files\7-Zip\7z.exe",
        },
    },
    "T1570-file": {
        "shown": {
            "TargetFilename": r"\\10.0.0.8\C$\Windows\Temp\beacon.exe",
            "Image": r"C:\Windows\System32\cmd.exe",
        },
        "variant": {
            "TargetFilename": r"\\192.168.1.50\ADMIN$\payload.dll",
            "Image": r"C:\Windows\System32\powershell.exe",
        },
        "benign": {
            "TargetFilename": r"\\fileserver\shared\report.docx",
            "Image": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        },
    },
}


def build_file_event(overrides):
    """Build a file creation event dict from a base template plus overrides."""
    ev = dict(BASE_FILE_CREATE)
    ev.update(overrides)
    return ev


def make_triple_file(technique):
    """Return (shown, variant, benign) file creation events for a technique."""
    t = TECHNIQUES_FILE[technique]
    return (
        build_file_event(t["shown"]),
        build_file_event(t["variant"]),
        build_file_event(t["benign"]),
    )
