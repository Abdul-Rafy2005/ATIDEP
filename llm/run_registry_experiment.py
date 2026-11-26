"""Run the registry logsource experiment.

Usage:
    python llm/run_registry_experiment.py --models qwen2.5-coder:14b qwen2.5-coder:7b
"""
import argparse
import csv
import datetime
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))

from runner import rule_to_sql, rule_matches
from techniques_registry import TECHNIQUES_REGISTRY, DESCRIPTIONS_REGISTRY
from techniques_file_create import TECHNIQUES_FILE, DESCRIPTIONS_FILE
from techniques_network import TECHNIQUES_NETWORK, DESCRIPTIONS_NETWORK
from compare_models import extract_yaml, safe
from scoring import score_rule
from prompts import registry_v1, registry_v2, file_v1, network_v1

PROMPT_MODULES = {
    "registry_v1": registry_v1, "registry_v2": registry_v2,
    "file_v1": file_v1, "network_v1": network_v1,
}

LOGSOURCE_SETS = {
    "registry": {"techniques": TECHNIQUES_REGISTRY, "descriptions": DESCRIPTIONS_REGISTRY, "category": "registry_set"},
    "file": {"techniques": TECHNIQUES_FILE, "descriptions": DESCRIPTIONS_FILE, "category": "file_event"},
    "network": {"techniques": TECHNIQUES_NETWORK, "descriptions": DESCRIPTIONS_NETWORK, "category": "network_connection"},
}


def tags(url):
    req = urllib.request.Request(url.rstrip("/") + "/api/tags")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("models", [])


def model_record(available, requested):
    for m in available:
        if m.get("name") in (requested, requested + ":latest"):
            return m
    return None


