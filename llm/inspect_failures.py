"""Print exact qwen 14b v2 syntax failures from saved runs."""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
from runner import rule_to_sql


TECHNIQUES = [
    "T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105",
    "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197",
    "T1047", "T1033",
]


def syntax_error(text):
    try:
        rule_to_sql(text)
    except Exception as error:
        return str(error)
    return ""


def numbered(text):
    return "\n".join(f"{index:4}: {line}" for index, line in enumerate(text.splitlines(), 1))


def cause(text, error):
    if "Unsupported type: <class 'dict'>" in error:
        for line in text.splitlines():
            if line.lstrip().startswith("-") and ": " in line:
                return "nested mapping where a list was expected"
    if "expected <block end>" in error and "found ':'" in error:
        return "value contains a colon followed by a space"
    if "found '<scalar>'" in error or "found ','" in error:
        return "quote problem inside a value"
    if "while scanning" in error and "character" in error:
        return "value starts with a special YAML character"
    if "could not find expected" in error or "unexpected end" in error:
        return "output cut off"
    return "unclear"


def inspect(run_folder, model_folder):
    first_folder = os.path.join(run_folder, "rules_first", model_folder)
    final_folder = os.path.join(run_folder, "rules_final", model_folder)
    records = []
    for name in TECHNIQUES:
        first_files = [name + ".yml"] + [name + f"_repeat{index}.yml" for index in range(1, 4)]
        for filename in first_files:
            first_path = os.path.join(first_folder, filename)
            if not os.path.exists(first_path):
                continue
            final_path = os.path.join(final_folder, filename)
            with open(first_path, encoding="utf-8") as source:
                first = source.read()
            with open(final_path, encoding="utf-8") as source:
                final = source.read()
            first_error = syntax_error(first)
            final_error = syntax_error(final)
            if first_error and final_error:
                records.append((name, filename, first, first_error, final, cause(first, first_error)))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+")
    args = parser.parse_args()
    counts = Counter()
    for run in args.runs:
        records = inspect(run, "qwen2.5-coder_14b")
        print(f"RUN {run}")
        for tech, filename, first, error, final, why in records:
            print(f"\n{tech} repeat={filename} cause={why}")
            print("Exception:")
            print(error)
            print("First-try YAML:")
            print(numbered(first))
            print("Repair YAML:")
            print(final)
            counts[why] += 1
        if not records:
            print("No final syntax failures.")
    print("\nCAUSE COUNTS")
    for key, value in counts.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()