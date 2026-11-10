"""Explain verdicts and common failure patterns in saved Sigma rules."""
import argparse
import datetime
import os
import re
import sys
from collections import Counter

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))
from runner import rule_matches, rule_to_sql
from generate import TECHNIQUES, make_pair, make_triple as make_triple_set1
from techniques_set2 import TECHNIQUES2, make_triple
from techniques_set3 import TECHNIQUES3, make_triple3
from compare_models import safe, evaluate
from compare_set2 import evaluate2
from scoring import score_rule


def evaluate3(rule_text, tech):
    out = dict(syntax=False, caught=False, quiet=False, error="")
    try:
        rule_to_sql(rule_text)
        out["syntax"] = True
    except Exception as e:
        out["error"] = str(e)[:150]
        return out
    mal, var, ben = make_triple3(tech)
    hit_shown = rule_matches(rule_text, mal)
    hit_variant = rule_matches(rule_text, var)
    out["caught"] = hit_shown and hit_variant
    out["quiet"] = not rule_matches(rule_text, ben)
    if hit_shown and not hit_variant:
        out["error"] = "too narrow: caught the shown attack but missed the hidden variant"
    elif not hit_shown:
        out["error"] = "missed the shown attack"
    return out

IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
DRIVE_PATH = re.compile(r"\b[A-Za-z]:\\")
FLAGS = ("duplicate_keys", "invented_metadata", "padded_values",
         "instance_specific_values", "COPIED")
METADATA = {"id", "related", "author", "date", "modified", "references"}


class DuplicateKeyLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)
        self.duplicates = []

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping and key not in self.duplicates:
                self.duplicates.append(key)
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def inspect_yaml(rule_text):
    loader = DuplicateKeyLoader(rule_text)
    try:
        data = loader.get_single_data()
    finally:
        loader.dispose()
    return data, list(loader.duplicates)


def detection_values(node, field=None):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "condition":
                continue
            yield from detection_values(value, str(key).split("|", 1)[0])
    elif isinstance(node, list):
        for value in node:
            yield from detection_values(value, field)
    elif isinstance(node, str):
        yield field, node


def detection_block(data):
    return data.get("detection", {}) if isinstance(data, dict) else {}


def copied_ratio(data, shown):
    candidates = [value.strip() for field, value in detection_values(detection_block(data), "")
                  if field == "CommandLine" and value.strip()]
    longest = max((len(value) for value in candidates if value in shown), default=0)
    return longest / len(shown) if shown else 0


def analyze_rule(rule_text, technique, set_number):
    if set_number == 1:
        techniques = TECHNIQUES
        shown, variant_event, _ = make_triple_set1(technique)
    elif set_number == 2:
        techniques = TECHNIQUES2
        shown, variant_event, _ = make_triple(technique)
    else:
        techniques = TECHNIQUES3
        shown, variant_event, _ = make_triple3(technique)
    if technique not in techniques:
        raise KeyError(technique)
    variant = variant_event

    sc = score_rule(set_number, technique, rule_text)
    verdict = sc.verdict

    try:
        data, duplicates = inspect_yaml(rule_text)
    except Exception:
        data, duplicates = {}, []

    values = list(detection_values(detection_block(data)))
    strings = [value for _, value in values]
    padded = any(value != value.strip() for value in strings)
    if set_number in (2, 3):
        specific = any(field == "CommandLine" and value.strip() in shown["CommandLine"]
                       and value.strip() not in variant["CommandLine"]
                       for field, value in values if value.strip())
    else:
        # Set 1 has no hidden variant, so use obvious IOCs, drive paths, or long values.
        specific = any(IPV4.search(value) or DRIVE_PATH.search(value) or len(value) > 30
                       for value in strings)
    ratio = copied_ratio(data, shown["CommandLine"])
    return {
        "verdict": verdict,
        "error": sc.error,
        "duplicate_keys": duplicates,
        "invented_metadata": sorted(set(data) & METADATA) if isinstance(data, dict) else [],
        "padded_values": padded,
        "instance_specific_values": specific,
        "copied": ratio >= 0.6,
        "shown": shown["CommandLine"],
        "variant": variant["CommandLine"] if variant else "",
        "detection": detection_block(data),
    }


