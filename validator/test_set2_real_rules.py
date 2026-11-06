import csv, sys
sys.path.insert(0, "validator"); sys.path.insert(0, "generator")
from runner import rule_to_sql, rule_matches
from techniques_set2 import make_triple

bad = 0
for row in csv.DictReader(open("results/techniques_set2.csv")):
    rule = open(f"data/sigmahq_rules_set2/{row['rule_file']}", encoding="utf-8").read()
    mal, var, ben = make_triple(row["technique"])
    try:
        a, b, c = rule_matches(rule, mal), rule_matches(rule, var), rule_matches(rule, ben)
    except Exception as e:
        print(f"{row['technique']:10} ERROR {str(e)[:70]}"); bad += 1; continue
    ok = a and b and not c
    bad += (not ok)
    print(f"{row['technique']:10} attack={a!s:5} variant={b!s:5} harmless_fires={c!s:5} {'OK' if ok else '<-- CHECK THIS LOG'}")
print("all good" if bad == 0 else f"{bad} need fixing")