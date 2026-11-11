"""Run a prompt version against saved experiment metadata and dual set 1 gates."""
import argparse
import csv
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))
from runner import rule_matches, rule_to_sql
from generate import TECHNIQUES, make_pair
from techniques_set2 import TECHNIQUES2, DESCRIPTIONS2, make_triple
from techniques_set3 import TECHNIQUES3, DESCRIPTIONS3, make_triple3
from compare_models import ask_ollama, extract_yaml, safe, DESCRIPTIONS
from analyze_results import analyze_rule, format_flags
from scoring import score_rule
from prompts import v1, v2, v2_1, v3a, v3b


def tags(url):
    request = urllib.request.Request(url.rstrip("/") + "/api/tags")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read()).get("models", [])


def model_record(available, requested):
    for model in available:
        if model.get("name") == requested or model.get("name") == requested + ":latest":
            return model
    return None


def command_output(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def prompt_for(version, tech, techniques, descriptions):
    module = {"v1": v1, "v2": v2, "v2_1": v2_1, "v3a": v3a, "v3b": v3b}[version]
    return module.build_prompt(tech, techniques, descriptions)


def ask(url, model, prompt, max_tokens, temperature=0, seed=None):
    options = {"temperature": temperature, "num_ctx": 4096,
               "num_predict": max_tokens}
    if seed is not None:
        options["seed"] = seed
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": options}).encode()
    request = urllib.request.Request(url.rstrip("/") + "/api/generate", body,
                                     {"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(request, timeout=900) as response:
        data = json.loads(response.read())
    seconds = time.time() - started
    token_count = data.get("eval_count", 0)
    tokens_per_second = token_count / (data["eval_duration"] / 1e9) if data.get("eval_duration") else 0
    return (data.get("response", ""), seconds, tokens_per_second,
            data.get("done_reason", ""), token_count)


def build_repair_prompt(prompt, rule, error, repair_hint=False):
    hint = ("\nA list item in your rule is a key and value pair, but every list item must be plain text. "
            "Modifiers such as windash belong in the key name (for example CommandLine|contains|windash|all:), "
            "never as a list item. Write the whole rule again.") if (repair_hint and "Unsupported type" in error) else ""
    return (prompt + rule + f"\n\nThis rule failed with: {error}{hint}\n"
            "Write the corrected rule. Output ONLY the YAML.\nRule:\n")


def single_score(rule_text, tech, set_number):
    sc = score_rule(set_number, tech, rule_text)
    return {"syntax": sc.syntax_ok, "caught": sc.fires_shown, "quiet": not sc.fires_benign,
            "error": sc.error, "pass": sc.single_pass}


def result_row(model, tech, repeat, rule_first, rule_final, seconds, tokens_per_second, set_number, row_seed,
               first_done_reason, first_eval_count, repair_done_reason, repair_eval_count):
    single = single_score(rule_first, tech, set_number)
    strict = analyze_rule(rule_first, tech, set_number)
    score = score_rule(set_number, tech, rule_first)
    return {
        "model": model, "technique": tech, "repeat": repeat,
        "single_pass": score.single_pass, "strict_pass": score.strict_pass,
        "single_syntax": score.syntax_ok, "single_caught": score.fires_shown,
        "single_quiet": not score.fires_benign, "verdict": score.verdict,
        "error": strict["error"], "flags": format_flags(strict),
        "duplicate_keys": bool(strict["duplicate_keys"]),
        "padded_values": strict["padded_values"],
        "seed": row_seed,
        "first_done_reason": first_done_reason,
        "first_eval_count": first_eval_count,
        "repair_done_reason": repair_done_reason,
        "repair_eval_count": repair_eval_count,
        "seconds": round(seconds, 2), "tokens_per_second": round(tokens_per_second, 2),
        "strict_result": strict, "rule_first": rule_first, "rule_final": rule_final,
    }


def write_summary(path, rows):
    with open(path, "w", encoding="utf-8") as output:
        output.write("# Experiment summary\n\n")
        output.write("| Model | Single gate pass | Strict gate pass | Verdict counts | Flags | Seconds/rule |\n")
        output.write("| --- | ---: | ---: | --- | --- | ---: |\n")
        for model in dict.fromkeys(row["model"] for row in rows):
            selected = [row for row in rows if row["model"] == model]
            verdicts = {}
            for row in selected:
                verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
            flag_counts = {}
            for row in selected:
                for flag in ("duplicate_keys", "padded_values", "COPIED"):
                    if flag in row["flags"]:
                        flag_counts[flag] = flag_counts.get(flag, 0) + 1
            counts = ", ".join(f"{key}={value}" for key, value in sorted(verdicts.items()))
            flags = ", ".join(f"{key}={value}" for key, value in sorted(flag_counts.items())) or "none"
            seconds = sum(row["seconds"] for row in selected) / len(selected)
            output.write(f"| {model} | {sum(row['single_pass'] for row in selected)} | "
                         f"{sum(row['strict_pass'] for row in selected)} | {counts} | {flags} | {seconds:.2f} |\n")


def write_report(path, rows):
    with open(path, "w", encoding="utf-8") as output:
        output.write("# Non-PASS first-try rules\n\n")
        for row in rows:
            if row["strict_pass"]:
                continue
            result = row["strict_result"]
            output.write(f"{row['model']} {row['technique']} repeat {row['repeat']}: {row['verdict']}\n")
            if result["error"]:
                output.write(f"Error: {result['error']}\n")
            output.write(f"Shown line: {result['shown']}\n")
            output.write(f"Variant: {result['variant']}\n")
            output.write("Detection:\n")
            output.write(yaml.safe_dump(result["detection"], sort_keys=False).rstrip() + "\n\n")


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--prompt", choices=("v1", "v2", "v2_1", "v3a", "v3b"), required=True)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=800)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--repair-hint", action="store_true")
    parser.add_argument("--url", default="http://localhost:11434")
    parser.add_argument("--allow-validation-set", action="store_true")
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--reason")
    parser.add_argument("--results-dir", default=None, help="Custom results directory (for testing)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if args.set == 2 and (not args.allow_validation_set or not args.reason):
        print("Set 2 is the validation set. Use --allow-validation-set and write down why.")
        return 2
    if args.set == 3:
        frozen_check = False
        if os.path.exists("tools/check_frozen.py"):
            try:
                res = subprocess.run([sys.executable, "tools/check_frozen.py"], capture_output=True)
                frozen_check = (res.returncode == 0)
            except Exception:
                frozen_check = False
        if not (args.final and args.reason and os.path.exists("FROZEN.md") and frozen_check):
            print("Set 3 is the locked final test set. Refusing run unless --final and --reason are given, FROZEN.md exists, and tools/check_frozen.py passes.")
            return 2

    available = tags(args.url)
    missing = [model for model in args.models if not model_record(available, model)]
    if missing:
        print("Missing Ollama model(s): " + ", ".join(missing))
        print("Available models: " + ", ".join(model.get("name", "") for model in available))
        return 2

    if args.set == 1:
        techniques = TECHNIQUES
        descriptions = DESCRIPTIONS
    elif args.set == 2:
        techniques = TECHNIQUES2
        descriptions = DESCRIPTIONS2
    else:
        techniques = TECHNIQUES3
        descriptions = DESCRIPTIONS3
    results_base = args.results_dir if args.results_dir else "results"
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    folder = os.path.join(results_base, "runs", f"{run_id}_set{args.set}_{args.prompt}")
    suffix = 1
    while os.path.exists(folder):
        folder = os.path.join(results_base, "runs", f"{run_id}_{suffix:02d}_set{args.set}_{args.prompt}")
        suffix += 1
    os.makedirs(folder)
    for directory in ("rules_first", "rules_final", "rules_raw"):
        for model in args.models:
            os.makedirs(os.path.join(folder, directory, safe(model)))

    settings = {
        "models": args.models, "ollama_version": command_output(["ollama", "--version"]),
        "model_info": {model: model_record(available, model) for model in args.models},
        "prompt": args.prompt, "set": args.set, "temperature": args.temperature, "seed": args.seed, "num_ctx": 4096,
        "max_tokens": args.max_tokens, "repeats": args.repeats,
        "python": platform.python_version(), "gpu": command_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]),
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(folder, "settings.json"), "w", encoding="utf-8") as output:
        json.dump(settings, output, indent=2)

    rows = []
    for model in args.models:
        for tech in techniques:
            prompt = prompt_for(args.prompt, tech, techniques, descriptions)
            for repeat in range(1, args.repeats + 1):
                row_seed = args.seed + repeat - 1 if args.seed is not None else None
                raw, seconds, tokens_per_second, first_done_reason, first_eval_count = ask(
                    args.url, model, prompt, args.max_tokens, args.temperature, row_seed)
                rule_first = extract_yaml(raw)
                first_score = score_rule(args.set, tech, rule_first)
                rule_final = rule_first
                repaired = False
                repair_done_reason = ""
                repair_eval_count = 0
                if not first_score.syntax_ok:
                    repair_prompt = build_repair_prompt(prompt, rule_first, first_score.error, args.repair_hint)
                    raw_final, repair_seconds, _, repair_done_reason, repair_eval_count = ask(
                        args.url, model, repair_prompt, args.max_tokens, args.temperature, row_seed)
                    rule_final = extract_yaml(raw_final)
                    seconds += repair_seconds
                    repaired = True
                raw_filename = f"{tech}_repeat{repeat}.txt"
                raw_path = os.path.join(folder, "rules_raw", safe(model), raw_filename)
                with open(raw_path, "w", encoding="utf-8") as output:
                    output.write(raw)
                first_path = os.path.join(folder, "rules_first", safe(model), tech + ".yml")
                final_path = os.path.join(folder, "rules_final", safe(model), tech + ".yml")
                if args.repeats > 1:
                    first_path = first_path.replace(".yml", f"_repeat{repeat}.yml")
                    final_path = final_path.replace(".yml", f"_repeat{repeat}.yml")
                with open(first_path, "w", encoding="utf-8") as output:
                    output.write(rule_first)
                with open(final_path, "w", encoding="utf-8") as output:
                    output.write(rule_final)
                row = result_row(model, tech, repeat, rule_first, rule_final, seconds, tokens_per_second,
                                args.set, row_seed, first_done_reason, first_eval_count,
                                repair_done_reason, repair_eval_count)
                row["repaired"] = repaired
                rows.append(row)
                print(f"{model:24} {tech:10} repeat={repeat} single={row['single_pass']!s:5} strict={row['strict_pass']!s:5} {row['seconds']}s")

    csv_fields = [key for key, value in rows[0].items() if key not in ("strict_result", "rule_first", "rule_final")]
    with open(os.path.join(folder, "results.csv"), "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in csv_fields} for row in rows)
    write_summary(os.path.join(folder, "summary.md"), rows)
    write_report(os.path.join(folder, "report.md"), rows)

    os.makedirs(results_base, exist_ok=True)
    with open(os.path.join(results_base, "run_log.csv"), "a", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        if output.tell() == 0:
            writer.writerow(["run_id", "date", "set", "prompt", "models"])
        writer.writerow([os.path.basename(folder), settings["date"], args.set, args.prompt, ";".join(args.models)])
    if args.set == 2:
        with open(os.path.join(results_base, "set2_use_log.csv"), "a", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            if output.tell() == 0:
                writer.writerow(["date", "models", "prompt", "reason"])
            writer.writerow([settings["date"], ";".join(args.models), args.prompt, args.reason])
    if args.set == 3:
        with open(os.path.join(results_base, "set3_use_log.csv"), "a", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            if output.tell() == 0:
                writer.writerow(["date", "models", "prompt", "reason"])
            writer.writerow([settings["date"], ";".join(args.models), args.prompt, args.reason])
    print(f"RUN_FOLDER {folder}")
    print(f"SINGLE_PASS {sum(row['single_pass'] for row in rows)} of {len(rows)}")
    print(f"STRICT_PASS {sum(row['strict_pass'] for row in rows)} of {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())