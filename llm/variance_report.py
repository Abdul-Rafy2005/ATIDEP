"""Build the set 1 prompt variance table from completed run CSV files."""
import csv
import os
import sys


TECHNIQUES = [
    "T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105",
    "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197",
    "T1047", "T1033",
]


def read_rows(path):
    with open(os.path.join(path, "results.csv"), encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def values(rows, model):
    selected = [row for row in rows if row["model"] == model]
    counts = []
    for tech in TECHNIQUES:
        counts.append(sum(row["strict_pass"] == "True" for row in selected if row["technique"] == tech))
    return {
        "single": sum(row["single_pass"] == "True" for row in selected),
        "strict": sum(row["strict_pass"] == "True" for row in selected),
        "syntax": sum(row["single_syntax"] == "False" for row in selected),
        "counts": counts,
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python llm/variance_report.py <v1-run> <v2-run>")
    v1_path, v2_path = sys.argv[1:]
    old_v2 = read_rows("results/runs/20261021_1511_set1_v2")
    rows = []
    for model in ("qwen2.5-coder:7b", "qwen2.5-coder:14b"):
        rows.append((model, "v1 temp0.2", values(read_rows(v1_path), model)))
        rows.append((model, "v2 temp0.2", values(read_rows(v2_path), model)))
        rows.append((model, "v2 temp0", values(old_v2, model)))
    path = "results/variance_set1_v1_vs_v2.md"
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    with open(path, "w", encoding="utf-8") as output:
        headers = " | ".join(TECHNIQUES)
        output.write("# Set 1 run-to-run variance\n\n")
        output.write("| Model | Prompt/run | Single pass | Strict pass | Syntax errors | " + headers + " |\n")
        output.write("| --- | --- | ---: | ---: | ---: | " + " | ".join("---:" for _ in TECHNIQUES) + " |\n")
        for model, prompt, value in rows:
            output.write(f"| {model} | {prompt} | {value['single']}/36 | {value['strict']}/36 | "
                         f"{value['syntax']}/36 | " + " | ".join(str(count) for count in value["counts"]) + " |\n")
    print(f"SAVED {path}")
    for model, prompt, value in rows:
        print(model, prompt, value["single"], value["strict"], value["syntax"], value["counts"])


if __name__ == "__main__":
    main()