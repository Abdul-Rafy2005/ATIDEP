"""Data loader for the ATIDEP dashboard.

Reads results/, coverage/, generator/ and builds JSON-friendly data
for the Flask API endpoints.
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import yaml

RUNS_DIR = os.path.join(ROOT, "results", "runs")
ARCHIVE_DIR = os.path.join(ROOT, "results", "archive", "prompt_v1", "model_outputs")
COVERAGE_CSV = os.path.join(ROOT, "coverage", "coverage.csv")

# ATT&CK tactic ID to name mapping
TACTIC_NAMES = {
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0010": "Exfiltration",
    "TA0011": "Command and Control",
    "TA0040": "Impact",
    "TA0042": "Resource Development",
    "TA0043": "Reconnaissance",
}

# Tactic names to IDs (reverse)
TACTIC_NAME_TO_ID = {v: k for k, v in TACTIC_NAMES.items()}

# Technique tactic mapping (from Sigma tags and ATT&CK)
TECHNIQUE_TACTIC_MAP = {
    # Set 1
    "T1059.001": ["Execution"],
    "T1218.011": ["Defense Evasion"],
    "T1218.005": ["Defense Evasion"],
    "T1218.010": ["Defense Evasion"],
    "T1105": ["Defense Evasion", "Command and Control"],
    "T1053.005": ["Privilege Escalation", "Execution", "Persistence"],
    "T1547.001": ["Privilege Escalation", "Persistence"],
    "T1136.001": ["Persistence"],
    "T1003.001": ["Defense Evasion", "Credential Access"],
    "T1197": ["Persistence", "Execution", "Defense Evasion", "Command and Control"],
    "T1047": ["Execution"],
    "T1033": ["Privilege Escalation", "Discovery"],
    # Set 2
    "T1218.001": ["Defense Evasion"],
    "T1021.002": ["Lateral Movement"],
    "T1560.001": ["Collection"],
    "T1222.001": ["Defense Evasion"],
    "T1489": ["Impact"],
    "T1482": ["Discovery"],
    "T1218.008": ["Defense Evasion"],
    "T1546.007": ["Privilege Escalation", "Persistence"],
    "T1090": ["Lateral Movement", "Command and Control"],
    "T1485": ["Impact"],
    "T1490": ["Impact"],
    "T1059": ["Execution"],
    # Set 3
    "T1003.002": ["Credential Access"],
    "T1021.006": ["Lateral Movement"],
    "T1040": ["Credential Access", "Discovery"],
    "T1053.002": ["Persistence", "Execution", "Privilege Escalation"],
    "T1082": ["Discovery"],
    "T1112": ["Persistence", "Defense Evasion"],
    "T1113": ["Collection"],
    "T1123": ["Collection"],
    "T1176.001": ["Persistence"],
    "T1185": ["Credential Access", "Collection"],
    "T1202": ["Execution", "Defense Evasion"],
    "T1218": ["Defense Evasion"],
    "T1219.002": ["Command and Control", "Persistence"],
    "T1220": ["Defense Evasion"],
    "T1529": ["Impact"],
    "T1563.002": ["Lateral Movement"],
    "T1564.004": ["Command and Control", "Defense Evasion"],
    "T1572": ["Command and Control", "Lateral Movement"],
    "T1574": ["Privilege Escalation", "Persistence", "Execution", "Defense Evasion"],
    "T1615": ["Discovery"],
}


def _technique_set(tid):
    """Return which set(s) a technique belongs to."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    from generator.techniques_set3 import TECHNIQUES3 as T3
    sets = []
    if tid in T1:
        sets.append(1)
    if tid in T2:
        sets.append(2)
    if tid in T3:
        sets.append(3)
    return sets


