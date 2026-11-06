"""Diagnose a saved experiment run without contacting Ollama."""
import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))
from runner import rule_to_sql
from analyze_results import DuplicateKeyLoader, detection_block, detection_values, inspect_yaml
from compare_models import safe
from generate import make_pair

LEAKED_VALUES = ("-all", "\\Users\\Public\\", ".vbs", r"\ipconfig.exe",
                 r"\wscript.exe", r"\cscript.exe")


def syntax_result(rule_text):
    try:
        rule_to_sql(rule_text)
    except Exception as error:
        return False, str(error)
    return True, ""


def raw_detection_block(rule_text):
    lines = rule_text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == "detection:"), None)
    if start is None:
        return "(no detection block)"
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index] and not lines[index][0].isspace():
            end = index
            break
    return "\n".join(lines[start:end])


def modifier_chains(data):
    chains = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key != "condition" and "|" in str(key):
                    parts = str(key).split("|")
                    chains.add((parts[0], tuple(parts[1:])))
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(detection_block(data))
    return chains


def inspect_rule(rule_text):
    syntax_ok, error = syntax_result(rule_text)
    try:
        data, duplicates = inspect_yaml(rule_text)
    except Exception:
        data, duplicates = {}, []
    return {"syntax": syntax_ok, "error": error, "data": data,
            "duplicates": duplicates, "chains": modifier_chains(data)}


def format_chain(chain):
    return "|".join(chain) if chain else "(none)"


def strict_pass(rule_text, tech):
    from analyze_results import analyze_rule
    try:
        return analyze_rule(rule_text, tech, 1)["verdict"] == "PASS"
    except Exception:
        return False


def techniques():
    with open("results/techniques.csv", encoding="utf-8", newline="") as source:
        return [row["technique"] for row in csv.DictReader(source)]


def shape(data):
    values = list(detection_values(detection_block(data)))
    command_parts = [value for field, value in values if field == "CommandLine"]
    image_values = [value for field, value in values if field == "Image"]
    padded = any(value != value.strip() for _, value in values)
    windash = any("windash" in chain for _, chain in modifier_chains(data))
    return len(command_parts), len(command_parts) > 3, padded, windash, len(image_values) > 1


def run_analysis(run_folder):
    with open(os.path.join(run_folder, "settings.json"), encoding="utf-8") as source:
        settings = yaml.safe_load(source)
    techs = techniques()
    records = []
    for model in settings["models"]:
        model_folder = os.path.join(run_folder, "rules_first", safe(model))
        final_folder = os.path.join(run_folder, "rules_final", safe(model))
        for tech in techs:
            first_path = os.path.join(model_folder, tech + ".yml")
            final_path = os.path.join(final_folder, tech + ".yml")
            with open(first_path, encoding="utf-8") as source:
                first_text = source.read()
            with open(final_path, encoding="utf-8") as source:
                final_text = source.read()
            first = inspect_rule(first_text)
            final_syntax, _ = syntax_result(final_text)
            final_pass = strict_pass(final_text, tech)
            shown, _ = make_pair(tech)
            records.append({"model": model, "technique": tech, "first_text": first_text,
                            "final_text": final_text, "first": first,
                            "final_syntax": final_syntax, "final_pass": final_pass,
                            "shown": shown, "shape": shape(first["data"]),
                            "leaks": [value for value in LEAKED_VALUES
                                      if value in first_text and value not in shown["CommandLine"]
                                      and value not in shown["Image"]]})
    return records


def write_report(path, records):
    syntax_errors = [record for record in records if not record["first"]["syntax"]]
    groups = Counter(record["first"]["error"] for record in syntax_errors)
    chains = defaultdict(lambda: {"rules": set(), "converted": 0, "failed": 0})
    for record in records:
        for field, chain in record["first"]["chains"]:
            key = f"{field}|{format_chain(chain)}"
            chains[key]["rules"].add((record["model"], record["technique"]))
            if record["first"]["syntax"]:
                chains[key].setdefault("converted_rules", set()).add((record["model"], record["technique"]))
            else:
                chains[key].setdefault("failed_rules", set()).add((record["model"], record["technique"]))

    shapes = {}
    for model in sorted({record["model"] for record in records}):
        selected = [record for record in records if record["model"] == model]
        shapes[model] = {
            "average": sum(record["shape"][0] for record in selected) / len(selected),
            "more": sum(record["shape"][1] for record in selected),
            "padded": sum(record["shape"][2] for record in selected),
            "windash": sum(record["shape"][3] for record in selected),
            "multi_image": sum(record["shape"][4] for record in selected),
        }

    with open(path, "w", encoding="utf-8") as output:
        output.write("# Run diagnosis\n\n")
        output.write("## A) Syntax errors, first try\n\n")
        for record in syntax_errors:
            output.write(f"{record['model']} {record['technique']}\n")
            output.write(f"Error: {record['first']['error']}\n")
            output.write(f"Final fixed syntax: {'yes' if record['final_syntax'] else 'no'}\n")
            if record["final_syntax"]:
                output.write(f"Final passes strict gate: {'yes' if record['final_pass'] else 'no'}\n")
            output.write("Detection block:\n" + raw_detection_block(record["first_text"]) + "\n\n")
        output.write("## B) Error groups\n\n")
        for error, count in groups.items():
            output.write(f"{count} | {error}\n")
        output.write("\n## C) Modifier chains\n\n")
        output.write("| Chain | Rules used | Converted | Failed | Only failing |\n| --- | ---: | ---: | ---: | --- |\n")
        for key in sorted(chains):
            value = chains[key]
            converted = len(value.get("converted_rules", set()))
            failed = len(value.get("failed_rules", set()))
            output.write(f"| {key} | {len(value['rules'])} | {converted} | {failed} | "
                         f"{'yes' if converted == 0 else 'no'} |\n")
        output.write("\n## D) Example leakage\n\n")
        for record in records:
            if record["leaks"]:
                output.write(f"{record['model']} {record['technique']}: {', '.join(record['leaks'])}\n")
        output.write("\n## E) Shape of the rules\n\n")
        output.write("| Model | Average CommandLine parts | More than 3 | Padded values | Uses windash | More than one Image |\n| --- | ---: | ---: | ---: | ---: | ---: |\n")
        for model, value in shapes.items():
            output.write(f"| {model} | {value['average']:.2f} | {value['more']} | {value['padded']} | "
                         f"{value['windash']} | {value['multi_image']} |\n")
    return syntax_errors, groups, chains


def print_console(syntax_errors, groups, chains):
    print("A) Syntax errors")
    for record in syntax_errors:
        print(f"{record['model']} {record['technique']} final_syntax={record['final_syntax']} final_strict={record['final_pass']}")
    print("B) Error groups")
    for error, count in groups.items():
        print(f"{count} {error}")
    print("C) Modifier chains")
    print("chain                         rules converted failed only_failing")
    for key in sorted(chains):
        value = chains[key]
        converted = len(value.get("converted_rules", set()))
        failed = len(value.get("failed_rules", set()))
        print(f"{key:28} {len(value['rules']):5} {converted:9} {failed:6} "
              f"{'yes' if converted == 0 else 'no'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_folder")
    args = parser.parse_args()
    path = os.path.join(args.run_folder, "diagnosis.md")
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    records = run_analysis(args.run_folder)
    syntax_errors, groups, chains = write_report(path, records)
    print_console(syntax_errors, groups, chains)
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()