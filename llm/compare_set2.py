"""
Run the model comparison on TEST SET 2 (12 new techniques).
The gate here is stricter: a rule must catch the attack line shown to the model
AND a hidden variant of the same attack, and stay quiet on a harmless use.

Usage (from repo root):
    python llm/compare_set2.py qwen2.5-coder:7b qwen2.5-coder:14b
"""
import os, sys, time, shutil

sys.path.insert(0, "validator"); sys.path.insert(0, "generator"); sys.path.insert(0, "llm")
import compare_models as cm
from runner import rule_to_sql, rule_matches
from techniques_set2 import TECHNIQUES2, DESCRIPTIONS2, make_triple

def evaluate2(rule_text, tech):
    out = dict(syntax=False, caught=False, quiet=False, error="")
    try:
        rule_to_sql(rule_text)
        out["syntax"] = True
    except Exception as e:
        out["error"] = str(e)[:150]
        return out
    mal, var, ben = make_triple(tech)
    hit_shown = rule_matches(rule_text, mal)
    hit_variant = rule_matches(rule_text, var)
    out["caught"] = hit_shown and hit_variant
    out["quiet"] = not rule_matches(rule_text, ben)
    if hit_shown and not hit_variant:
        out["error"] = "too narrow: caught the shown attack but missed the hidden variant"
    elif not hit_shown:
        out["error"] = "missed the shown attack"
    return out

# Point the comparison script at set 2
cm.TECHNIQUES = TECHNIQUES2
cm.DESCRIPTIONS = DESCRIPTIONS2
cm.evaluate = evaluate2

if __name__ == "__main__":
    cm.main()
    src = "results/model_comparison.csv"
    if os.path.exists(src):
        dst = "results/set2_comparison_" + time.strftime("%Y%m%d_%H%M") + ".csv"
        shutil.copy(src, dst)
        print("\nSaved a copy as", dst)