def load_runs():
    """Load all experiment runs from results/runs/."""
    runs = []
    if not os.path.isdir(RUNS_DIR):
        return runs
    for folder in sorted(os.listdir(RUNS_DIR)):
        run_dir = os.path.join(RUNS_DIR, folder)
        settings_path = os.path.join(run_dir, "settings.json")
        results_path = os.path.join(run_dir, "results.csv")
        invalid_path = os.path.join(run_dir, "INVALID_PARTIAL.txt")
        if os.path.isfile(invalid_path):
            continue
        if not os.path.isfile(settings_path) or not os.path.isfile(results_path):
            continue
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        results = []
        with open(results_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
        # Compute summary stats
        total = len(results)
        strict_pass = sum(1 for r in results if r.get("strict_pass") == "True")
        single_pass = sum(1 for r in results if r.get("single_pass") == "True")
        syntax_errors = sum(1 for r in results if r.get("verdict") == "SYNTAX_ERROR")
        too_narrow = sum(1 for r in results if r.get("verdict") == "TOO_NARROW")
        missed = sum(1 for r in results if r.get("verdict") == "MISSED_SHOWN")
        noisy = sum(1 for r in results if r.get("verdict") == "NOISY")

        # Determine label (primary/exploratory/baseline)
        label = "development"
        set_num = settings.get("set", 0)
        prompt = settings.get("prompt", "")
        models = settings.get("models", [])
        if set_num == 3:
            if prompt == "v1":
                label = "baseline"
            elif len(models) == 1:
                model = models[0]
                if (model == "qwen2.5-coder:14b" and prompt == "v3b") or \
                   (model == "qwen2.5-coder:7b" and prompt == "v3a"):
                    label = "primary"
                else:
                    label = "exploratory"

        runs.append({
            "folder": folder,
            "date": settings.get("date", ""),
            "set": set_num,
            "prompt": prompt,
            "models": models,
            "temperature": settings.get("temperature", 0),
            "repeats": settings.get("repeats", 1),
            "seed": settings.get("seed", 0),
            "total": total,
            "strict_pass": strict_pass,
            "single_pass": single_pass,
            "syntax_errors": syntax_errors,
            "too_narrow": too_narrow,
            "missed": missed,
            "noisy": noisy,
            "label": label,
            "results": results,
        })
    return runs


def load_techniques():
    """Build a unified technique list with metadata and best verdicts."""
    techniques = {}

    # Read coverage.csv for technique metadata
    if os.path.isfile(COVERAGE_CSV):
        with open(COVERAGE_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row["technique_id"]
                tactics_raw = row.get("tactic", "")
                tactics = [t.strip() for t in tactics_raw.split(";") if t.strip()]
                techniques[tid] = {
                    "id": tid,
                    "tactics": tactics,
                    "tactic_ids": [TACTIC_NAME_TO_ID.get(t, "") for t in tactics],
                    "title": row.get("reference_rule_title", ""),
                    "sets": _technique_set(tid),
                    "ref_status": row.get("reference_rule_status", ""),
                    "best_verdict": "NOT_TESTED",
                    "configs": {},
                }

    # Also pull from the tactic map for any missing
    for tid, tacs in TECHNIQUE_TACTIC_MAP.items():
        if tid not in techniques:
            techniques[tid] = {
                "id": tid,
                "tactics": tacs,
                "tactic_ids": [TACTIC_NAME_TO_ID.get(t, "") for t in tacs],
                "title": "",
                "sets": _technique_set(tid),
                "ref_status": "",
                "best_verdict": "NOT_TESTED",
                "configs": {},
            }

    # Walk runs and collect per-technique verdicts
    runs = load_runs()
    for run in runs:
        for row in run["results"]:
            tid = row.get("technique", "")
            if tid not in techniques:
                continue
            model = row.get("model", "")
            prompt = run["prompt"]
            repeat = row.get("repeat", "1")
            config_key = f"{model}|{prompt}|r{repeat}|set{run['set']}"
            verdict = row.get("verdict", "NOT_TESTED")
            techniques[tid]["configs"][config_key] = {
                "model": model,
                "prompt": prompt,
                "repeat": int(repeat),
                "set": run["set"],
                "run_folder": run["folder"],
                "verdict": verdict,
                "strict_pass": row.get("strict_pass") == "True",
                "single_pass": row.get("single_pass") == "True",
            }

    # Compute best verdict per technique
    verdict_priority = {"PASS": 0, "TOO_NARROW": 1, "NOISY": 2, "MISSED_SHOWN": 3, "SYNTAX_ERROR": 4, "NOT_TESTED": 5}
    for tid, tech in techniques.items():
        best = "NOT_TESTED"
        for cfg in tech["configs"].values():
            v = cfg["verdict"]
            if verdict_priority.get(v, 5) < verdict_priority.get(best, 5):
                best = v
        tech["best_verdict"] = best

    return techniques


def load_tactic_coverage():
    """Compute coverage percentage per tactic for the radar chart."""
    techniques = load_techniques()
    tactic_stats = {}
    for tid, tech in techniques.items():
        for tactic in tech["tactics"]:
            if tactic not in tactic_stats:
                tactic_stats[tactic] = {"total": 0, "covered": 0}
            tactic_stats[tactic]["total"] += 1
            if tech["best_verdict"] == "PASS":
                tactic_stats[tactic]["covered"] += 1

    result = []
    for tactic_name, stats in sorted(tactic_stats.items(),
                                      key=lambda x: TACTIC_NAME_TO_ID.get(x[0], "")):
        tactic_id = TACTIC_NAME_TO_ID.get(tactic_name, "")
        pct = round(100 * stats["covered"] / stats["total"], 1) if stats["total"] > 0 else 0
        result.append({
            "tactic_id": tactic_id,
            "tactic_name": tactic_name,
            "total": stats["total"],
            "covered": stats["covered"],
            "coverage_pct": pct,
        })
    return result


def load_overview():
    """Compute headline numbers for the overview page."""
    techniques = load_techniques()
    runs = load_runs()
    total_techniques = len(techniques)
    covered = sum(1 for t in techniques.values() if t["best_verdict"] == "PASS")
    coverage_pct = round(100 * covered / total_techniques, 1) if total_techniques > 0 else 0
    total_rules = sum(r["total"] for r in runs)

    # Find latest run
    latest = runs[-1] if runs else None

    return {
        "total_techniques": total_techniques,
        "covered": covered,
        "coverage_pct": coverage_pct,
        "total_rules_tested": total_rules,
        "total_runs": len(runs),
        "latest_run": {
            "folder": latest["folder"],
            "set": latest["set"],
            "prompt": latest["prompt"],
            "models": latest["models"],
            "strict_pass": latest["strict_pass"],
            "total": latest["total"],
            "label": latest["label"],
        } if latest else None,
    }


def load_run_detail(folder):
    """Load detailed results for a single run."""
    runs = load_runs()
    for run in runs:
        if run["folder"] == folder:
            return run
    return None


def load_technique_detail(technique_id):
    """Load all run results for a single technique, plus test events."""
    techniques = load_techniques()
    tech = techniques.get(technique_id)
    if not tech:
        return None

    # Load test events from generator
    events = {}
    for set_num in tech["sets"]:
        try:
            from llm.scoring import score_rule
            if set_num == 1:
                from generator.generate import make_triple as mt
            elif set_num == 2:
                from generator.techniques_set2 import make_triple as mt
            elif set_num == 3:
                from generator.techniques_set3 import make_triple3 as mt
            shown, variant, benign = mt(technique_id)
            events[str(set_num)] = {
                "shown": shown.get("CommandLine", ""),
                "variant": variant.get("CommandLine", ""),
                "benign": benign.get("CommandLine", ""),
                "shown_image": shown.get("Image", ""),
            }
        except Exception:
            pass

    tech["events"] = events
    return tech


def load_prompt_comparison():
    """Build prompt comparison data for the grouped bar chart."""
    runs = load_runs()
    comparison = []
    for run in runs:
        if run["total"] == 0:
            continue
        for model in run["models"]:
            model_results = [r for r in run["results"] if r.get("model") == model]
            total = len(model_results)
            strict = sum(1 for r in model_results if r.get("strict_pass") == "True")
            comparison.append({
                "folder": run["folder"],
                "set": run["set"],
                "prompt": run["prompt"],
                "model": model,
                "label": run["label"],
                "total": total,
                "strict_pass": strict,
                "strict_pct": round(100 * strict / total, 1) if total > 0 else 0,
            })
    return comparison


def load_rule_text(run_folder, model, technique, repeat):
    """Load a saved rule YAML from a run folder."""
    # Normalize model name for folder path (: and / replaced with _)
    model_folder = model.replace(":", "_").replace("/", "_")
    rule_path = os.path.join(
        RUNS_DIR, run_folder, "rules_first",
        model_folder, f"{technique}_repeat{repeat}.yml"
    )
    if os.path.isfile(rule_path):
        with open(rule_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

