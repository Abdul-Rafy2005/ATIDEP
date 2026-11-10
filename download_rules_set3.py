import csv
import os
import shutil
import urllib.request

BASE = "https://raw.githubusercontent.com/SigmaHQ/sigma/master"
RULE_DIR = "rules/windows/process_creation"
LOCAL_FALLBACK_DIR = r"C:\tmp\sigma_src\rules\windows\process_creation"

# technique, rule file name (without .yml), rule id, has_test_data
RULES = [
    ("T1003.002", "proc_creation_win_hktl_pypykatz", "a29808fd-ef50-49ff-9c7a-59a9b040b404", False),
    ("T1021.006", "proc_creation_win_hktl_evil_winrm", "a197e378-d31b-41c0-9635-cfdf1c1bb423", False),
    ("T1040",     "proc_creation_win_susp_network_sniffing", "ba1f7802-adc7-48b4-9ecb-81e227fddfd5", False),
    ("T1053.002", "proc_creation_win_at_interactive_execution", "60fc936d-2eb0-4543-8a13-911c750a1dfc", False),
    ("T1082",     "proc_creation_win_dtrace_kernel_dump", "7124aebe-4cd7-4ccb-8df0-6d6b93c96795", False),
    ("T1112",     "proc_creation_win_virtualbox_vboxdrvinst_execution", "b7b19cb6-9b32-4fc4-a108-73f19acfe262", False),
    ("T1113",     "proc_creation_win_psr_capture_screenshots", "2158f96f-43c2-43cb-952a-ab4580f32382", False),
    ("T1123",     "proc_creation_win_soundrecorder_audio_capture", "83865853-59aa-449e-9600-74b9d89a6d6e", False),
    ("T1176.001", "proc_creation_win_browsers_chromium_load_extension", "88d6e60c-759d-4ac1-a447-c0f1466c2d21", False),
    ("T1185",     "proc_creation_win_browsers_remote_debugging", "b3d34dc5-2efd-4ae3-845f-8ec14921f449", False),
    ("T1202",     "proc_creation_win_lolbin_runscripthelper", "eca49c87-8a75-4f13-9c73-a5a29e845f03", False),
    ("T1218",     "proc_creation_win_dsacls_password_spray", "bac9fb54-2da7-44e9-988f-11e9a5edbc0c", False),
    ("T1219.002", "proc_creation_win_ssm_agent_abuse", "d20ee2f4-822c-4827-9e15-41500b1fff10", False),
    ("T1220",     "proc_creation_win_msxsl_remote_execution", "75d0a94e-6252-448d-a7be-d953dff527bb", False),
    ("T1529",     "proc_creation_win_shutdown_execution", "34ebb878-1b15-4895-b352-ca2eeb99b274", False),
    ("T1563.002", "proc_creation_win_mstsc_rdp_hijack_shadowing", "6ba5a05f-b095-4f0a-8654-b825f4f16334", False),
    ("T1564.004", "proc_creation_win_lolbin_printbrm", "cafeeba3-01da-4ab4-b6c4-a31b1d9730c7", False),
    ("T1572",     "proc_creation_win_ssh_port_forward", "327f48c1-a6db-4eb8-875a-f6981f1b0183", False),
    ("T1574",     "proc_creation_win_registry_cimprovider_dll_load", "76de9e01-11d6-444a-9aa2-cb920ef0f6cc", False),
    ("T1615",     "proc_creation_win_gpresult_execution", "e56d3073-83ff-4021-90fe-c658e0709e72", False),
]


def get(url, path, name):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception:
        fallback = os.path.join(LOCAL_FALLBACK_DIR, f"{name}.yml")
        if os.path.exists(fallback):
            shutil.copyfile(fallback, path)
        else:
            raise


os.makedirs("results", exist_ok=True)
with open("results/techniques_set3.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["technique", "rule_file", "rule_id", "has_test_data"])
    for tech, name, rid, has_data in RULES:
        get(f"{BASE}/{RULE_DIR}/{name}.yml", f"data/sigmahq_rules_set3/{name}.yml", name)
        w.writerow([tech, name + ".yml", rid, has_data])
        print("ok", tech, name)
print("done")
