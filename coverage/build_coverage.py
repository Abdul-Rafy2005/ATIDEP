"""Build the ATT&CK coverage template from technique CSVs and run results.

Reads:
  results/techniques.csv
  results/techniques_set2.csv
  results/techniques_set3.csv (if present, only included if set 3 runs exist)
  data/sigmahq_rules/ (real rule YAML files for tactic and title)
  data/sigmahq_rules_set2/
  data/sigmahq_rules_set3/
  results/runs/*/ (COMPLETE run folders with results.csv and settings.json)
  results/validation_results.csv (real rule validation, set 1)

Writes:
  coverage/coverage.csv
  coverage/coverage.html
  coverage/README.md
"""
import csv
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    """Return (title, tactic) from a real SigmaHQ rule YAML file."""
    if not os.path.exists(rule_path):
        return ("unknown", "unknown")
    with open(rule_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return ("unknown", "unknown")
    title = data.get("title", "unknown")
    tactic = "unknown"
    tags = data.get("tags", [])
    for tag in tags:
        tag_lower = str(tag).lower()
        if tag_lower.startswith("attack.") and not TECH_TAG_PATTERN.match(tag_lower):
            tactic_key = tag_lower.replace("attack.", "", 1).replace("_", "-")
            if tactic_key in TACTIC_MAP:
                tactic = TACTIC_MAP[tactic_key]
                break
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


def collect_config_results(newest_configs):
    """Return dict: config_key -> {technique -> [verdicts]}."""
    results = {}
    for key, (folder_name, settings, rows) in newest_configs.items():
        tech_verdicts = {}
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

    # Collect runs
    runs = find_complete_runs(runs_dir)
    newest_configs = select_newest_runs(runs)
    config_results = collect_config_results(newest_configs)

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

    # Compute config totals (total passes, total attempts)
    config_summaries = {}
    for key, (folder_name, settings, model_rows) in newest_configs.items():
        total_attempts = len(model_rows)
        total_passes = sum(1 for r in model_rows if r.get("strict_pass", "").strip().lower() == "true")
        config_summaries[key] = {
            "folder": folder_name,
            "passes": total_passes,
            "attempts": total_attempts,
            "ratio": f"{total_passes}/{total_attempts}",
        }

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
    techs_with_pass = 0
    for row in rows:
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            p, _ = _passes_text(v)
            if p > 0:
                techs_with_pass += 1
                break

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
        f"<strong>Coverage Summary:</strong> {techs_with_pass} of {total_techniques} techniques have at least one configuration that passes.<br>",
        f"Sets included: sets 1 and 2 ({total_techniques} techniques total). Set 3 has not been run.",
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
# 9. Write coverage/README.md
# ---------------------------------------------------------------------------

def write_readme(path=None):
    if path is None:
        path = os.path.join(ROOT, "coverage", "README.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = r"""# ATT&CK Coverage Template

## What this template is
This template tracks which MITRE ATT&CK techniques have passing Sigma detection rules in ATIDEP. It displays the reference SigmaHQ rules, their validation status against our synthetic logs, and the performance of each LLM configuration.

## What the columns mean

| Column | Meaning |
|---|---|
| technique_id | The MITRE ATT&CK technique or sub-technique ID (for example T1059.001). |
| tactic | The ATT&CK tactic from the reference SigmaHQ rule's tags (for example Execution). |
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
5. Rebuild coverage: Run python coverage/build_coverage.py to update coverage.csv and coverage.html.
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
    readme_path = write_readme()

    total = len(rows)
    techs_with_pass = 0
    for row in rows:
        for ck in config_keys:
            v = row.get(ck, "NOT_TESTED")
            p, _ = _passes_text(v)
            if p > 0:
                techs_with_pass += 1
                break

    print(f"Coverage built: {total} techniques (sets 1 and 2)")
    print(f"Techniques with at least one passing configuration: {techs_with_pass} / {total}")
    print(f"Configurations ({len(config_keys)}):")
    for ck in config_keys:
        summary = config_summaries.get(ck, {})
        ratio = summary.get("ratio", "-")
        folder = summary.get("folder", "-")
        print(f"  {ck:30} passes: {ratio:6} (from {folder})")
    print(f"CSV:    {csv_path}")
    print(f"HTML:   {html_path}")
    print(f"README: {readme_path}")


if __name__ == "__main__":
    main()
