"""ATIDEP Gate Demonstration Tool.

Evaluates a Sigma rule against synthetic logs for a specified technique.

Usage:
    python demo/gate_demo.py --rule demo/sample_rules/<file>.yml --set <1|2|3> --technique <id>
"""
import argparse
import os
import sys

# Ensure repository root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from llm.scoring import (
    score_rule,
    make_triple_set1,
    make_triple_set2,
    make_triple_set3,
)


VERDICT_EXPLANATIONS = {
    "PASS": "The rule has valid syntax, catches both the observed attack line and its hidden variant, and stays quiet on harmless commands.",
    "TOO_NARROW": "The rule catches the attack line it was written from but misses a changed version of the same attack. A check with only one attack log would have approved it.",
    "SYNTAX_ERROR": "The rule contains invalid syntax and could not be converted to SQL by pySigma.",
    "MISSED_SHOWN": "The rule fails to catch even the observed attack command line it was written from.",
    "NOISY": "The rule fires on harmless everyday commands, causing false alarms.",
}


def load_technique_triple(set_num, technique):
    """Load shown, variant, and benign events for technique."""
    if set_num == 1:
        return make_triple_set1(technique)
    elif set_num == 2:
        return make_triple_set2(technique)
    elif set_num == 3:
        return make_triple_set3(technique)
    else:
        raise ValueError(f"Unknown set number: {set_num}")


def run_gate_demo(rule_path, set_num, technique):
    """Score rule against technique logs and display formatted gate checklist."""
    if not os.path.exists(rule_path):
        raise FileNotFoundError(f"Rule file not found: {rule_path}")

    with open(rule_path, "r", encoding="utf-8") as f:
        rule_text = f.read()

    shown, variant, benign = load_technique_triple(set_num, technique)
    res = score_rule(set_num, technique, rule_text)

    print("=" * 80)
    print("ATIDEP Gate Demonstration")
    print(f"Rule: {rule_path} | Set: {set_num} | Technique: {technique}")
    print("=" * 80)
    print()
    print("[RULE TEXT]")
    print("-" * 80)
    print(rule_text.strip())
    print("-" * 80)
    print()
    print("[TEST EVENTS]")
    print(f"  Attack line:    {shown.get('CommandLine', '')}")
    print(f"  Hidden variant: {variant.get('CommandLine', '')}")
    print(f"  Harmless line:  {benign.get('CommandLine', '')}")
    print()
    print("[GATE CHECKLIST]")
    if res.syntax_ok:
        print("  Syntax valid:                yes")
    else:
        err_msg = res.error if res.error else "pySigma conversion failed"
        print(f"  Syntax valid:                no ({err_msg})")

    print(f"  Fires on the attack line:    {'yes' if res.fires_shown else 'no'}")
    print(f"  Fires on the hidden variant: {'yes' if res.fires_variant else 'no'}")
    print(f"  Quiet on the harmless line:  {'yes' if not res.fires_benign else 'no'}")
    print()
    print("[VERDICT]")
    explanation = VERDICT_EXPLANATIONS.get(res.verdict, "No explanation available.")
    print(f"  {res.verdict}: {explanation}")
    print("=" * 80)

    return res


def main():
    parser = argparse.ArgumentParser(description="ATIDEP Gate Demonstration Tool")
    parser.add_argument("--rule", required=True, help="Path to Sigma rule YAML file")
    parser.add_argument("--set", type=int, choices=[1, 2, 3], required=True, help="Set number (1, 2, or 3)")
    parser.add_argument("--technique", required=True, help="Technique ID (e.g. T1615)")
    args = parser.parse_args()

    run_gate_demo(args.rule, args.set, args.technique)


if __name__ == "__main__":
    main()

