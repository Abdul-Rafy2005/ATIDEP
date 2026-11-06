import csv
import sys

sys.path.insert(0, "validator")
sys.path.insert(0, "generator")
from runner import rule_matches, rule_to_sql
from techniques_set3 import make_triple3

bad = 0
for row in csv.DictReader(open("results/techniques_set3.csv", encoding="utf-8")):
    rule = open(f"data/sigmahq_rules_set3/{row['rule_file']}", encoding="utf-8").read()
    mal, var, ben = make_triple3(row["technique"])
    try:
        a = rule_matches(rule, mal)
        b = rule_matches(rule, var)
        c = rule_matches(rule, ben)
    except Exception as e:
        print(f"{row['technique']:12} ERROR {str(e)[:70]}")
        bad += 1
        continue
    ok = a and b and not c
    bad += not ok
    print(
        f"{row['technique']:12} attack={a!s:5} variant={b!s:5} harmless_fires={c!s:5} {'OK' if ok else '<-- CHECK THIS LOG'}"
    )
print("all good" if bad == 0 else f"{bad} need fixing")
if bad != 0:
    sys.exit(1)

