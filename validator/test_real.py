import csv, glob
from runner import rule_matches, load_event

for row in csv.DictReader(open("results/techniques.csv")):
    if row["has_test_data"] != "True":
        continue
    name = row["rule_file"][:-4]
    rule = open(f"data/sigmahq_rules/{row['rule_file']}", encoding="utf-8").read()
    log = glob.glob(f"data/sigmahq_test_logs/{name}/*.json")[0]
    ev = load_event(log)
    try:
        hit = rule_matches(rule, ev)
    except Exception as e:
        hit = f"ERROR {type(e).__name__}: {str(e)[:80]}"
    print(f"{row['technique']:10} {name[17:50]:34} fires on real attack log: {hit}")