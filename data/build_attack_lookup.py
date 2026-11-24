"""Parse the MITRE ATT&CK STIX 2.1 bundle into a small lookup JSON.

Reads:  data/enterprise-attack.json  (55 MB, downloaded once from GitHub)
Writes: data/attack_lookup.json      (small, checked into the repo)

The lookup maps technique IDs (like T1547.001) to their official name and
tactic list. Only active (not revoked, not deprecated) techniques are kept.

Usage:
    python data/build_attack_lookup.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STIX_PATH = os.path.join(HERE, "enterprise-attack.json")
LOOKUP_PATH = os.path.join(HERE, "attack_lookup.json")

TACTIC_DISPLAY = {
    "reconnaissance": "Reconnaissance",
    "resource-development": "Resource Development",
    "initial-access": "Initial Access",
    "execution": "Execution",
    "persistence": "Persistence",
    "privilege-escalation": "Privilege Escalation",
    "defense-evasion": "Defense Evasion",
    "stealth": "Defense Evasion",
    "defense-impairment": "Defense Evasion",
    "credential-access": "Credential Access",
    "discovery": "Discovery",
    "lateral-movement": "Lateral Movement",
    "collection": "Collection",
    "command-and-control": "Command and Control",
    "exfiltration": "Exfiltration",
    "impact": "Impact",
}


def build_lookup(stix_path=STIX_PATH):
    with open(stix_path, encoding="utf-8") as f:
        bundle = json.load(f)

    lookup = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked"):
            continue
        if obj.get("x_mitre_deprecated"):
            continue

        refs = obj.get("external_references", [])
        mitre_ref = None
        for r in refs:
            if r.get("source_name") == "mitre-attack":
                mitre_ref = r
                break
        if not mitre_ref:
            continue

        tech_id = mitre_ref.get("external_id", "")
        if not tech_id.startswith("T"):
            continue

        name = obj.get("name", "")
        url = mitre_ref.get("url", "")

        tactics = []
        for phase in obj.get("kill_chain_phases", []):
            if phase.get("kill_chain_name") == "mitre-attack":
                slug = phase.get("phase_name", "")
                display = TACTIC_DISPLAY.get(slug, slug)
                if display not in tactics:
                    tactics.append(display)

        lookup[tech_id] = {
            "name": name,
            "tactics": tactics,
            "url": url,
        }

    return lookup


def main():
    if not os.path.exists(STIX_PATH):
        print(f"STIX bundle not found at {STIX_PATH}")
        print("Download it first:")
        print("  curl -sL -o data/enterprise-attack.json \\")
        print("    https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json")
        return

    lookup = build_lookup()
    with open(LOOKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(lookup)} techniques to {LOOKUP_PATH}")

    our_ids = [
        "T1547.001", "T1059.001", "T1003.001", "T1016", "T1082",
        "T1615", "T1529", "T1564.004", "T1218", "T1490",
    ]
    print("\nSample entries for our techniques:")
    for tid in our_ids:
        entry = lookup.get(tid)
        if entry:
            print(f"  {tid}: {entry['name']} [{', '.join(entry['tactics'])}]")
        else:
            print(f"  {tid}: NOT FOUND")


if __name__ == "__main__":
    main()
