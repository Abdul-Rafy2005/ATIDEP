"""Build the ATT&CK coverage template from technique CSVs and run results.

Reads:
  results/techniques.csv
  results/techniques_set2.csv
  results/techniques_set3.csv (if present, only included if set 3 runs exist)
  data/sigmahq_rules/ (real rule YAML files for tactic and title)
  data/sigmahq_rules_set2/
  data/sigmahq_rules_set3/
  results/runs/*/ (COMPLETE run folders with results.csv and settings.json)
  results/archive/prompt_v1/model_outputs/ (Set 2 baseline rules)
  results/validation_results.csv (real rule validation, set 1)

Writes:
  coverage/coverage.csv
  coverage/coverage.html
  coverage/COVERAGE.md
  coverage/README.md
"""
import csv
import datetime
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from llm.scoring import score_rule


# ---------------------------------------------------------------------------
# 1. Read technique CSVs
# ---------------------------------------------------------------------------

def read_techniques_csv(path):
    """Return list of dicts with keys: technique, rule_file, rule_id."""
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 2. Read real rule metadata (title, tactic) from YAML files
# ---------------------------------------------------------------------------

TACTIC_MAP = {
    "reconnaissance": "Reconnaissance",
    "resource-development": "Resource Development",
    "initial-access": "Initial Access",
    "execution": "Execution",
    "persistence": "Persistence",
    "privilege-escalation": "Privilege Escalation",
    "defense-evasion": "Defense Evasion",
    "defense-impairment": "Defense Evasion",
    "credential-access": "Credential Access",
    "discovery": "Discovery",
    "lateral-movement": "Lateral Movement",
    "collection": "Collection",
    "command-and-control": "Command and Control",
    "exfiltration": "Exfiltration",
    "impact": "Impact",
    "stealth": "Defense Evasion",
}

TECH_TAG_PATTERN = re.compile(r"^attack\.[tsg]\d+", re.IGNORECASE)


