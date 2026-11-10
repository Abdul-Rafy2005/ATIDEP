"""Build the all-runs summary without contacting Ollama."""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))

from compare_models import safe
from generate import TECHNIQUES as TECH1
from scoring import score_rule

RUNS = [
    "20261021_1510_set1_v1", "20261021_1510_01_set1_v1",
    "20261021_1511_set1_v2", "20261021_1528_set1_v1",
    "20261021_1534_set1_v2", "20261021_1536_set1_v2",
    "20261104_1503_set1_v2",
    "20261106_1338_set1_v2", "20261106_1344_set1_v2_1",
]


def run_rows(run_id, repo_root):
    folder = os.path.join(repo_root, "results", "runs", run_id)
    with open(os.path.join(folder, "settings.json"), encoding="utf-8") as sf:
        settings = json.load(sf)
    result_path = os.path.join(folder, "results.csv")
    expected = len(settings["models"]) * len(TECH1) * settings["repeats"]
    actual = sum(
        1 for root, _, files in os.walk(os.path.join(folder, "rules_first"))
        for name in files if name.endswith(".yml")
    )
    rows = []
    if not os.path.exists(result_path):
        for model in settings["models"]:
            rows.append([
                run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
                settings["temperature"], settings["repeats"], "-", "-", "-", "-",
                f"PARTIAL {actual}/{expected} rules"
            ])
        return rows

    grouped = defaultdict(list)
    with open(result_path, encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            grouped[row["model"]].append(row)

    set_num = settings["set"]
    repeats = int(settings["repeats"])

    for model, values in grouped.items():
        total = len(values)
        first_single = 0
        first_strict = 0
        final_single = 0
        final_strict = 0

        for row in values:
            tech = row["technique"]
            repeat_num = row.get("repeat", "1")
            filename = tech + (f"_repeat{repeat_num}" if repeats > 1 else "") + ".yml"
            p_first = os.path.join(folder, "rules_first", safe(model), filename)
            p_final = os.path.join(folder, "rules_final", safe(model), filename)

            with open(p_first, encoding="utf-8") as sf:
                res_first = score_rule(set_num, tech, sf.read())
            if res_first.single_pass:
                first_single += 1
            if res_first.strict_pass:
                first_strict += 1

            if os.path.exists(p_final):
                with open(p_final, encoding="utf-8") as sf:
                    res_final = score_rule(set_num, tech, sf.read())
                if res_final.single_pass:
                    final_single += 1
                if res_final.strict_pass:
                    final_strict += 1
            else:
                if res_first.single_pass:
                    final_single += 1
                if res_first.strict_pass:
                    final_strict += 1

        rows.append([
            run_id, settings["date"][:10], settings["set"], settings["prompt"], model,
            settings["temperature"], settings["repeats"],
            f"{first_single}/{total}",
            f"{first_strict}/{total}",
            f"{final_single}/{total}",
            f"{final_strict}/{total}",
            "COMPLETE"
        ])
    return rows


def archive_rows(repo_root):
    archive_dir = os.path.join(repo_root, "results", "archive", "prompt_v1", "model_outputs")
    models = [
        ("mistral:7b", "mistral_7b"),
        ("qwen2.5-coder:7b", "qwen2.5-coder_7b"),
        ("mistral-rules", "mistral-rules"),
        ("qwen2.5-coder:14b", "qwen2.5-coder_14b"),
    ]
    rows = []
    for model_name, folder_name in models:
        m_dir = os.path.join(archive_dir, folder_name)
        single_cnt = 0
        strict_cnt = 0
        for tech in TECH1:
            fn = os.path.join(m_dir, f"{tech}.yml")
            with open(fn, encoding="utf-8") as f:
                res = score_rule(1, tech, f.read())
            if res.single_pass:
                single_cnt += 1
            if res.strict_pass:
                strict_cnt += 1
        rows.append([
            "archive_v1_rescore", "2026-10-21", 1, "v1", model_name,
            0, 1,
            f"{single_cnt}/12",
            f"{strict_cnt}/12",
            "-", "-",
            "ARCHIVED"
        ])
    return rows


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(repo_root, "results", "RESULTS_SUMMARY.md")
    rows = []
    for run_id in RUNS:
        rows.extend(run_rows(run_id, repo_root))
    rows.extend(archive_rows(repo_root))
    rows.append([
        "repair_hint_v2_14b", "2026-11-04", 1, "v2", "qwen2.5-coder:14b",
        0.2, 3, "-", "-", "-", "-",
        "superseded: run as 20261106_1338_set1_v2"
    ])

    with open(path, "w", encoding="utf-8") as output:
        output.write("# ATIDEP Results Summary\n\n")
        output.write("| id | date | set | prompt | model | temperature | repeats | single pass (first try) | strict pass (first try) | final single pass | final strict pass | notes |\n")
        output.write("| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for row in rows:
            output.write("| " + " | ".join(str(value) for value in row) + " |\n")
        output.write("\nUnder the true strict gate requiring the hidden variant, set 1 separates prompt versions and reveals overfitting: qwen 7b achieves 9/36 under v2 and 11/36 under v2_1, while qwen 14b achieves 8/36 under both. Most failures on set 1 are TOO_NARROW (rules that overfit to the shown command line).\n\n")
        output.write("Set 2 is the prompt v1 baseline only.\n")
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()