def format_flags(result):
    names = ["duplicate_keys", "invented_metadata", "padded_values",
             "instance_specific_values"]
    flags = [name for name in names if result[name]]
    if result["copied"]:
        flags.append("COPIED")
    return ",".join(flags) or "-"


def has_flag(result, flag):
    key = "copied" if flag == "COPIED" else flag
    return bool(result["duplicate_keys"] if key == "duplicate_keys" else result[key])


def print_summary(model_results, set_number):
    for model, rows in model_results.items():
        verdicts = Counter(row["result"]["verdict"] for row in rows)
        flags = Counter()
        for row in rows:
            for flag in FLAGS:
                if has_flag(row["result"], flag):
                    flags[flag] += 1
        print(f"SUMMARY {model}")
        print("  verdicts: " + ", ".join(f"{key}={verdicts[key]}" for key in
              ("PASS", "SYNTAX_ERROR", "MISSED_SHOWN", "TOO_NARROW", "NOISY")))
        print("  flags: " + ", ".join(f"{key}={flags[key]}" for key in FLAGS))
        if set_number == 1:
            print(f"  PASS flagged COPIED: {sum(row['result']['verdict'] == 'PASS' and row['result']['copied'] for row in rows)}")


def write_report(path, model_results, set_number):
    with open(path, "w", encoding="utf-8") as report:
        report.write(f"ATIDEP saved-rule analysis, set {set_number}\n\n")
        for model, rows in model_results.items():
            report.write(f"Summary: {model}\n")
            verdicts = Counter(row["result"]["verdict"] for row in rows)
            report.write("Verdicts: " + ", ".join(f"{key}={verdicts[key]}" for key in
                         ("PASS", "SYNTAX_ERROR", "MISSED_SHOWN", "TOO_NARROW", "NOISY")) + "\n")
            flags = Counter()
            for row in rows:
                for flag in FLAGS:
                    if has_flag(row["result"], flag):
                        flags[flag] += 1
            report.write("Flags: " + ", ".join(f"{key}={flags[key]}" for key in FLAGS) + "\n\n")
        for model, rows in model_results.items():
            for row in rows:
                result = row["result"]
                if result["verdict"] == "PASS":
                    continue
                report.write(f"{model} {row['technique']} {result['verdict']}\n")
                if result["error"]:
                    report.write(f"Error: {result['error']}\n")
                report.write(f"Shown line: {result['shown']}\n")
                if set_number == 2:
                    report.write(f"Hidden variant: {result['variant']}\n")
                report.write("Detection:\n")
                report.write(yaml.safe_dump(result["detection"], sort_keys=False).rstrip() + "\n\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=int, choices=(1, 2), required=True)
    parser.add_argument("--models", nargs="+", required=True)
    args = parser.parse_args()
    csv_path = "results/techniques.csv" if args.set == 1 else "results/techniques_set2.csv"
    with open(csv_path, encoding="utf-8", newline="") as source:
        import csv
        techniques = [row["technique"] for row in csv.DictReader(source)]
    all_results = {}
    for model in args.models:
        rows = []
        folder = os.path.join("results", "model_outputs", safe(model))
        for technique in techniques:
            path = os.path.join(folder, technique + ".yml")
            if not os.path.exists(path):
                print(f"{model:24} {technique:10} missing, skipping")
                continue
            try:
                with open(path, encoding="utf-8") as saved_rule:
                    rule = saved_rule.read()
                result = analyze_rule(rule, technique, args.set)
            except Exception as error:
                print(f"{model:24} {technique:10} ERROR {error}")
                continue
            rows.append({"model": model, "technique": technique, "result": result})
            print(f"{model:24} {technique:10} {result['verdict']:14} {format_flags(result)}")
        all_results[model] = rows
    print("\nSUMMARY TABLES")
    print_summary(all_results, args.set)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    report_path = f"results/analysis_set{args.set}_{stamp}.md"
    write_report(report_path, all_results, args.set)
    print(f"REPORT {report_path}")


if __name__ == "__main__":
    main()