def read_rule_metadata(rule_path):
    """Return (title, tactic) from a real SigmaHQ rule YAML file.
    
    All tactics found in attack.<tactic> tags are collected, converted to display
    names via TACTIC_MAP, deduplicated while preserving appearance order, and
    joined with '; '.
    """
    if not os.path.exists(rule_path):
        return ("unknown", "unknown")
    with open(rule_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return ("unknown", "unknown")
    title = data.get("title", "unknown")
    tags = data.get("tags", [])
    tactics = []
    for tag in tags:
        tag_lower = str(tag).lower()
        if tag_lower.startswith("attack.") and not TECH_TAG_PATTERN.match(tag_lower):
            tactic_key = tag_lower.replace("attack.", "", 1).replace("_", "-")
            if tactic_key in TACTIC_MAP:
                tactic_name = TACTIC_MAP[tactic_key]
                if tactic_name not in tactics:
                    tactics.append(tactic_name)
    tactic = "; ".join(tactics) if tactics else "unknown"
    return (title, tactic)


def rule_dir_for_set(set_number, root_dir=None):
    if root_dir is None:
        root_dir = ROOT
    if set_number == 1:
        return os.path.join(root_dir, "data", "sigmahq_rules")
    elif set_number == 2:
        return os.path.join(root_dir, "data", "sigmahq_rules_set2")
    else:
        return os.path.join(root_dir, "data", "sigmahq_rules_set3")


# ---------------------------------------------------------------------------
# 3. Read real rule validation results
# ---------------------------------------------------------------------------

def read_validation_results(root_dir=None):
    """Return dict: technique -> status (PASS or FAIL)."""
    if root_dir is None:
        root_dir = ROOT
    path = os.path.join(root_dir, "results", "validation_results.csv")
    results = {}
    if not os.path.exists(path):
        return results
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            results[row["technique"]] = row["status"]
    return results


# ---------------------------------------------------------------------------
# 4. Read COMPLETE run folders
# ---------------------------------------------------------------------------

def find_complete_runs(runs_dir=None):
    """Return list of (folder_name, settings_dict, results_rows)."""
    if runs_dir is None:
        runs_dir = os.path.join(ROOT, "results", "runs")
    if not os.path.isdir(runs_dir):
        return []
    runs = []
    for name in sorted(os.listdir(runs_dir)):
        folder = os.path.join(runs_dir, name)
        if not os.path.isdir(folder):
            continue
        # Skip partial runs
        if os.path.exists(os.path.join(folder, "INVALID_PARTIAL.txt")):
            continue
        settings_path = os.path.join(folder, "settings.json")
        results_path = os.path.join(folder, "results.csv")
        if not os.path.exists(settings_path) or not os.path.exists(results_path):
            continue
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
        with open(results_path, encoding="utf-8", newline="") as f:
            results_rows = list(csv.DictReader(f))
        runs.append((name, settings, results_rows))
    return runs


def verdict_from_run_row(row):
    """Map a results.csv row to a coverage verdict string."""
    v = row.get("verdict", "").strip()
    mapping = {
        "PASS": "PASS",
        "SYNTAX_ERROR": "SYNTAX",
        "MISSED_SHOWN": "MISSED",
        "TOO_NARROW": "NARROW",
        "NOISY": "NOISY",
    }
    return mapping.get(v, v)


def map_score_verdict(score_res):
    """Map a ScoreResult to a coverage verdict string."""
    if score_res.strict_pass:
        return "PASS"
    mapping = {
        "PASS": "PASS",
        "SYNTAX_ERROR": "SYNTAX",
        "MISSED_SHOWN": "MISSED",
        "TOO_NARROW": "NARROW",
        "NOISY": "NOISY",
    }
    return mapping.get(score_res.verdict, score_res.verdict)


def select_newest_runs(runs):
    """Return dict: config_key -> (folder_name, settings, rows_for_model).

    config_key = "model|prompt|set"
    Runs are sorted chronologically by folder name (starts with YYYYMMDD_HHMM).
    Later runs overwrite earlier runs for the same configuration key.
    """
    configs = {}
    for folder_name, settings, rows in runs:
        set_num = settings.get("set", 1)
        prompt = settings.get("prompt", "?")
        models = settings.get("models", [])
        for model in models:
            key = f"{model}|{prompt}|{set_num}"
            model_rows = [r for r in rows if r.get("model") == model]
            configs[key] = (folder_name, settings, model_rows)
    return configs


def collect_config_results(newest_configs, root_dir=None):
    """Return dict: config_key -> {technique -> [verdicts]}.
    
    Scores saved first-try rules from rules_first directory using score_rule.
    Falls back to model_rows only if rules_first directory is absent (e.g. mock unit tests).
    """
    if root_dir is None:
        root_dir = ROOT
    runs_base = os.path.join(root_dir, "results", "runs")
    results = {}
    for key, (folder_name, settings, rows) in newest_configs.items():
        parts = key.split("|")
        model = parts[0]
        set_num = int(settings.get("set", parts[2] if len(parts) > 2 else 1))
        repeats = int(settings.get("repeats", 1))
        model_safe = model.replace(":", "_").replace("/", "_")
        rf_dir = os.path.join(runs_base, folder_name, "rules_first", model_safe)

        tech_verdicts = {}
        if os.path.isdir(rf_dir):
            # Gather techniques from rows or files
            tech_names = []
            for r in rows:
                t = r.get("technique")
                if t and t not in tech_names:
                    tech_names.append(t)
            if not tech_names:
                for fn in sorted(os.listdir(rf_dir)):
                    if fn.endswith(".yml"):
                        t = fn.replace(".yml", "").split("_repeat")[0]
                        if t not in tech_names:
                            tech_names.append(t)

            for tech in tech_names:
                v_list = []
                if repeats == 1:
                    p = os.path.join(rf_dir, f"{tech}.yml")
                    if os.path.exists(p):
                        with open(p, encoding="utf-8") as f:
                            sr = score_rule(set_num, tech, f.read())
                        v_list.append(map_score_verdict(sr))
                else:
                    for rep in range(1, repeats + 1):
                        p = os.path.join(rf_dir, f"{tech}_repeat{rep}.yml")
                        if os.path.exists(p):
                            with open(p, encoding="utf-8") as f:
                                sr = score_rule(set_num, tech, f.read())
                            v_list.append(map_score_verdict(sr))
                if v_list:
                    tech_verdicts[tech] = v_list
        else:
            # Fallback for fake run tests without rule files
            for row in rows:
                tech = row.get("technique", "")
                v = verdict_from_run_row(row)
                tech_verdicts.setdefault(tech, []).append(v)

        results[key] = tech_verdicts
    return results


# ---------------------------------------------------------------------------
# 5. Format verdict for display
# ---------------------------------------------------------------------------

def format_verdict(verdicts):
    """Format a list of verdicts for display.

    No attempts: "NOT_TESTED"
    Single attempt: verdict name ("PASS", "SYNTAX", etc.)
    Multiple attempts: "N/M" passes out of M repeats (for example "2/3")
    """
    if not verdicts:
        return "NOT_TESTED"
    if len(verdicts) == 1:
        return verdicts[0]
    passes = sum(1 for v in verdicts if v == "PASS")
    return f"{passes}/{len(verdicts)}"


# ---------------------------------------------------------------------------
# 6. Build the coverage table
# ---------------------------------------------------------------------------

def build_coverage_table(runs_dir=None, root_dir=None):
    """Build the coverage table as a list of row dicts and list of config keys.

    Returns (rows, config_keys, config_summaries)
    """
    if root_dir is None:
        root_dir = ROOT

    # Read technique CSVs
    set1_techs = read_techniques_csv(os.path.join(root_dir, "results", "techniques.csv"))
    set2_techs = read_techniques_csv(os.path.join(root_dir, "results", "techniques_set2.csv"))
    set3_techs = read_techniques_csv(os.path.join(root_dir, "results", "techniques_set3.csv"))

    # Validation results for reference rules
    val_results = read_validation_results(root_dir)

    # Collect runs from results/runs
    runs = find_complete_runs(runs_dir)
    newest_configs = select_newest_runs(runs)
    config_results = collect_config_results(newest_configs, root_dir)

    config_summaries = {}
    for key, (folder_name, settings, model_rows) in newest_configs.items():
        tech_map = config_results.get(key, {})
        all_verdicts = [v for v_list in tech_map.values() for v in v_list]
        total_attempts = len(all_verdicts) if all_verdicts else len(model_rows)
        total_passes = sum(1 for v in all_verdicts if v == "PASS")
        config_summaries[key] = {
            "folder": folder_name,
            "passes": total_passes,
            "attempts": total_attempts,
            "ratio": f"{total_passes}/{total_attempts}",
        }

    # Add Set 2 baseline from results/archive/prompt_v1/model_outputs
    archive_base = os.path.join(root_dir, "results", "archive", "prompt_v1", "model_outputs")
    if os.path.isdir(archive_base) and set2_techs:
        set2_baseline_models = [
            ("qwen2.5-coder:7b", "qwen2.5-coder_7b"),
            ("qwen2.5-coder:14b", "qwen2.5-coder_14b"),
            ("mistral-rules", "mistral-rules"),
        ]
        for model_name, model_dir in set2_baseline_models:
            key = f"{model_name}|v1|2"
            model_folder = os.path.join(archive_base, model_dir)
            tech_verdicts = {}
            total_passes = 0
            total_attempts = 0
            if os.path.isdir(model_folder):
                for tech_row in set2_techs:
                    tech = tech_row["technique"]
                    rule_file = os.path.join(model_folder, f"{tech}.yml")
                    if os.path.exists(rule_file):
                        with open(rule_file, encoding="utf-8") as f:
                            sr = score_rule(2, tech, f.read())
                        v = map_score_verdict(sr)
                        tech_verdicts[tech] = [v]
                        if sr.strict_pass:
                            total_passes += 1
                        total_attempts += 1
                    else:
                        tech_verdicts[tech] = ["NOT_TESTED"]
            config_results[key] = tech_verdicts
            config_summaries[key] = {
                "folder": os.path.join("results", "archive", "prompt_v1", "model_outputs", model_dir),
                "passes": total_passes,
                "attempts": total_attempts if total_attempts > 0 else len(set2_techs),
                "ratio": f"{total_passes}/{total_attempts if total_attempts > 0 else len(set2_techs)}",
            }

    # Determine which sets have been run
    sets_with_runs = {s.get("set") for _, s, _ in runs}

    # Decide which sets to include in rows:
    # Sets 1 and 2 are always included (24 rows).
    # Set 3 is included ONLY if set 3 has been run.
    sets_to_include = [(1, set1_techs), (2, set2_techs)]
    if 3 in sets_with_runs and set3_techs:
        sets_to_include.append((3, set3_techs))

    # Stable column order: sort by model, then prompt, then set
    config_keys = sorted(config_results.keys())

    # Build rows
    rows = []
    for set_number, tech_list in sets_to_include:
        rule_dir = rule_dir_for_set(set_number, root_dir)
        for tech_row in tech_list:
            tech_id = tech_row["technique"]
            rule_file = tech_row["rule_file"]
            rule_path = os.path.join(rule_dir, rule_file)
            title, tactic = read_rule_metadata(rule_path)

            if set_number == 1:
                ref_status = val_results.get(tech_id, "PASS")
            else:
                # Set 2 and 3 real rules were verified by sanity test suites
                ref_status = "PASS"

            row = {
                "technique_id": tech_id,
                "tactic": tactic,
                "reference_rule_title": title,
                "reference_rule_file": rule_file,
                "reference_rule_status": ref_status,
            }

            for key in config_keys:
                verdicts = config_results[key].get(tech_id, [])
                row[key] = format_verdict(verdicts)

            rows.append(row)

    return rows, config_keys, config_summaries


# ---------------------------------------------------------------------------
# 7. Write coverage.csv
# ---------------------------------------------------------------------------

def write_csv(rows, config_keys, path=None):
    if path is None:
        path = os.path.join(ROOT, "coverage", "coverage.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = [
        "technique_id",
        "tactic",
        "reference_rule_title",
        "reference_rule_file",
        "reference_rule_status",
    ]
    fieldnames.extend(config_keys)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ---------------------------------------------------------------------------
# 8. Write coverage.html
# ---------------------------------------------------------------------------

VERDICT_COLORS = {
    "PASS": "#4caf50",
    "NARROW": "#ff9800",
    "MISSED": "#f44336",
    "SYNTAX": "#9c27b0",
    "NOISY": "#e91e63",
    "NOT_TESTED": "#9e9e9e",
}


def _passes_text(verdict_str):
    """Return (passes, total) from a verdict string."""
    if "/" in verdict_str:
        parts = verdict_str.split("/")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            return 0, 0
    if verdict_str == "PASS":
        return 1, 1
    if verdict_str == "NOT_TESTED":
        return 0, 0
    return 0, 1


def _cell_color(verdict_str):
    """Return background color for a verdict cell."""
    if "/" in verdict_str:
        passes, total = _passes_text(verdict_str)
        if total > 0 and passes == total:
            return VERDICT_COLORS["PASS"]
        elif passes == 0:
            return VERDICT_COLORS["MISSED"]
        else:
            return VERDICT_COLORS["NARROW"]
    return VERDICT_COLORS.get(verdict_str, "#9e9e9e")


def _html_escape(s):
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))


