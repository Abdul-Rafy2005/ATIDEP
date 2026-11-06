"""Build the all-runs summary without contacting Ollama."""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from analyze_results import analyze_rule
from compare_models import safe


RUNS = [
    "20261021_1510_set1_v1", "20261021_1510_01_set1_v1",
    "20261021_1511_set1_v2", "20261021_1528_set1_v1",
    "20261021_1534_set1_v2", "20261021_1536_set1_v2",
    "20261104_1503_set1_v2",
]
TECHNIQUES = [
    "T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105",
    "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197",
    "T1047", "T1033",
]


def final_pass(folder, model, filename):
    path = os.path.join(folder, "rules_final", safe(model), filename)
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as source:
        text = source.read()
    technique = filename[:-4].split("_repeat", 1)[0]
    return analyze_rule(text, technique, 1)["verdict"] == "PASS"


def run_rows(run_id):
    folder = os.path.join("results", "runs", run_id)
    settings = json.load(open(os.path.join(folder, "settings.json"), encoding="utf-8"))
    result_path = os.path.join(folder, "results.csv")
    expected = len(settings["models"]) * len(TECHNIQUES) * settings["repeats"]
    actual = len(list(os.scandir(os.path.join(folder, "rules_first")))) if False else sum(
        1 for root, _, files in os.walk(os.path.join(folder, "rules_first")) for name in files if name.endswith(".yml"))
    rows = []
    if not os.path.exists(result_path):
        for model in settings["models"]:
            rows.append([run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
                         settings["temperature"], settings["repeats"], "-", "-", "-", "-",
                         f"PARTIAL {actual}/{expected} rules"])
        return rows
    grouped = defaultdict(list)
    with open(result_path, encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            grouped[row["model"]].append(row)
    for model, values in grouped.items():
        final_count = 0
        for row in values:
            filename = row["technique"] + (f"_repeat{row['repeat']}" if int(row["repeat"]) > 1 else "") + ".yml"
            final_count += final_pass(folder, model, filename)
        rows.append([run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
                     settings["temperature"], settings["repeats"],
                     f"{sum(row['single_pass'] == 'True' for row in values)}/{len(values)}",
                     f"{sum(row['strict_pass'] == 'True' for row in values)}/{len(values)}",
                     sum(row.get("single_syntax", "True") == "False" for row in values),
                     final_count, "COMPLETE"])
    return rows


def main():
    path = "results/RESULTS_SUMMARY.md"
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    rows = []
    for run_id in RUNS:
        rows.extend(run_rows(run_id))
    rows.extend([
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "mistral:7b", 0, 1, "4/12", "4/12", 0, "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "qwen2.5-coder:7b", 0, 1, "10/12", "10/12", 2, "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "mistral-rules", 0, 1, "10/12", "10/12", 0, "-", "ARCHIVED"],
        ["archive_v1_rescore", "2026-10-21", 1, "v1", "qwen2.5-coder:14b", 0, 1, "11/12", "11/12", 0, "-", "ARCHIVED"],
        ["repair_hint_v2_14b", "2026-11-04", 1, "v2", "qwen2.5-coder:14b", 0.2, 3, "-", "-", "-", "-", "NOT RUN: blocked by active Python processes"],
    ])
    with open(path, "w", encoding="utf-8") as output:
        output.write("# ATIDEP Results Summary\n\n")
        output.write("| id | date | set | prompt | model | temperature | repeats | single gate pass | strict gate pass | first-try syntax errors | final pass after repair | notes |\n")
        output.write("| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for row in rows:
            output.write("| " + " | ".join(str(value) for value in row) + " |\n")
        output.write("\nSet 1 variants cannot show generalisation, because a keyword rule passes all 12.\n\n")
        output.write("Set 2 is the prompt v1 baseline only.\n")
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()