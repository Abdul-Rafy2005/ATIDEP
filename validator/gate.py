import csv, sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
from runner import rule_to_sql, rule_matches
from generate import make_pair

def check_rule(rule_text, technique):
    """Returns (status, detail). status is PASS or FAIL."""
    try:
        rule_to_sql(rule_text)                      # 1. syntax check
    except Exception as e:
        return "FAIL", f"syntax error: {str(e)[:60]}"
    mal, ben = make_pair(technique)
    caught = rule_matches(rule_text, mal)           # 2. must fire on attack
    noisy = rule_matches(rule_text, ben)            # 3. must stay quiet on normal use
    if not caught:
        return "FAIL", "missed the malicious log"
    if noisy:
        return "FAIL", "fired on the benign log"
    return "PASS", "caught malicious, quiet on benign"

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    rows = []
    for r in csv.DictReader(open("results/techniques.csv")):
        text = open(f"data/sigmahq_rules/{r['rule_file']}", encoding="utf-8").read()
        status, detail = check_rule(text, r["technique"])
        rows.append([r["technique"], r["rule_file"], status, detail])
        print(f"{r['technique']:10} {status:5} {detail}")
    with open("results/validation_results.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["technique", "rule_file", "status", "detail"]); w.writerows(rows)
    print("passed", sum(1 for x in rows if x[2] == "PASS"), "of", len(rows))