"""
End-to-end ATIDEP demonstration pipeline.

Usage:
    python demo/demo.py --file demo/samples/sample1.txt
    python demo/demo.py --text "Synthetic example, not real intelligence..."
"""
import argparse
import datetime
import importlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import yaml

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "validator"))
sys.path.insert(0, os.path.join(ROOT, "generator"))
sys.path.insert(0, os.path.join(ROOT, "llm"))

from runner import rule_to_sql, rule_matches
from generate import TECHNIQUES, build_event
from techniques_set2 import TECHNIQUES2
from compare_models import DESCRIPTIONS, extract_yaml
from techniques_set2 import DESCRIPTIONS2


# ---------------------------------------------------------------------------
# Supported techniques and metadata
# ---------------------------------------------------------------------------

def load_supported_techniques():
    """Load the 24 supported techniques of sets 1 and 2 with descriptions and templates."""
    all_techs = {}
    for tech_id, d in TECHNIQUES.items():
        all_techs[tech_id] = {
            "set": 1,
            "description": DESCRIPTIONS[tech_id],
            "image": d["image"],
            "malicious": d["malicious"],
            "variant": d["variant"],
            "variant_image": d.get("variant_image", d["image"]),
            "benign": d["benign"],
        }
    for tech_id, d in TECHNIQUES2.items():
        all_techs[tech_id] = {
            "set": 2,
            "description": DESCRIPTIONS2[tech_id],
            "image": d["image"],
            "malicious": d["malicious"],
            "variant": d["variant"],
            "variant_image": d.get("variant_image", d["image"]),
            "benign": d["benign"],
        }
    return all_techs


# ---------------------------------------------------------------------------
# Read configuration from FROZEN.md
# ---------------------------------------------------------------------------

def read_frozen_config(frozen_path=None):
    """Read primary model and its chosen prompt from FROZEN.md."""
    if frozen_path is None:
        frozen_path = os.path.join(ROOT, "FROZEN.md")
    if not os.path.exists(frozen_path):
        raise FileNotFoundError(f"FROZEN.md not found at {frozen_path}")

    with open(frozen_path, "r", encoding="utf-8") as f:
        content = f.read()

    model_match = re.search(r"Primary model:\s*([^\r\n]+)", content)
    prompt_match = re.search(r"Primary model:[^\n]*\n\s*-\s*Chosen prompt:\s*([^\r\n]+)", content)

    if not model_match or not prompt_match:
        raise ValueError("Could not extract primary model and chosen prompt from FROZEN.md")

    model = model_match.group(1).strip()
    prompt_version = prompt_match.group(1).strip()

    # Optional runtime parameters
    seed_match = re.search(r"Seed option and value:\s*--seed\s*(\d+)", content)
    temp_match = re.search(r"Temperature:\s*([0-9.]+)", content)
    ctx_match = re.search(r"num_ctx:\s*(\d+)", content)
    max_match = re.search(r"max_tokens:\s*(\d+)", content)

    return {
        "model": model,
        "prompt_version": prompt_version,
        "seed": int(seed_match.group(1)) if seed_match else 100,
        "temperature": float(temp_match.group(1)) if temp_match else 0.2,
        "num_ctx": int(ctx_match.group(1)) if ctx_match else 4096,
        "max_tokens": int(max_match.group(1)) if max_match else 800,
    }


# ---------------------------------------------------------------------------
# Ollama communication
# ---------------------------------------------------------------------------

def call_ollama(url, model, prompt, temperature=0.2, seed=100, num_ctx=4096, max_tokens=800):
    """Send prompt to Ollama and return (response_text, duration_seconds)."""
    options = {
        "temperature": temperature,
        "num_ctx": num_ctx,
        "num_predict": max_tokens,
    }
    if seed is not None:
        options["seed"] = seed

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url.rstrip("/") + "/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))
    duration = time.time() - t0
    return data.get("response", ""), duration


# ---------------------------------------------------------------------------
# Step 1: Technique & Command Line Extraction
# ---------------------------------------------------------------------------