def command_output(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def ask(url, model, prompt, max_tokens, temperature=0, seed=None):
    options = {"temperature": temperature, "num_ctx": 4096, "num_predict": max_tokens}
    if seed is not None:
        options["seed"] = seed
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": options}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", body,
                                {"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read())
    seconds = time.time() - started
    token_count = data.get("eval_count", 0)
    tps = token_count / (data["eval_duration"] / 1e9) if data.get("eval_duration") else 0
    return data.get("response", ""), seconds, tps, data.get("done_reason", ""), token_count


def build_repair_prompt(prompt, rule, error):
    hint = ""
    if "Unsupported type" in error:
        hint = ("\nA list item in your rule is a key and value pair, but every list item must be plain text. "
                "Modifiers belong in the key name, never as a list item. Write the whole rule again.")
    return (prompt + rule + f"\n\nThis rule failed with: {error}{hint}\n"
            "Write the corrected rule. Output ONLY the YAML.\nRule:\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run registry logsource experiment")
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--logsource", choices=list(LOGSOURCE_SETS.keys()), required=True)
    parser.add_argument("--prompt", choices=list(PROMPT_MODULES.keys()), required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=800)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--url", default="http://localhost:11434")
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args(argv)

    available = tags(args.url)
    missing = [m for m in args.models if not model_record(available, m)]
    if missing:
        print("Missing model(s): " + ", ".join(missing))
        return 2

    ls = LOGSOURCE_SETS[args.logsource]
    techniques = ls["techniques"]
    descriptions = ls["descriptions"]
    prompt_module = PROMPT_MODULES[args.prompt]

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    folder = os.path.join(args.results_dir, "runs", f"{run_id}_{args.logsource}_{args.prompt}")
    suffix = 1
    while os.path.exists(folder):
        folder = os.path.join(args.results_dir, "runs", f"{run_id}_{suffix:02d}_{args.logsource}_{args.prompt}")
        suffix += 1
    os.makedirs(folder)
    for subdir in ("rules_first", "rules_final", "rules_raw"):
        for model in args.models:
            os.makedirs(os.path.join(folder, subdir, safe(model)))

    settings = {
        "models": args.models,
        "ollama_version": command_output(["ollama", "--version"]),
        "model_info": {m: model_record(available, m) for m in args.models},
        "prompt": args.prompt,
        "set": args.logsource,
        "logsource": ls["category"],
        "temperature": args.temperature,
        "seed": args.seed,
        "num_ctx": 4096,
        "max_tokens": args.max_tokens,
        "repeats": args.repeats,
        "techniques_count": len(techniques),
        "python": platform.python_version(),
        "gpu": command_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]),
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(folder, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    rows = []
    for model in args.models:
        for tech in techniques:
            prompt = prompt_module.build_prompt(tech, techniques, descriptions)
            for repeat in range(1, args.repeats + 1):
                row_seed = args.seed + repeat - 1 if args.seed is not None else None
                raw, seconds, tps, done_reason, eval_count = ask(
                    args.url, model, prompt, args.max_tokens, args.temperature, row_seed)
                rule_first = extract_yaml(raw)
                score = score_rule(args.logsource, tech, rule_first)
                rule_final = rule_first
                repaired = False
                if not score.syntax_ok:
                    repair_prompt = build_repair_prompt(prompt, rule_first, score.error)
                    raw2, sec2, _, _, _ = ask(
                        args.url, model, repair_prompt, args.max_tokens, args.temperature, row_seed)
                    rule_final = extract_yaml(raw2)
                    seconds += sec2
                    repaired = True

                raw_path = os.path.join(folder, "rules_raw", safe(model), f"{tech}_repeat{repeat}.txt")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(raw)
                first_suffix = f"_repeat{repeat}.yml" if args.repeats > 1 else ".yml"
                first_path = os.path.join(folder, "rules_first", safe(model), tech + first_suffix)
                final_path = os.path.join(folder, "rules_final", safe(model), tech + first_suffix)
                with open(first_path, "w", encoding="utf-8") as f:
                    f.write(rule_first)
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(rule_final)

                final_score = score_rule(args.logsource, tech, rule_final)
                row = {
                    "model": model,
                    "technique": tech,
                    "repeat": repeat,
                    "syntax_ok": score.syntax_ok,
                    "fires_shown": score.fires_shown,
                    "fires_variant": score.fires_variant,
                    "fires_benign": score.fires_benign,
                    "single_pass": score.single_pass,
                    "strict_pass": score.strict_pass,
                    "verdict": score.verdict,
                    "error": score.error,
                    "repaired": repaired,
                    "final_strict_pass": final_score.strict_pass,
                    "final_verdict": final_score.verdict,
                    "seconds": round(seconds, 2),
                    "tokens_per_second": round(tps, 2),
                    "seed": row_seed,
                }
                rows.append(row)
                mark = "PASS" if score.strict_pass else score.verdict
                print(f"{model:24} {tech:20} r={repeat} strict={score.strict_pass!s:5} {mark:12} {seconds:.1f}s")

    csv_fields = list(rows[0].keys())
    with open(os.path.join(folder, "results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        w.writerows(rows)

    # Summary
    with open(os.path.join(folder, "summary.md"), "w", encoding="utf-8") as f:
        f.write(f"# {args.logsource.title()} experiment summary\n\n")
        f.write(f"Prompt: {args.prompt} | Logsource: {ls['category']} | "
                f"Techniques: {len(techniques)} | Temperature: {args.temperature}\n\n")
        f.write("| Model | Strict pass | Single pass | Syntax errors | Verdicts |\n")
        f.write("| --- | ---: | ---: | ---: | --- |\n")
        for model in dict.fromkeys(r["model"] for r in rows):
            sel = [r for r in rows if r["model"] == model]
            verdicts = {}
            for r in sel:
                verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
            counts = ", ".join(f"{k}={v}" for k, v in sorted(verdicts.items()))
            syntax_errors = sum(1 for r in sel if not r["syntax_ok"])
            f.write(f"| {model} | {sum(r['strict_pass'] for r in sel)}/{len(sel)} | "
                    f"{sum(r['single_pass'] for r in sel)}/{len(sel)} | "
                    f"{syntax_errors} | {counts} |\n")

    total = len(rows)
    strict = sum(r["strict_pass"] for r in rows)
    single = sum(r["single_pass"] for r in rows)
    print(f"\nRUN_FOLDER {folder}")
    print(f"STRICT_PASS {strict}/{total}")
    print(f"SINGLE_PASS {single}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
