"""TAXII-based structured ingestion for the ATIDEP pipeline.

Given a threat group name (e.g. "APT29"), this module:
1. Pulls group-to-technique mappings from MITRE's TAXII server.
2. Filters to the techniques our pipeline can handle (those with synthetic
   logs in sets 1, 2 or 3).
3. Returns the technique list so the pipeline can generate and validate
   a Sigma rule for each one.

If the TAXII server is unreachable, the module falls back to the local
attack_lookup.json and returns all supported techniques (no group filter).

Usage from Python:
    from data.taxii_ingest import ingest_by_group, list_groups
    groups = list_groups()           # {"APT29": ["T1547.001", ...], ...}
    result = ingest_by_group("APT29")  # filtered to our supported set
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _supported_technique_ids():
    """Return the set of technique IDs that our pipeline has synthetic logs for."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    from generator.techniques_set3 import TECHNIQUES3 as T3
    return set(T1) | set(T2) | set(T3)


def list_groups(timeout=60):
    """Fetch group-to-technique mappings from TAXII.

    Returns {"group_name": ["T1234", ...], ...} on success.
    Returns None if the TAXII server cannot be reached.
    """
    try:
        from data.taxii_connector import fetch_all_types, build_group_techniques
        all_objects = fetch_all_types(timeout=timeout)
        return build_group_techniques(all_objects)
    except Exception:
        return None


def ingest_by_group(group_name, timeout=60):
    """Return pipeline-ready technique info for a threat group.

    On success returns:
        {
            "source": "taxii",
            "group": "APT29",
            "total_techniques": 42,
            "supported_techniques": 8,
            "techniques": [
                {"id": "T1547.001", "name": "Registry Run Keys...",
                 "set": 1, "supported": True},
                ...
            ]
        }

    If the group is not found, "techniques" is empty.
    If the TAXII server is unreachable, source is "local_fallback" and
    all supported techniques are returned (no group filter).
    """
    from data.attack_lookup import get_name

    supported = _supported_technique_ids()
    groups = list_groups(timeout=timeout)

    if groups is not None:
        tids = groups.get(group_name, [])
        techniques = []
        for tid in sorted(tids):
            techniques.append({
                "id": tid,
                "name": get_name(tid),
                "supported": tid in supported,
                "set": _which_set(tid) if tid in supported else None,
            })
        return {
            "source": "taxii",
            "group": group_name,
            "total_techniques": len(techniques),
            "supported_techniques": sum(1 for t in techniques if t["supported"]),
            "techniques": techniques,
        }

    # Fallback: return all supported techniques, no group filter
    techniques = []
    for tid in sorted(supported):
        techniques.append({
            "id": tid,
            "name": get_name(tid),
            "supported": True,
            "set": _which_set(tid),
        })
    return {
        "source": "local_fallback",
        "group": None,
        "total_techniques": len(techniques),
        "supported_techniques": len(techniques),
        "techniques": techniques,
    }


def ingest_all_groups(timeout=60):
    """Return a summary of all groups and how many of their techniques we cover.

    Returns a list of dicts sorted by supported count (descending):
        [{"group": "APT29", "total": 42, "supported": 8}, ...]

    Returns None if TAXII is unreachable.
    """
    groups = list_groups(timeout=timeout)
    if groups is None:
        return None
    supported = _supported_technique_ids()
    result = []
    for name, tids in groups.items():
        sup = sum(1 for t in tids if t in supported)
        result.append({"group": name, "total": len(tids), "supported": sup})
    result.sort(key=lambda x: (-x["supported"], x["group"]))
    return result


def _which_set(tid):
    """Return the set number a technique belongs to (1, 2 or 3)."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    if tid in T1:
        return 1
    if tid in T2:
        return 2
    return 3