def build_extraction_prompt(text, supported_techs):
    """Build prompt asking model to pick technique and extract attack command line."""
    lines = [
        "You are a threat detection engineer.",
        "First, read this incident report:",
        f'"""\n{text.strip()}\n"""',
        "\nWhich of the following 24 supported MITRE ATT&CK techniques matches the attacker activity in the report above?",
    ]
    for tech_id in sorted(supported_techs.keys()):
        prog = supported_techs[tech_id]["image"].split("\\")[-1]
        lines.append(f"- {tech_id} ({prog}): {supported_techs[tech_id]['description']}")

    lines.append("\nInstructions:")
    lines.append("Compare the program name and attacker action in the report with the list above.")
    lines.append('Output ONLY a JSON object: {"technique": "<TECHNIQUE_ID>", "command_line": "<EXACT_COMMAND_LINE>"}')
    lines.append('If none of the 24 techniques match, output: {"technique": "UNKNOWN", "command_line": ""}')
    return "\n".join(lines)


def parse_extraction_json(response_text):
    """Safely extract JSON object from model response."""
    # Strip markdown code blocks if any
    cleaned = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL)
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL)
    if m:
        cleaned = m.group(1).strip()
    # Try finding the first { and matching }
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = cleaned[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Step 3: Gate Evaluation
# ---------------------------------------------------------------------------

def evaluate_gate(rule_text, tech_id, extracted_cmd, tech_info):
    """
    Syntax check, then strict gate:
    fires on extracted line AND technique's hidden variant, quiet on benign line.
    Returns (status, reason, parsed_sql) where status is PASS or FAIL.
    """
    try:
        sql = rule_to_sql(rule_text)
    except Exception as e:
        return "FAIL", f"Syntax error: {str(e)[:150]}", ""

    # Build events
    extracted_event = build_event(tech_info["image"], extracted_cmd)
    variant_event = build_event(tech_info["variant_image"], tech_info["variant"])
    benign_event = build_event(tech_info["image"], tech_info["benign"])

    hit_extracted = rule_matches(rule_text, extracted_event)
    hit_variant = rule_matches(rule_text, variant_event)
    hit_benign = rule_matches(rule_text, benign_event)

    if not hit_extracted:
        return "FAIL", "Missed extracted command line", sql
    if not hit_variant:
        return "FAIL", "Too narrow: caught extracted line but missed hidden variant", sql
    if hit_benign:
        return "FAIL", "Noisy: fired on harmless benign line", sql

    return "PASS", "Caught extracted attack and hidden variant, quiet on benign line", sql


# ---------------------------------------------------------------------------
# Main Demo Pipeline
# ---------------------------------------------------------------------------

def run_demo(input_text, url="http://localhost:11434", frozen_path=None, output_dir=None):
    """Run the 4-step pipeline on input_text."""
    if output_dir is None:
        output_dir = os.path.join(ROOT, "demo", "output")
    os.makedirs(output_dir, exist_ok=True)

    supported_techs = load_supported_techniques()
    config = read_frozen_config(frozen_path)
    model = config["model"]
    prompt_version = config["prompt_version"]

    print("================================================================================")
    print("ATIDEP End-to-End Demo")
    print(f"Model: {model} | Prompt: {prompt_version} | Seed: {config['seed']} | Temp: {config['temperature']}")
    print("================================================================================")

    # -----------------------------------------------------------------------
    # Step 1: TECHNIQUE
    # -----------------------------------------------------------------------
    t_start = time.time()
    print("\n[STEP 1: TECHNIQUE] Asking model to identify technique and extract command line...")
    extract_prompt = build_extraction_prompt(input_text, supported_techs)

    try:
        raw_extract_resp, dur_step1 = call_ollama(
            url=url,
            model=model,
            prompt=extract_prompt,
            temperature=0.0,
            seed=config["seed"],
            num_ctx=config["num_ctx"],
            max_tokens=250,
        )
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        sys.exit(1)

    parsed_json = parse_extraction_json(raw_extract_resp)
    tech = parsed_json.get("technique", "").strip()
    cmd = parsed_json.get("command_line", "").strip()

    # Validation criteria:
    # 1. technique is in the supported list (24 techniques)
    # 2. command_line appears in the text (case-insensitive)
    # Note: in JSON deserialization, backslashes may be unescaped (e.g. \\\\ becomes \\ or \),
    # so we also check normalized backslashes or find exact matching text line.
    cmd_in_text = False
    if cmd:
        if cmd.lower() in input_text.lower():
            cmd_in_text = True
        else:
            # Check normalized backslashes
            norm_cmd = re.sub(r"\\+", r"\\", cmd.lower())
            norm_text = re.sub(r"\\+", r"\\", input_text.lower())
            if norm_cmd in norm_text:
                cmd_in_text = True
                # Recover exact substring from input_text if possible
                for line in input_text.splitlines():
                    if re.sub(r"\\+", r"\\", line.strip().lower()) == norm_cmd:
                        cmd = line.strip()
                        break

    is_supported = tech in supported_techs

    step1_time = time.time() - t_start
    print(f"Time: {step1_time:.2f}s")
    print(f"Identified technique: {tech}")
    print(f"Extracted command line: {cmd}")

    if not is_supported or not cmd_in_text:
        print("\nResult: no supported technique found")
        sys.exit(2)

    tech_info = supported_techs[tech]
    print(f"Technique description: {tech_info['description']}")
    print(f"Template executable: {tech_info['image']}")

    # -----------------------------------------------------------------------
    # Step 2: RULE
    # -----------------------------------------------------------------------
    t_start = time.time()
    print("\n[STEP 2: RULE] Building rule prompt with frozen module and calling Ollama...")
    prompt_module = importlib.import_module(f"llm.prompts.{prompt_version}")

    rule_prompt = (
        prompt_module.INSTRUCTIONS + prompt_module.EXAMPLES +
        f"\nNow your turn.\nTechnique: {tech}\nActivity: {tech_info['description']}\n"
        f"Process: {tech_info['image']}\nObserved command line: {cmd}\nRule:\n"
    )

    try:
        raw_rule_resp, dur_step2 = call_ollama(
            url=url,
            model=model,
            prompt=rule_prompt,
            temperature=config["temperature"],
            seed=config["seed"],
            num_ctx=config["num_ctx"],
            max_tokens=config["max_tokens"],
        )
    except Exception as e:
        print(f"Error generating rule with Ollama: {e}")
        sys.exit(1)

    rule_yaml = extract_yaml(raw_rule_resp)
    step2_time = time.time() - t_start
    print(f"Time: {step2_time:.2f}s")
    print("Generated Sigma Rule:")
    print("--------------------------------------------------------------------------------")
    print(rule_yaml)
    print("--------------------------------------------------------------------------------")

    # -----------------------------------------------------------------------
    # Step 3: GATE
    # -----------------------------------------------------------------------
    t_start = time.time()
    print("\n[STEP 3: GATE] Running syntax verification and strict validation gate...")
    verdict, reason, sql = evaluate_gate(rule_yaml, tech, cmd, tech_info)
    step3_time = time.time() - t_start
    print(f"Time: {step3_time:.2f}s")
    print(f"Verdict: {verdict}")
    print(f"Reason:  {reason}")

    # -----------------------------------------------------------------------
    # Step 4: SAVE OUTPUT
    # -----------------------------------------------------------------------
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"{timestamp}.json")
    yml_path = os.path.join(output_dir, f"{timestamp}.yml")

    result_data = {
        "timestamp": timestamp,
        "input_text": input_text,
        "model": model,
        "prompt_version": prompt_version,
        "technique": tech,
        "extracted_command_line": cmd,
        "process_image": tech_info["image"],
        "gate_verdict": verdict,
        "gate_reason": reason,
        "rule_yaml": rule_yaml,
        "timings": {
            "step1_technique_seconds": round(step1_time, 2),
            "step2_rule_seconds": round(step2_time, 2),
            "step3_gate_seconds": round(step3_time, 2),
            "total_seconds": round(step1_time + step2_time + step3_time, 2),
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    with open(yml_path, "w", encoding="utf-8") as f:
        f.write(rule_yaml + "\n")

    print(f"\n[STEP 4: SAVE] Outputs saved:")
    print(f"  JSON: {json_path}")
    print(f"  YAML: {yml_path}")
    print("================================================================================")

    return result_data


def main():
    parser = argparse.ArgumentParser(description="ATIDEP End-to-End Demo")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to text sample file")
    group.add_argument("--text", help="Raw input text to analyze")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama service URL")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: input file {args.file} not found.")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            input_text = f.read()
    else:
        input_text = args.text

    run_demo(input_text, url=args.url)


if __name__ == "__main__":
    main()
