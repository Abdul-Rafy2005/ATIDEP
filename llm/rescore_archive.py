"""Re-score archived prompt v1 rules on set 1 with hidden variants."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))
from runner import rule_matches, rule_to_sql
from generate import make_pair
from analyze_results import analyze_rule
from compare_models import safe


MODELS = ["mistral:7b", "qwen2.5-coder:7b", "mistral-rules", "qwen2.5-coder:14b"]
EXPECTED_SINGLE = {"mistral:7b": 4, "qwen2.5-coder:7b": 10,
                   "mistral-rules": 10, "qwen2.5-coder:14b": 11}


def score_single(rule, tech):
    try:
        rule_to_sql(rule)
    except Exception:
        return False
    shown, benign = make_pair(tech)
    return rule_matches(rule, shown) and not rule_matches(rule, benign)


def main():
    techniques = [row["technique"] for row in
                  csv.DictReader(open("results/techniques.csv", encoding="utf-8"))]
    rows = []
    for model in MODELS:
        single = strict = narrow = 0
        folder = os.path.join("results", "archive", "prompt_v1", "model_outputs", safe(model))
        for tech in techniques:
            path = os.path.join(folder, tech + ".yml")
            if not os.path.exists(path):
                print(f"{model:24} {tech:10} missing")
                continue
            with open(path, encoding="utf-8") as saved_rule:
                rule = saved_rule.read()
            single += score_single(rule, tech)
            result = analyze_rule(rule, tech, 1)
            strict += result["verdict"] == "PASS"
            narrow += result["verdict"] == "TOO_NARROW"
        rows.append((model, single, strict, narrow))

    print("model                     single gate  strict gate  TOO_NARROW")
    for model, single, strict, narrow in rows:
        print(f"{model:24} {single:11} {strict:12} {narrow:11}")
    actual = {model: single for model, single, _, _ in rows}
    if actual != EXPECTED_SINGLE:
        raise SystemExit(f"Expected single-gate counts {EXPECTED_SINGLE}, got {actual}; archive differs from the stated baseline.")

    path = "results/archive/prompt_v1/set1_strict_rescore.md"
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    with open(path, "w", encoding="utf-8") as output:
        output.write("# Set 1 strict rescore of archived prompt v1 rules\n\n")
        output.write("| Model | Single gate pass | Strict gate pass | TOO_NARROW |\n")
        output.write("| --- | ---: | ---: | ---: |\n")
        for model, single, strict, narrow in rows:
            output.write(f"| {model} | {single} | {strict} | {narrow} |\n")
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()