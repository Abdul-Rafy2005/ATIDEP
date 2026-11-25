"""Threat-informed prioritisation for ATIDEP.

Ranks ATT&CK techniques by how many active threat groups use them, so a
defender can decide which uncovered technique to build a detection for next.

The ranking uses group-to-technique mappings from MITRE's TAXII 2.1 server.
When TAXII is unreachable the module still returns our 44 pipeline techniques
with coverage status but without group counts.

Usage:
    from export.prioritisation import build_priority_backlog
    backlog = build_priority_backlog()
    for row in backlog["backlog"][:10]:
        print(row["id"], row["name"], row["group_count"], row["covered"])
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _mitre_url(tid):
    """Build a MITRE ATT&CK URL from a technique ID like T1059.001."""
    parts = tid.split(".")
    path = parts[0]
    if len(parts) > 1:
        path += "/" + parts[1]
    return f"https://attack.mitre.org/techniques/{path}/"


def _supported_technique_ids():
    """Return the set of 44 technique IDs our pipeline has synthetic logs for."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    from generator.techniques_set3 import TECHNIQUES3 as T3
    return set(T1) | set(T2) | set(T3)


def _which_set(tid):
    """Return the set number a technique belongs to (1, 2 or 3), or None."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    if tid in T1:
        return 1
    if tid in T2:
        return 2
    return 3


def _covered_techniques():
    """Return set of technique IDs that have at least one strict-pass rule.

    Uses the run CSV verdicts directly (fast) instead of re-scoring every
    rule from disk.
    """
    import csv
    runs_dir = os.path.join(ROOT, "results", "runs")
    if not os.path.isdir(runs_dir):
        return set()

    covered = set()
    for folder in os.listdir(runs_dir):
        folder_path = os.path.join(runs_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        if os.path.exists(os.path.join(folder_path, "INVALID_PARTIAL.txt")):
            continue
        results_path = os.path.join(folder_path, "results.csv")
        if not os.path.isfile(results_path):
            continue
        with open(results_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("strict_pass") == "True":
                    tid = row.get("technique", "")
                    if tid:
                        covered.add(tid)
    return covered


def _invert_groups(group_map):
    """Invert {group: [techniques]} to {technique: set(groups)}."""
    tech_groups = {}
    for group, tids in group_map.items():
        for tid in tids:
            tech_groups.setdefault(tid, set()).add(group)
    return tech_groups


def build_priority_backlog(timeout=30):
    """Build a prioritised backlog of ATT&CK techniques.

    Returns a dict with:
        source: "taxii" or "local_only"
        total_attack_techniques: number of techniques in the full ATT&CK catalog
        total_groups: number of threat groups found (0 if local_only)
        our_techniques: 44 (how many we have synthetic logs for)
        covered: how many of our 44 have a passing rule
        backlog: list of dicts sorted by priority (see below)

    Each backlog entry:
        id, name, tactics, group_count, top_groups (up to 5 names),
        in_pipeline (bool), covered (bool), set (1/2/3 or None)

    Sort order: uncovered-in-pipeline first (by group_count desc),
    then not-in-pipeline (by group_count desc),
    then covered (by group_count desc).
    """
    from data.attack_lookup import all_techniques, get_technique

    supported = _supported_technique_ids()
    covered_set = _covered_techniques()
    all_techs = all_techniques()

    # Try TAXII for group data
    group_map = None
    try:
        from data.taxii_ingest import list_groups
        group_map = list_groups(timeout=timeout)
    except Exception:
        pass

    source = "taxii" if group_map is not None else "local_only"
    tech_groups = _invert_groups(group_map) if group_map else {}
    total_groups = len(group_map) if group_map else 0

    backlog = []
    seen = set()

    # Walk all ATT&CK techniques from the lookup
    for tid, info in all_techs.items():
        seen.add(tid)
        groups_using = tech_groups.get(tid, set())
        in_pipeline = tid in supported
        is_covered = tid in covered_set
        backlog.append({
            "id": tid,
            "name": info.get("name", tid),
            "tactics": info.get("tactics", []),
            "url": info.get("url", "") or _mitre_url(tid),
            "group_count": len(groups_using),
            "top_groups": sorted(groups_using)[:5],
            "in_pipeline": in_pipeline,
            "covered": is_covered,
            "set": _which_set(tid) if in_pipeline else None,
        })

    # Add any supported technique not in the lookup (should not happen, but safe)
    for tid in supported:
        if tid not in seen:
            groups_using = tech_groups.get(tid, set())
            backlog.append({
                "id": tid,
                "name": tid,
                "tactics": [],
                "url": _mitre_url(tid),
                "group_count": len(groups_using),
                "top_groups": sorted(groups_using)[:5],
                "in_pipeline": True,
                "covered": tid in covered_set,
                "set": _which_set(tid),
            })

    # Sort: uncovered-in-pipeline first, then not-in-pipeline, then covered
    def sort_key(row):
        if row["in_pipeline"] and not row["covered"]:
            bucket = 0
        elif not row["in_pipeline"]:
            bucket = 1
        else:
            bucket = 2
        return (bucket, -row["group_count"], row["id"])

    backlog.sort(key=sort_key)

    return {
        "source": source,
        "total_attack_techniques": len(all_techs),
        "total_groups": total_groups,
        "our_techniques": len(supported),
        "covered": len(covered_set & supported),
        "backlog": backlog,
    }