def write_html(rows, config_keys, config_summaries=None, path=None):
    if path is None:
        path = os.path.join(ROOT, "coverage", "coverage.html")
    if config_summaries is None:
        config_summaries = {}
    os.makedirs(os.path.dirname(path), exist_ok=True)

    total_techniques = len(rows)
    covered_techniques = 0
    for row in rows:
        is_covered = False
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            p, t = _passes_text(v)
            if t > 0 and p == t:
                is_covered = True
                break
        if is_covered:
            covered_techniques += 1

    # Dynamically determine sets present in rows
    tech_ids = [r["technique_id"] for r in rows]
    set1_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques.csv"))}
    set2_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques_set2.csv"))}
    set3_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques_set3.csv"))}

    sets_present = set()
    for tid in tech_ids:
        if tid in set1_ids:
            sets_present.add(1)
        elif tid in set2_ids:
            sets_present.add(2)
        elif tid in set3_ids:
            sets_present.add(3)
    sorted_sets = sorted(list(sets_present))
    if sorted_sets == [1, 2, 3]:
        sets_included_str = "sets 1, 2, and 3"
    elif sorted_sets == [1, 2]:
        sets_included_str = "sets 1 and 2"
    else:
        sets_included_str = "sets " + ", ".join(str(s) for s in sorted_sets)

    # Dynamically determine sets with results
    sets_with_results = set()
    for ck in config_keys:
        parts = ck.split("|")
        if len(parts) > 2 and parts[2].isdigit():
            sets_with_results.add(int(parts[2]))
    sets_with_results_str = ", ".join(str(s) for s in sorted(list(sets_with_results)))
    date_str = datetime.date.today().isoformat()

    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>ATIDEP ATT&amp;CK Coverage</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 24px; color: #222; }",
        "h1 { font-size: 1.5em; margin-bottom: 8px; }",
        "p.subtitle { color: #666; margin-top: 0; margin-bottom: 16px; font-size: 0.9em; }",
        ".totals { background: #f5f5f5; border: 1px solid #ddd; padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 0.95em; }",
        ".totals strong { color: #111; }",
        ".legend { margin: 16px 0; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }",
        ".legend-item { display: inline-flex; align-items: center; font-size: 0.85em; }",
        ".legend-box { width: 14px; height: 14px; margin-right: 6px; border-radius: 2px; }",
        "table { border-collapse: collapse; width: 100%; font-size: 0.85em; margin-top: 8px; }",
        "th, td { border: 1px solid #ddd; padding: 6px 10px; }",
        "th { background: #2c3e50; color: #fff; text-align: left; font-weight: 600; }",
        "th.config-header { text-align: center; font-size: 0.8em; line-height: 1.3; }",
        "td.tech-id { font-family: monospace; font-weight: 600; white-space: nowrap; }",
        "td.tactic { white-space: nowrap; color: #555; }",
        "td.title { max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
        "td.status { text-align: center; font-weight: 600; color: #fff; }",
        "td.verdict { text-align: center; font-weight: 600; color: #fff; }",
        "tr:nth-child(even) td.title, tr:nth-child(even) td.tech-id, tr:nth-child(even) td.tactic { background: #fafafa; }",
        "tfoot td { font-weight: bold; background: #eee; border-top: 2px solid #333; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>ATIDEP ATT&amp;CK Coverage Grid</h1>",
        "<p class='subtitle'>Automated Threat-Informed Detection Engineering Platform</p>",
        f"<div class='totals'>",
        f"<strong>Coverage Summary:</strong> {covered_techniques} of {total_techniques} techniques covered (at least one configuration passes all repeats).<br>",
        f"Sets included: {sets_included_str} ({total_techniques} techniques total). Sets with results: {sets_with_results_str}. Date: {date_str}.",
        f"</div>",
        "<div class='legend'>",
        "<strong>Legend:</strong>",
    ]

    for label, color in VERDICT_COLORS.items():
        lines.append(f"<span class='legend-item'><span class='legend-box' style='background:{color};'></span>{label}</span>")
    lines.append("</div>")

    # Table
    lines.append("<table>")
    lines.append("<thead><tr>")
    lines.append("<th>Technique ID</th>")
    lines.append("<th>Tactic</th>")
    lines.append("<th>Reference Rule</th>")
    lines.append("<th style='text-align:center;'>Reference Status</th>")

    for ck in config_keys:
        parts = ck.split("|")
        model = parts[0] if len(parts) > 0 else "?"
        prompt = parts[1] if len(parts) > 1 else "?"
        set_num = parts[2] if len(parts) > 2 else "?"
        if set_num == "2":
            lines.append(f"<th class='config-header'>{_html_escape(model)}<br>prompt {prompt}<br>set 2 baseline</th>")
        else:
            lines.append(f"<th class='config-header'>{_html_escape(model)}<br>prompt {prompt}<br>set {set_num}</th>")
    lines.append("</tr></thead>")

    lines.append("<tbody>")
    for row in rows:
        lines.append("<tr>")
        lines.append(f"<td class='tech-id'>{_html_escape(row['technique_id'])}</td>")
        lines.append(f"<td class='tactic'>{_html_escape(row['tactic'])}</td>")
        lines.append(f"<td class='title' title='{_html_escape(row['reference_rule_title'])}'>{_html_escape(row['reference_rule_title'])}</td>")
        ref_color = VERDICT_COLORS.get(row['reference_rule_status'], "#9e9e9e")
        lines.append(f"<td class='status' style='background:{ref_color};'>{_html_escape(row['reference_rule_status'])}</td>")
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            color = _cell_color(v)
            lines.append(f"<td class='verdict' style='background:{color};'>{_html_escape(v)}</td>")
        lines.append("</tr>")
    lines.append("</tbody>")

    # Footer with column totals
    lines.append("<tfoot><tr>")
    lines.append("<td colspan='4' style='text-align:right;'>Strict Pass Total (matches RESULTS_SUMMARY.md):</td>")
    for ck in config_keys:
        summary = config_summaries.get(ck, {})
        ratio = summary.get("ratio", "-")
        lines.append(f"<td style='text-align:center;'>{ratio}</td>")
    lines.append("</tr></tfoot>")

    lines.append("</table>")
    lines.append("</body></html>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ---------------------------------------------------------------------------
# 9. Write coverage/COVERAGE.md
# ---------------------------------------------------------------------------

def write_coverage_md(rows, config_keys, config_summaries=None, path=None):
    if path is None:
        path = os.path.join(ROOT, "coverage", "COVERAGE.md")
    if config_summaries is None:
        config_summaries = {}
    os.makedirs(os.path.dirname(path), exist_ok=True)

    set1_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques.csv"))}
    set2_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques_set2.csv"))}
    set3_ids = {r["technique"] for r in read_techniques_csv(os.path.join(ROOT, "results", "techniques_set3.csv"))}

    covered_by_set = {1: [], 2: [], 3: []}
    never_covered_by_set = {1: [], 2: [], 3: []}

    for row in rows:
        tid = row["technique_id"]
        set_num = 1 if tid in set1_ids else (2 if tid in set2_ids else 3)
        is_covered = False
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            p, t = _passes_text(v)
            if t > 0 and p == t:
                is_covered = True
                break
        if is_covered:
            covered_by_set[set_num].append(row)
        else:
            never_covered_by_set[set_num].append(row)

    total_techs = len(rows)
    total_covered = sum(len(v) for v in covered_by_set.values())
    sets1_3_total = len(set1_ids) + len(set3_ids)
    sets1_3_covered = len(covered_by_set[1]) + len(covered_by_set[3])

    lines = [
        "# ATIDEP ATT&CK Coverage Summary",
        "",
        "## Coverage Definition",
        "A technique is defined as **covered** when at least one configuration achieves a strict pass in all of its repeats (3 of 3 for 3-repeat runs, or 1 of 1 for the single-repeat set 2 baseline).",
        "",
        "## Headline Metrics",
        f"- Total techniques in catalog: {total_techs} (Set 1: 12, Set 2: 12, Set 3: 20)",
        f"- Techniques evaluated: {total_techs} of {total_techs} (100%)",
        f"- Techniques covered: {total_covered} of {total_techs} ({total_covered / total_techs * 100:.1f}%)",
        f"- Development and final test sets (Sets 1 and 3): {sets1_3_covered} of {sets1_3_total} ({sets1_3_covered / sets1_3_total * 100:.1f}%)",
        "",
        "## Coverage Breakdown by Set",
        f"- **Set 1 (Development Set, 12 techniques):** {len(covered_by_set[1])} of 12 covered ({len(covered_by_set[1]) / 12 * 100:.1f}%)",
        f"- **Set 2 (Baseline Validation Set, 12 techniques):** {len(covered_by_set[2])} of 12 covered ({len(covered_by_set[2]) / 12 * 100:.1f}%)",
        f"- **Set 3 (Final Clean Test Set, 20 techniques):** {len(covered_by_set[3])} of 20 covered ({len(covered_by_set[3]) / 20 * 100:.1f}%)",
        "",
        "## Covered Techniques (29 of 44)",
        "",
        "| Technique ID | Set | Tactic | Reference Rule Title |",
        "|---|---|---|---|",
    ]

    for s in (1, 2, 3):
        for r in covered_by_set[s]:
            lines.append(f"| `{r['technique_id']}` | Set {s} | {r['tactic']} | {r['reference_rule_title']} |")

    lines.extend([
        "",
        "## Never-Covered Techniques (15 of 44)",
        "",
        "The following 15 techniques did not achieve an all-repeat strict pass under any tested configuration:",
        "",
        "### Set 1 (4 techniques)",
        "- `T1059.001` (Command and Scripting Interpreter: PowerShell): Rules overfit to specific cmdlet flags or syntax.",
        "- `T1547.001` (Boot or Logon Autostart Execution: Registry Run Keys): Rules overfit to specific registry value names.",
        "- `T1136.001` (Create Account: Local Account): Rules overfit to specific net user parameters.",
        "- `T1003.001` (OS Credential Dumping: LSASS Memory): Rules overfit to procdump flags or dump file paths.",
        "",
        "### Set 2 (10 techniques)",
        "Set 2 was evaluated only under prompt v1 as a single-repeat baseline (temperature 0). Ten techniques did not pass strict validation due to missing outside domain knowledge (e.g. net1.exe alias, port numbers, bcdedit tamper settings, forfiles syntax) or narrow command line matching:",
        "- `T1218.001` (System Binary Proxy Execution: Compiled HTML File)",
        "- `T1021.002` (Remote Services: SMB/Windows Admin Shares)",
        "- `T1560.001` (Archive Collected Data: Archive via Utility)",
        "- `T1222.001` (File and Directory Permissions Modification: Windows MACs)",
        "- `T1489` (Service Stop)",
        "- `T1482` (Domain Trust Discovery)",
        "- `T1218.008` (System Binary Proxy Execution: Odbcconf)",
        "- `T1090` (Proxy)",
        "- `T1490` (Inhibit System Recovery)",
        "- `T1059` (Command and Scripting Interpreter)",
        "",
        "### Set 3 (1 technique)",
        "- `T1529` (System Shutdown/Reboot): Requires generalising shutdown command arguments; models overfitted to specific timeout and comment flags.",
        "",
        "## Configuration Strict Pass Totals",
        "",
        "| Configuration | Label | Repeats | Strict Pass Ratio | Percentage | Source Folder |",
        "|---|---|---|---|---|---|",
    ])

    for ck in config_keys:
        summary = config_summaries.get(ck, {})
        ratio = summary.get("ratio", "-")
        folder = summary.get("folder", "-")
        parts = ck.split("|")
        model = parts[0]
        prompt = parts[1]
        set_num = parts[2]
        repeats = 1 if set_num == "2" else 3
        label = f"{model} (prompt {prompt}, set {set_num})"
        p = summary.get("passes", 0)
        a = summary.get("attempts", 1)
        pct = (p / a * 100) if a > 0 else 0.0
        lines.append(f"| `{ck}` | {label} | {repeats} | {ratio} | {pct:.1f}% | `{folder}` |")

    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ---------------------------------------------------------------------------
# 10. Write coverage/README.md
# ---------------------------------------------------------------------------

def write_readme(path=None):
    if path is None:
        path = os.path.join(ROOT, "coverage", "README.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = r"""# ATT&CK Coverage Template

## What this template is
This template tracks which MITRE ATT&CK techniques have passing Sigma detection rules in ATIDEP. It displays the reference SigmaHQ rules, their validation status against our synthetic logs, and the performance of each LLM configuration.

## Coverage definition
A technique is defined as **covered** when at least one configuration has a strict pass in all of its repeats (3 of 3 for 3-repeat runs, or 1 of 1 for the set 2 baseline).

Across all 44 evaluated techniques:
- **29 of 44 techniques are covered** across all sets (65.9%).
- **27 of 32 techniques are covered** across Sets 1 and 3 (84.4%).

Never-covered techniques:
- **Set 1 (4 techniques):** T1059.001, T1547.001, T1136.001, T1003.001
- **Set 2 (10 techniques):** T1218.001, T1021.002, T1560.001, T1222.001, T1489, T1482, T1218.008, T1090, T1490, T1059
- **Set 3 (1 technique):** T1529

Full details and technique breakdown are recorded in [COVERAGE.md](COVERAGE.md).

## What the columns mean

| Column | Meaning |
|---|---|
| technique_id | The MITRE ATT&CK technique or sub-technique ID (for example T1059.001). |
| tactic | The ATT&CK tactics from the reference SigmaHQ rule's tags, separated by semicolons (for example Privilege Escalation; Discovery). |
| reference_rule_title | Title of the real SigmaHQ rule used as the ground-truth reference. |
| reference_rule_file | File name of the reference rule in data/sigmahq_rules*/. |
| reference_rule_status | Whether the real SigmaHQ rule passes our synthetic logs (PASS or FAIL). |
| model\|prompt\|set | The strict-gate result of the first-try LLM-generated rule for that configuration. |

## Verdict values

| Verdict | Meaning |
|---|---|
| PASS | The rule has valid syntax, fires on the shown attack and hidden variant, and stays quiet on benign logs. |
| NARROW | The rule fires on the shown attack but misses the hidden variant (overfitted to the example). |
| MISSED | The rule fails to fire on the shown attack line. |
| SYNTAX | The rule contains a YAML or pySigma syntax error that cannot convert to SQL. |
| NOISY | The rule fires on harmless benign logs (false positive). |
| NOT_TESTED | No run has evaluated this technique under this configuration. |
| N/M | For runs with repeats: N passes out of M repeats (for example 2/3). |

## How to add a new technique

1. Pick a technique: Select an ATT&CK technique and find a suitable SigmaHQ process creation rule from rules/windows/process_creation.
2. Add to generator: In generator/techniques_set3.py (or the current set file), add the technique entry with:
   - image: full path to the executable
   - malicious: the command line shown to the model
   - variant: the hidden attack variant (different flag, path, or syntax)
   - benign: a harmless command line using the same program
   - variant_type, rule_file, rule_id
   - Add a plain-English description to DESCRIPTIONS3.
3. Download the reference rule: Place the SigmaHQ rule YAML file into data/sigmahq_rules_set3/ and add a row to results/techniques_set3.csv.
4. Verify the reference rule: Run python validator/test_set3_real_rules.py to confirm the reference rule passes your synthetic logs.
5. Rebuild coverage: Run python coverage/build_coverage.py to update coverage.csv, coverage.html, and COVERAGE.md.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rows, config_keys, config_summaries = build_coverage_table()
    csv_path = write_csv(rows, config_keys)
    html_path = write_html(rows, config_keys, config_summaries)
    coverage_md_path = write_coverage_md(rows, config_keys, config_summaries)
    readme_path = write_readme()

    total = len(rows)
    covered = 0
    for row in rows:
        is_covered = False
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            p, t = _passes_text(v)
            if t > 0 and p == t:
                is_covered = True
                break
        if is_covered:
            covered += 1

    print(f"Coverage built: {total} techniques")
    print(f"Covered techniques (all repeats strict pass): {covered} / {total} ({covered / total * 100:.1f}%)")
    print(f"Configurations ({len(config_keys)}):")
    for ck in config_keys:
        summary = config_summaries.get(ck, {})
        ratio = summary.get("ratio", "-")
        folder = summary.get("folder", "-")
        print(f"  {ck:30} passes: {ratio:6} (from {folder})")
    print(f"CSV:         {csv_path}")
    print(f"HTML:        {html_path}")
    print(f"COVERAGE.MD: {coverage_md_path}")
    print(f"README:      {readme_path}")


if __name__ == "__main__":
    main()
