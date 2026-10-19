"""
Compare LLMs on the 12 techniques using our pass/fail gate.

Usage (from repo root):
    python llm/compare_models.py mistral:7b qwen2.5-coder:7b qwen2.5-coder:14b mistral-rules
Optional:
    --url http://localhost:11434   (Ollama address)
"""
import csv, os, re, sys, json, time, argparse, urllib.request

sys.path.insert(0, "validator")
sys.path.insert(0, "generator")
from runner import rule_to_sql, rule_matches
from generate import TECHNIQUES, make_pair

# What a CTI report would tell us about each technique (plain words).
DESCRIPTIONS = {
    "T1059.001": "PowerShell is used to download a script from a web address and run it.",
    "T1218.011": "rundll32 is made to run code from a file with a .sys extension.",
    "T1218.005": "mshta runs inline JavaScript instead of opening a normal .hta file.",
    "T1218.010": "regsvr32 loads a remote script from an IP address over HTTP.",
    "T1105":     "certutil is used to download a file from the internet.",
    "T1053.005": "A scheduled task is created that runs a program from a Temp folder.",
    "T1547.001": "A program is added to the Run registry key so it starts at every logon.",
    "T1136.001": "A new local user account is created from the command line.",
    "T1003.001": "A tool is used to dump the memory of the lsass process to a file.",
    "T1197":     "bitsadmin is used to download a DLL file from a remote server.",
    "T1047":     "WMIC is used to start a new process.",
    "T1033":     "whoami is used to list the privileges of the current user.",
}

INSTRUCTIONS = """You write Sigma detection rules for Windows process creation logs.
Rules:
- Output ONLY the Sigma rule as YAML. No explanation.
- Use only these fields: Image, CommandLine, ParentImage, ParentCommandLine, OriginalFileName.
- Use modifiers like |contains, |endswith, |contains|all.
- Required keys: title, status, logsource (category: process_creation, product: windows), detection (with condition), level, tags.
- The rule must catch the attacker activity but NOT normal harmless use of the same program.
"""

# Two examples on techniques that are NOT in our test set.
EXAMPLES = """
Example 1
Technique: T1016
Activity: ipconfig is used to list network settings.
Process: C:\\Windows\\System32\\ipconfig.exe
Observed command line: ipconfig.exe /all
Rule:
title: Network Configuration Discovery With Ipconfig
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\ipconfig.exe'
        CommandLine|contains: ' /all'
    condition: selection
level: low
tags:
    - attack.discovery
    - attack.t1016

Example 2
Technique: T1564.001
Activity: attrib is used to hide a file.
Process: C:\\Windows\\System32\\attrib.exe
Observed command line: attrib.exe +h C:\\Users\\student\\secret.exe
Rule:
title: File Hidden With Attrib
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\attrib.exe'
        CommandLine|contains: ' +h '
    condition: selection
level: medium
tags:
    - attack.defense-evasion
    - attack.t1564.001
"""

def build_prompt(tech):
    t = TECHNIQUES[tech]
    return (INSTRUCTIONS + EXAMPLES +
            f"\nNow your turn.\nTechnique: {tech}\nActivity: {DESCRIPTIONS[tech]}\n"
            f"Process: {t['image']}\nObserved command line: {t['malicious']}\nRule:\n")

def ask_ollama(url, model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "num_ctx": 4096, "num_predict": 800}}).encode()
    req = urllib.request.Request(url + "/api/generate", body, {"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.loads(r.read())
    secs = time.time() - t0
    toks = d.get("eval_count", 0)
    tps = toks / (d["eval_duration"] / 1e9) if d.get("eval_duration") else 0
    return d.get("response", ""), secs, tps

def extract_yaml(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)   # reasoning models
    m = re.search(r"```(?:yaml|yml)?\s*\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    i = text.find("title:")
    if i >= 0:
        text = text[i:]
    return text.split("```")[0].strip()

def evaluate(rule_text, tech):
    """Returns dict of three yes/no results and an error text."""
    out = dict(syntax=False, caught=False, quiet=False, error="")
    try:
        rule_to_sql(rule_text)
        out["syntax"] = True
    except Exception as e:
        out["error"] = str(e)[:150]
        return out
    mal, ben = make_pair(tech)
    out["caught"] = rule_matches(rule_text, mal)
    out["quiet"] = not rule_matches(rule_text, ben)
    return out

def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--url", default="http://localhost:11434")
    a = ap.parse_args()

    os.makedirs("results", exist_ok=True)
    rows = []
    for model in a.models:
        os.makedirs(f"results/model_outputs/{safe(model)}", exist_ok=True)
        for tech in TECHNIQUES:
            prompt = build_prompt(tech)
            raw, secs, tps = ask_ollama(a.url, model, prompt)
            rule = extract_yaml(raw)
            first = evaluate(rule, tech)
            final, repaired = first, False
            if not first["syntax"]:                       # one repair try
                fix = prompt + rule + f"\n\nThis rule failed with: {first['error']}\nWrite the corrected rule. Output ONLY the YAML.\nRule:\n"
                raw2, s2, _ = ask_ollama(a.url, model, fix)
                rule2 = extract_yaml(raw2)
                final, repaired, secs = evaluate(rule2, tech), True, secs + s2
                if final["syntax"]:
                    rule = rule2
            open(f"results/model_outputs/{safe(model)}/{tech}.yml", "w", encoding="utf-8").write(rule)
            rows.append(dict(model=model, technique=tech,
                             syntax=first["syntax"], caught=first["caught"], quiet=first["quiet"],
                             full_pass=first["syntax"] and first["caught"] and first["quiet"],
                             pass_after_repair=final["syntax"] and final["caught"] and final["quiet"],
                             seconds=round(secs, 1), tokens_per_sec=round(tps, 1), error=first["error"]))
            r = rows[-1]
            print(f"{model:24} {tech:10} syntax={r['syntax']!s:5} caught={r['caught']!s:5} quiet={r['quiet']!s:5} {r['seconds']}s")

    with open(f"results/model_comparison_{time.strftime('%Y%m%d_%H%M')}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    print("\nSUMMARY (first try, out of 12)")
    print(f"{'model':26}{'syntax':>8}{'caught':>8}{'quiet':>8}{'PASS':>7}{'PASS+fix':>10}{'sec/rule':>10}{'tok/s':>8}")
    for model in a.models:
        m = [r for r in rows if r["model"] == model]
        n = len(m)
        print(f"{model:26}{sum(r['syntax'] for r in m):>8}{sum(r['caught'] for r in m):>8}"
              f"{sum(r['quiet'] for r in m):>8}{sum(r['full_pass'] for r in m):>7}"
              f"{sum(r['pass_after_repair'] for r in m):>10}"
              f"{sum(r['seconds'] for r in m)/n:>10.1f}{sum(r['tokens_per_sec'] for r in m)/n:>8.1f}")

if __name__ == "__main__":
    main()