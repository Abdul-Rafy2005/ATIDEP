"""
Re-score rule files that compare_models.py already saved. Does NOT call the model.

Usage (from repo root):
    python llm/rescore_saved.py mistral-rules
"""
import os, re, sys

sys.path.insert(0, "validator")
sys.path.insert(0, "generator")
sys.path.insert(0, "llm")
from generate import TECHNIQUES
from compare_models import evaluate, safe

def detection_part(rule_text):
    i = rule_text.find("detection:")
    if i < 0:
        return "(no detection section)"
    block = rule_text[i:]
    j = block.find("\nfalsepositives")
    k = block.find("\nlevel:")
    ends = [x for x in (j, k) if x > 0]
    return block[: min(ends)] if ends else block

def main():
    if len(sys.argv) != 2:
        print("Usage: python llm/rescore_saved.py <model-name>")
        return
    model = sys.argv[1]
    folder = f"results/model_outputs/{safe(model)}"
    if not os.path.isdir(folder):
        print("Folder not found:", folder)
        return

    rows, failures = [], []
    for tech in TECHNIQUES:
        path = f"{folder}/{tech}.yml"
        if not os.path.exists(path):
            print(f"{tech}: no saved file, skipping")
            continue
        rule = open(path, encoding="utf-8").read()
        r = evaluate(rule, tech)
        full = r["syntax"] and r["caught"] and r["quiet"]
        rows.append((tech, r, full))
        why = "PASS" if full else ("syntax error: " + r["error"] if not r["syntax"]
              else "missed the attack" if not r["caught"] else "fired on the harmless log")
        print(f"{tech:10} syntax={r['syntax']!s:5} caught={r['caught']!s:5} quiet={r['quiet']!s:5} {why}")
        if not full:
            failures.append((tech, rule, why))

    n = len(rows)
    print(f"\nSUMMARY for {model} (first try, out of {n})")
    print(f"  syntax valid : {sum(r['syntax'] for _, r, _ in rows)}")
    print(f"  caught attack: {sum(r['caught'] for _, r, _ in rows)}")
    print(f"  quiet benign : {sum(r['quiet'] for _, r, _ in rows)}   (a rule that never fires also counts as quiet)")
    print(f"  FULL PASS    : {sum(f for _, _, f in rows)}")

    if failures:
        print("\n---- WHY THE FAILURES FAILED (compare with the attack line) ----")
        for tech, rule, why in failures:
            print(f"\n[{tech}] {why}")
            print("Attack line we expected it to catch:")
            print("   ", TECHNIQUES[tech]["malicious"])
            print("Harmless line it should ignore:")
            print("   ", TECHNIQUES[tech]["benign"])
            print("What the model wrote:")
            print(detection_part(rule))

if __name__ == "__main__":
    main()