"""Build the all-runs summary without contacting Ollama."""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))

from analyze_results import analyze_rule
from compare_models import safe
from runner import rule_matches, rule_to_sql
from generate import make_triple
from techniques_set2 import make_triple as make_triple2
from techniques_set3 import make_triple3


RUNS = [
    "20261021_1510_set1_v1", "20261021_1510_01_set1_v1",
    "20261021_1511_set1_v2", "20261021_1528_set1_v1",
    "20261021_1534_set1_v2", "20261021_1536_set1_v2",
    "20261104_1503_set1_v2",
    "20261106_1338_set1_v2", "20261106_1344_set1_v2_1",
]
TECHNIQUES = [
    "T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105",
    "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197",
    "T1047", "T1033",
]


def check_strict_variant(rule_text, tech, set_num):
    try:
        rule_to_sql(rule_text)
    except Exception:
        return False
    if set_num == 1:
        shown, variant, benign = make_triple(tech)
    elif set_num == 2:
        shown, variant, benign = make_triple2(tech)
    else:
        shown, variant, benign = make_triple3(tech)
    return (rule_matches(rule_text, shown) and
            rule_matches(rule_text, variant) and
            not rule_matches(rule_text, benign))


def run_rows(run_id):
    folder = os.path.join("results", "runs", run_id)
    settings = json.load(open(os.path.join(folder, "settings.json"), encoding="utf-8"))
    result_path = os.path.join(folder, "results.csv")
    expected = len(settings["models"]) * len(TECHNIQUES) * settings["repeats"]
    actual = sum(
        1 for root, _, files in os.walk(os.path.join(folder, "rules_first")) for name in files if name.endswith(".yml"))
    rows = []
    if not os.path.exists(result_path):
        for model in settings["models"]:
            rows.append([run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
                         settings["temperature"], settings["repeats"], "-", "-", "-", "-", "-",
                         f"PARTIAL {actual}/{expected} rules"])
        return rows
    grouped = defaultdict(list)
    with open(result_path, encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            grouped[row["model"]].append(row)
    for model, values in grouped.items():
        first_pass_count = 0
        repaired_count_single = 0
        repaired_count_strict = 0
        syntax_error_count = 0
        for row in values:
            filename = row["technique"] + (f"_repeat{row['repeat']}" if int(settings["repeats"]) > 1 else "") + ".yml"
            p_first = os.path.join(folder, "rules_first", safe(model), filename)
            p_final = os.path.join(folder, "rules_final", safe(model), filename)
            with open(p_first, encoding="utf-8") as sf:
                res_first = analyze_rule(sf.read(), row["technique"], settings["set"])
            if res_first["verdict"] == "PASS":
                first_pass_count += 1
            elif res_first["verdict"] == "SYNTAX_ERROR":
                syntax_error_count += 1
                with open(p_final, encoding="utf-8") as sf:
                    final_text = sf.read()
                    res_final = analyze_rule(final_text, row["technique"], settings["set"])
                if res_final["verdict"] == "PASS":
                    repaired_count_single += 1
                if check_strict_variant(final_text, row["technique"], settings["set"]):
                    repaired_count_strict += 1
        final_pass_single = first_pass_count + repaired_count_single
        final_pass_strict = first_pass_count + repaired_count_strict
        rows.append([run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
                     settings["temperature"], settings["repeats"],
                     f"{sum(row['single_pass'] == 'True' for row in values)}/{len(values)}",
                     f"{first_pass_count}/{len(values)}",
                     syntax_error_count,
                     final_pass_single,
                     final_pass_strict,
                     "COMPLETE"])
    return rows


def main():
    path = "results/RESULTS_SUMMARY.md"
    rows = []
    for run_id in RUNS:
        rows.extend(run_rows(run_id))
    rows.extend([
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "mistral:7b", 0, 1, "4/12", "4/12", 0, "-", "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "qwen2.5-coder:7b", 0, 1, "10/12", "10/12", 2, "-", "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "mistral-rules", 0, 1, "10/12", "10/12", 0, "-", "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "qwen2.5-coder:14b", 0, 1, "11/12", "11/12", 0, "-", "-", "ARCHIVED"],
        ["repair_hint_v2_14b", "2026-11-04", 1, "v2", "qwen2.5-coder:14b", 0.2, 3, "-", "-", "-", "-", "-", "superseded: run as 20261106_1338_set1_v2"],
    ])
    with open(path, "w", encoding="utf-8") as output:
        output.write("# ATIDEP Results Summary\n\n")
        output.write("| id | date | set | prompt | model | temperature | repeats | single gate pass | strict gate pass | first-try syntax errors | final pass after repair (single gate) | final strict pass after repair | notes |\n")
        output.write("| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for row in rows:
            output.write("| " + " | ".join(str(value) for value in row) + " |\n")
        output.write("\nSet 1 variants cannot show generalisation, because a keyword rule passes all 12.\n\n")
        output.write("Set 2 is the prompt v1 baseline only.\n")
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()
