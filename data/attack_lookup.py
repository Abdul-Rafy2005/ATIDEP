"""Load the ATT&CK technique lookup and provide accessor functions.

The lookup file (attack_lookup.json) is built by build_attack_lookup.py from
the MITRE ATT&CK STIX 2.1 bundle. It maps technique IDs to official names,
tactics, and ATT&CK URLs.

Usage:
    from data.attack_lookup import get_technique, get_name, get_tactics

    t = get_technique("T1547.001")
    # {"name": "Registry Run Keys / Startup Folder",
    #  "tactics": ["Persistence", "Privilege Escalation"],
    #  "url": "https://attack.mitre.org/techniques/T1547/001"}

    get_name("T1547.001")   # "Registry Run Keys / Startup Folder"
    get_tactics("T1547.001") # ["Persistence", "Privilege Escalation"]
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKUP_PATH = os.path.join(HERE, "attack_lookup.json")

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    if not os.path.exists(LOOKUP_PATH):
        _cache = {}
        return _cache
    with open(LOOKUP_PATH, encoding="utf-8") as f:
        _cache = json.load(f)
    return _cache


def get_technique(tech_id):
    """Return the lookup entry for a technique ID, or None."""
    return _load().get(tech_id)


def get_name(tech_id):
    """Return the official ATT&CK name, or the tech_id itself as fallback."""
    entry = get_technique(tech_id)
    if entry:
        return entry["name"]
    return tech_id


def get_tactics(tech_id):
    """Return list of tactic display names, or empty list."""
    entry = get_technique(tech_id)
    if entry:
        return entry["tactics"]
    return []


def get_url(tech_id):
    """Return the ATT&CK URL, or empty string."""
    entry = get_technique(tech_id)
    if entry:
        return entry.get("url", "")
    return ""


def all_techniques():
    """Return the full lookup dict."""
    return _load()
