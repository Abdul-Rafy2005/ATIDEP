"""Write the requested prompt v1 versus v2 set 1 comparison."""
import csv
import glob
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))
from runner import rule_matches, rule_to_sql
from generate import make_pair
from analyze_results import analyze_rule
from compare_models import safe


MODELS = ["qwen2.5-coder:7b", "qwen2.5-coder:14b"]


def single_pass(rule, tech):
    try:
        rule_to_sql(rule)
    except Exception:
        return False
    shown, benign = make_pair(tech)
    return rule_matches(rule, shown) and not rule_matches(rule, benign)


def score_folder(folder, model):
    techniques = [row["technique"] for row in
                  csv.DictReader(open("results/techniques.csv", encoding="utf-8"))]
    rows = []
    for tech in techniques:
        path = os.path.join(folder, safe(model), tech + ".yml")
        with open(path, encoding="utf-8") as saved_rule:
            rule = saved_rule.read()
        result = analyze_rule(rule, tech, 1)
        rows.append((single_pass(rule, tech), result))
    return rows


def summary(rows):
    verdicts = Counter(result["verdict"] for _, result in rows)
    return {
        "single": sum(single for single, _ in rows),
        "strict": verdicts["PASS"],
        "syntax": verdicts["SYNTAX_ERROR"],
        "missed": verdicts["MISSED_SHOWN"],
        "narrow": verdicts["TOO_NARROW"],
        "noisy": verdicts["NOISY"],
        "padded": sum(result["padded_values"] for _, result in rows),
        "duplicate": sum(bool(result["duplicate_keys"]) for _, result in rows),
    }


def main():
    v2_runs = sorted(glob.glob("results/runs/*_set1_v2"))
    if not v2_runs:
        raise SystemExit("No set 1 prompt v2 run folder found")
    v2_folder = os.path.join(v2_runs[-1], "rules_first")
    v1_folder = "results/archive/prompt_v1/model_outputs"
    path = "results/prompt_v1_vs_v2_set1.md"
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    values = []
    for model in MODELS:
        values.append((model, "v1", summary(score_folder(v1_folder, model))))
        values.append((model, "v2", summary(score_folder(v2_folder, model))))
    with open(path, "w", encoding="utf-8") as output:
        output.write("# Prompt v1 versus v2 on set 1\n\n")
        output.write("| Model | Prompt | Single gate pass | Strict gate pass | SYNTAX_ERROR | MISSED_SHOWN | TOO_NARROW | NOISY | padded_values | duplicate_keys |\n")
        output.write("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for model, prompt, value in values:
            output.write(f"| {model} | {prompt} | {value['single']} | {value['strict']} | "
                         f"{value['syntax']} | {value['missed']} | {value['narrow']} | "
                         f"{value['noisy']} | {value['padded']} | {value['duplicate']} |\n")
    print(f"SAVED {path}")
    for model, prompt, value in values:
        print(model, prompt, value)


if __name__ == "__main__":
    main()