"""Field schemas and base events for each Sysmon log type.

process_creation (Event ID 1) is the original and default.
New log types added here: registry (Event ID 12/13), file creation
(Event ID 11), network connection (Event ID 3).

Each log type defines:
    FIELDS_*: ordered list of column names (used to build the SQLite table)
    BASE_*:   default values for a synthetic event of that type
"""

# ---- Process creation (Event ID 1) -- original, unchanged -----------------

FIELDS_PROCESS_CREATION = [
    "Image", "CommandLine", "ParentImage", "ParentCommandLine",
    "OriginalFileName", "User", "IntegrityLevel", "Description",
    "Product", "Company",
]

BASE_PROCESS_CREATION = {
    "Image": "",
    "CommandLine": "",
    "OriginalFileName": "",
    "ParentImage": r"C:\Windows\System32\cmd.exe",
    "ParentCommandLine": r"C:\Windows\system32\cmd.exe",
    "User": r"LABPC\student",
    "IntegrityLevel": "Medium",
    "Description": "",
    "Product": "",
    "Company": "",
}

# ---- Registry (Event ID 12/13) -------------------------------------------

FIELDS_REGISTRY = [
    "EventType",
    "TargetObject",
    "Details",
    "Image",
    "User",
]

BASE_REGISTRY = {
    "EventType": "SetValue",
    "TargetObject": "",
    "Details": "",
    "Image": r"C:\Windows\System32\reg.exe",
    "User": r"LABPC\student",
}

# ---- File creation (Event ID 11) -----------------------------------------

FIELDS_FILE_CREATE = [
    "TargetFilename",
    "Image",
    "User",
]

BASE_FILE_CREATE = {
    "TargetFilename": "",
    "Image": "",
    "User": r"LABPC\student",
}

# ---- Network connection (Event ID 3) -------------------------------------

FIELDS_NETWORK = [
    "Image",
    "DestinationIp",
    "DestinationPort",
    "DestinationHostname",
    "Initiated",
    "Protocol",
    "User",
]

BASE_NETWORK = {
    "Image": "",
    "DestinationIp": "",
    "DestinationPort": "",
    "DestinationHostname": "",
    "Initiated": "true",
    "Protocol": "tcp",
    "User": r"LABPC\student",
}

# ---- Lookup by Sigma logsource category -----------------------------------

CATEGORY_FIELDS = {
    "process_creation": FIELDS_PROCESS_CREATION,
    "registry_set": FIELDS_REGISTRY,
    "registry_add": FIELDS_REGISTRY,
    "registry_event": FIELDS_REGISTRY,
    "file_event": FIELDS_FILE_CREATE,
    "network_connection": FIELDS_NETWORK,
}

CATEGORY_BASE = {
    "process_creation": BASE_PROCESS_CREATION,
    "registry_set": BASE_REGISTRY,
    "registry_add": BASE_REGISTRY,
    "registry_event": BASE_REGISTRY,
    "file_event": BASE_FILE_CREATE,
    "network_connection": BASE_NETWORK,
}
