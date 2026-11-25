"""Pull ATT&CK data from MITRE's public TAXII 2.1 server.

Supports two modes:

1. Lookup refresh (the original use): fetch attack-pattern objects, rebuild
   data/attack_lookup.json. Local file is the fallback.
2. Structured ingestion: fetch attack-patterns, intrusion-sets and
   relationships. Return technique IDs grouped by threat group, so the
   pipeline can generate rules for all techniques a given group uses.

Usage:
    python data/taxii_connector.py            fetch and update the lookup
    python data/taxii_connector.py --check    fetch and compare, write nothing
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_attack_lookup import LOOKUP_PATH, build_lookup  # noqa: E402

TAXII_ROOT = "https://attack-taxii.mitre.org/api/v21/"
COLLECTION_TITLE = "Enterprise ATT&CK"
FETCHED_PATH = os.path.join(HERE, "enterprise-attack-taxii.json")
MIN_TECHNIQUES = 500


def _get_collection(root=TAXII_ROOT, title=COLLECTION_TITLE, timeout=60):
    """Return the TAXII Collection object for Enterprise ATT&CK."""
    import socket

    from taxii2client.v21 import ApiRoot, Collection

    socket.setdefaulttimeout(timeout)
    api_root = ApiRoot(root)
    match = [c for c in api_root.collections if c.title == title]
    if not match:
        names = [c.title for c in api_root.collections]
        raise RuntimeError(f"Collection '{title}' not found. Server has: {names}")
    return Collection(match[0].url)


def fetch_objects(root=TAXII_ROOT, title=COLLECTION_TITLE, timeout=60):
    """Return the list of STIX attack-pattern objects from the TAXII collection."""
    collection = _get_collection(root, title, timeout)
    objects = []
    for page in _pages(collection, stix_type="attack-pattern"):
        objects.extend(page.get("objects", []))
    return objects


def fetch_all_types(root=TAXII_ROOT, title=COLLECTION_TITLE, timeout=60):
    """Fetch attack-patterns, intrusion-sets and relationships from TAXII.

    Returns a dict with keys "attack-pattern", "intrusion-set", "relationship",
    each holding a list of STIX objects.
    """
    collection = _get_collection(root, title, timeout)
    result = {"attack-pattern": [], "intrusion-set": [], "relationship": []}
    for stix_type in result:
        for page in _pages(collection, stix_type=stix_type):
            result[stix_type].extend(page.get("objects", []))
    return result


def build_group_techniques(all_objects):
    """Map threat group names to the technique IDs they use.

    Uses intrusion-set objects and "uses" relationships that link an
    intrusion-set to an attack-pattern. Only active (not revoked, not
    deprecated) groups and techniques are included.

    Returns a dict like {"APT29": ["T1547.001", "T1059.001", ...], ...}.
    """
    # Build id-to-technique-id map from attack-patterns
    id_to_tid = {}
    for obj in all_objects.get("attack-pattern", []):
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                eid = ref.get("external_id", "")
                if eid.startswith("T"):
                    id_to_tid[obj["id"]] = eid
                break

    # Build id-to-group-name map from intrusion-sets
    id_to_group = {}
    for obj in all_objects.get("intrusion-set", []):
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        id_to_group[obj["id"]] = obj.get("name", obj["id"])

    # Walk relationships: intrusion-set --uses--> attack-pattern
    groups = {}
    for rel in all_objects.get("relationship", []):
        if rel.get("revoked") or rel.get("x_mitre_deprecated"):
            continue
        if rel.get("relationship_type") != "uses":
            continue
        src = rel.get("source_ref", "")
        tgt = rel.get("target_ref", "")
        group_name = id_to_group.get(src)
        tech_id = id_to_tid.get(tgt)
        if group_name and tech_id:
            groups.setdefault(group_name, [])
            if tech_id not in groups[group_name]:
                groups[group_name].append(tech_id)

    for tids in groups.values():
        tids.sort()
    return groups


def _pages(collection, stix_type="attack-pattern"):
    from taxii2client.v21 import as_pages

    for page in as_pages(
        collection.get_objects, per_request=500, type=stix_type
    ):
        yield page


def update_lookup(objects, write=True):
    """Save objects, rebuild the lookup, and return (new_lookup, old_lookup)."""
    bundle = {"type": "bundle", "objects": objects}
    with open(FETCHED_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f)
    new = build_lookup(FETCHED_PATH)

    old = {}
    if os.path.exists(LOOKUP_PATH):
        with open(LOOKUP_PATH, encoding="utf-8") as f:
            old = json.load(f)

    if len(new) < MIN_TECHNIQUES:
        raise RuntimeError(
            f"TAXII returned only {len(new)} techniques (need {MIN_TECHNIQUES}). "
            "Keeping the local lookup."
        )
    if write:
        with open(LOOKUP_PATH, "w", encoding="utf-8") as f:
            json.dump(new, f, indent=2, ensure_ascii=False)
    return new, old


def main():
    check_only = "--check" in sys.argv
    try:
        objects = fetch_objects()
        new, old = update_lookup(objects, write=not check_only)
    except Exception as e:
        print(f"TAXII unavailable, local lookup kept: {type(e).__name__}: {e}")
        return 1

    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(new) & set(old) if new[k] != old[k])
    print(f"TAXII returned {len(objects)} attack-pattern objects, {len(new)} active techniques")
    print(f"Local lookup had {len(old)}. New: {len(added)}, gone: {len(removed)}, changed: {len(changed)}")
    print("Check only, nothing written." if check_only else f"Wrote {LOOKUP_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
