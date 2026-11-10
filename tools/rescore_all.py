"""Rescore all saved runs and write results/rescore_strict_all.md."""
import os
import sys
import json
import csv
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))

from scoring import score_rule
from compare_models import safe
from generate import TECHNIQUES as TECH1
from techniques_set2 import TECHNIQUES2 as TECH2

RUNS = [
    "20261021_1510_set1_v1",
    "20261021_1510_01_set1_v1",
    "20261021_1511_set1_v2",
    "20261021_1528_set1_v1",
    "20261104_1503_set1_v2",
    "20261106_1338_set1_v2",
    "20261106_1344_set1_v2_1",
]

OLD_STRICT = {
    ("20261021_1510_set1_v1", "qwen2.5-coder:7b"): "10/12",
    ("20261021_1510_01_set1_v1", "qwen2.5-coder:7b"): "10/12",
    ("20261021_1511_set1_v2", "qwen2.5-coder:7b"): "12/12",
    ("20261021_1511_set1_v2", "qwen2.5-coder:14b"): "8/12",
    ("20261021_1528_set1_v1", "qwen2.5-coder:7b"): "28/36",
    ("20261021_1528_set1_v1", "qwen2.5-coder:14b"): "35/36",
    ("20261104_1503_set1_v2", "qwen2.5-coder:7b"): "36/36",
    ("20261104_1503_set1_v2", "qwen2.5-coder:14b"): "26/36",
    ("20261106_1338_set1_v2", "qwen2.5-coder:14b"): "26/36",
    ("20261106_1344_set1_v2_1", "qwen2.5-coder:7b"): "36/36",
    ("20261106_1344_set1_v2_1", "qwen2.5-coder:14b"): "36/36",
    ("archive_v1_set1", "mistral:7b"): "4/12",
    ("archive_v1_set1", "qwen2.5-coder:7b"): "10/12",
    ("archive_v1_set1", "mistral-rules"): "10/12",
    ("archive_v1_set1", "qwen2.5-coder:14b"): "11/12",
    ("archive_v1_set2", "qwen2.5-coder:7b"): "2/12",
    ("archive_v1_set2", "qwen2.5-coder:14b"): "2/12",
    ("archive_v1_set2", "mistral-rules"): "0/12",
}


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_table_rows = []

    # 1. Rescore COMPLETE runs in results/runs
    run_results = {}
    for r in RUNS:
        folder = os.path.join(repo_root, "results", "runs", r)
        with open(os.path.join(folder, "settings.json"), encoding="utf-8") as f:
            settings = json.load(f)
        result_path = os.path.join(folder, "results.csv")
        if not os.path.exists(result_path):
            continue
        grouped = defaultdict(list)
        with open(result_path, encoding="utf-8", newline="") as sf:
            for row in csv.DictReader(sf):
                grouped[row["model"]].append(row)

        set_num = settings["set"]
        prompt = settings["prompt"]
        temp = settings["temperature"]
        repeats = settings["repeats"]

        for model, rows in grouped.items():
            total = len(rows)
            first_single = 0
            first_strict = 0
            final_single = 0
            final_strict = 0
            first_verdicts = {"SYNTAX_ERROR": 0, "MISSED_SHOWN": 0, "NOISY": 0, "TOO_NARROW": 0, "PASS": 0}

            for row in rows:
                tech = row["technique"]
                repeat_num = row.get("repeat", "1")
                fn = tech + (f"_repeat{repeat_num}" if int(repeats) > 1 else "") + ".yml"
                p_first = os.path.join(folder, "rules_first", safe(model), fn)
                p_final = os.path.join(folder, "rules_final", safe(model), fn)

                with open(p_first, encoding="utf-8") as f:
                    content_first = f.read()
                res_first = score_rule(set_num, tech, content_first)
                first_verdicts[res_first.verdict] += 1
                if res_first.single_pass:
                    first_single += 1
                if res_first.strict_pass:
                    first_strict += 1

                if os.path.exists(p_final):
                    with open(p_final, encoding="utf-8") as f:
                        content_final = f.read()
                    res_final = score_rule(set_num, tech, content_final)
                    if res_final.single_pass:
                        final_single += 1
                    if res_final.strict_pass:
                        final_strict += 1
                else:
                    if res_first.single_pass:
                        final_single += 1
                    if res_first.strict_pass:
                        final_strict += 1

            old = OLD_STRICT.get((r, model), "-")
            strict_first_str = f"{first_strict}/{total}"
            changed = "yes" if old != strict_first_str else "no"

            run_results[(r, model)] = {
                "first_single": first_single,
                "first_strict": first_strict,
                "final_single": final_single,
                "final_strict": final_strict,
                "total": total,
                "verdicts": first_verdicts,
            }

            out_table_rows.append([
                r, set_num, prompt, model, temp, repeats,
                f"{first_single}/{total}",
                strict_first_str,
                f"{final_single}/{total}",
                f"{final_strict}/{total}",
                first_verdicts["SYNTAX_ERROR"],
                first_verdicts["MISSED_SHOWN"],
                first_verdicts["NOISY"],
                first_verdicts["TOO_NARROW"],
                old,
                changed,
            ])

    # 2. Rescore archived runs in results/archive/prompt_v1/model_outputs
    archive_dir = os.path.join(repo_root, "results", "archive", "prompt_v1", "model_outputs")
    arch_models_set1 = [
        ("mistral:7b", "mistral_7b"),
        ("qwen2.5-coder:7b", "qwen2.5-coder_7b"),
        ("mistral-rules", "mistral-rules"),
        ("qwen2.5-coder:14b", "qwen2.5-coder_14b"),
    ]

    for model_name, folder_name in arch_models_set1:
        m_dir = os.path.join(archive_dir, folder_name)
        first_single = 0
        first_strict = 0
        first_verdicts = {"SYNTAX_ERROR": 0, "MISSED_SHOWN": 0, "NOISY": 0, "TOO_NARROW": 0, "PASS": 0}
        for t in TECH1:
            fn = os.path.join(m_dir, f"{t}.yml")
            with open(fn, encoding="utf-8") as f:
                content = f.read()
            res = score_rule(1, t, content)
            first_verdicts[res.verdict] += 1
            if res.single_pass:
                first_single += 1
            if res.strict_pass:
                first_strict += 1
        old = OLD_STRICT.get(("archive_v1_set1", model_name), "-")
        strict_first_str = f"{first_strict}/12"
        changed = "yes" if old != strict_first_str else "no"
        out_table_rows.append([
            "archive_v1_set1", 1, "v1", model_name, 0, 1,
            f"{first_single}/12",
            strict_first_str,
            "-",
            "-",
            first_verdicts["SYNTAX_ERROR"],
            first_verdicts["MISSED_SHOWN"],
            first_verdicts["NOISY"],
            first_verdicts["TOO_NARROW"],
            old,
            changed,
        ])

    arch_models_set2 = [
        ("qwen2.5-coder:7b", "qwen2.5-coder_7b"),
        ("qwen2.5-coder:14b", "qwen2.5-coder_14b"),
        ("mistral-rules", "mistral-rules"),
    ]
    set2_results = {}
    for model_name, folder_name in arch_models_set2:
        m_dir = os.path.join(archive_dir, folder_name)
        first_single = 0
        first_strict = 0
        first_verdicts = {"SYNTAX_ERROR": 0, "MISSED_SHOWN": 0, "NOISY": 0, "TOO_NARROW": 0, "PASS": 0}
        for t in TECH2:
            fn = os.path.join(m_dir, f"{t}.yml")
            with open(fn, encoding="utf-8") as f:
                content = f.read()
            res = score_rule(2, t, content)
            first_verdicts[res.verdict] += 1
            if res.single_pass:
                first_single += 1
            if res.strict_pass:
                first_strict += 1
        old = OLD_STRICT.get(("archive_v1_set2", model_name), "-")
        strict_first_str = f"{first_strict}/12"
        changed = "yes" if old != strict_first_str else "no"
        set2_results[model_name] = first_verdicts
        out_table_rows.append([
            "archive_v1_set2", 2, "v1", model_name, 0, 1,
            f"{first_single}/12",
            strict_first_str,
            "-",
            "-",
            first_verdicts["SYNTAX_ERROR"],
            first_verdicts["MISSED_SHOWN"],
            first_verdicts["NOISY"],
            first_verdicts["TOO_NARROW"],
            old,
            changed,
        ])

    # 3. Assertions / Regression Checks
    # Regression check on Set 2 baseline
    expected_set2 = {
        "qwen2.5-coder:7b": {"PASS": 2, "SYNTAX_ERROR": 1, "MISSED_SHOWN": 1, "TOO_NARROW": 8, "NOISY": 0},
        "qwen2.5-coder:14b": {"PASS": 2, "SYNTAX_ERROR": 0, "MISSED_SHOWN": 3, "TOO_NARROW": 7, "NOISY": 0},
        "mistral-rules": {"PASS": 0, "SYNTAX_ERROR": 0, "MISSED_SHOWN": 6, "TOO_NARROW": 6, "NOISY": 0},
    }

    print("=== REGRESSION CHECKS ===")
    all_passed = True
    for m, exp in expected_set2.items():
        act = set2_results[m]
        match = (act == exp)
        status = "PASS" if match else "WARN"
        if not match:
            all_passed = False
        print(f"[{status}] Set 2 baseline for {m}: expected {exp}, got {act}")

    # Check run 20261106_1338
    run_1338 = run_results.get(("20261106_1338_set1_v2", "qwen2.5-coder:14b"))
    if run_1338:
        match_1338 = (run_1338["first_strict"] == 8 and run_1338["final_strict"] == 11 and run_1338["total"] == 36)
        status_1338 = "PASS" if match_1338 else "WARN"
        if not match_1338:
            all_passed = False
        print(f"[{status_1338}] Run 20261106_1338 strict: first_strict={run_1338['first_strict']}/36 (expected 8/36), final_strict={run_1338['final_strict']}/36 (expected 11/36)")
    else:
        print("[WARN] Run 20261106_1338 not found")
        all_passed = False

    # 4. Write results/rescore_strict_all.md
    out_file = os.path.join(repo_root, "results", "rescore_strict_all.md")
    with open(out_file, "w", encoding="utf-8") as out:
        out.write("# Rescore of All Saved Runs under True Strict Gate\n\n")
        out.write("This document records the true single-gate and strict-gate numbers for all saved complete runs and prompt v1 archives.\n\n")
        out.write("## Rescore Table\n\n")
        headers = [
            "run or archive id", "set", "prompt", "model", "temperature", "repeats",
            "single pass first try", "strict pass first try", "single pass final", "strict pass final",
            "SYNTAX_ERROR", "MISSED_SHOWN", "NOISY", "TOO_NARROW", "old strict number", "changed",
        ]
        out.write("| " + " | ".join(headers) + " |\n")
        out.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in out_table_rows:
            out.write("| " + " | ".join(str(v) for v in row) + " |\n")

        out.write("\n## Regression Checks\n\n")
        out.write("### Set 2 Baseline Counts\n\n")
        out.write("Baseline reported in AGENTS.md for set 2 (prompt v1, 12 techniques):\n\n")
        out.write("| Model | PASS | SYNTAX_ERROR | MISSED_SHOWN | TOO_NARROW | NOISY | Status |\n")
        out.write("| --- | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for m, exp in expected_set2.items():
            act = set2_results[m]
            st = "PASS" if act == exp else "WARN"
            out.write(f"| {m} | {act['PASS']} | {act['SYNTAX_ERROR']} | {act['MISSED_SHOWN']} | {act['TOO_NARROW']} | {act['NOISY']} | {st} |\n")

        out.write("\n### Run 20261106_1338 Repair Check\n\n")
        if run_1338:
            st = "PASS" if (run_1338["first_strict"] == 8 and run_1338["final_strict"] == 11) else "WARN"
            out.write(f"- First-try strict pass: {run_1338['first_strict']}/36 (expected 8/36)\n")
            out.write(f"- Final strict pass after repair: {run_1338['final_strict']}/36 (expected 11/36)\n")
            out.write(f"- Status: {st}\n")

    print(f"\nWritten {out_file}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

