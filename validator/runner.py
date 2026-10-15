import json, sqlite3
from sigma.collection import SigmaCollection
from sigma.backends.sqlite import sqlite

FIELDS = ["Image", "CommandLine", "ParentImage", "ParentCommandLine",
          "OriginalFileName", "User", "IntegrityLevel", "Description",
          "Product", "Company"]

def rule_to_sql(rule_yaml_text):
    """Turn a Sigma rule (yaml text) into a SQL query. Raises an error if the rule is broken."""
    rules = SigmaCollection.from_yaml(rule_yaml_text)
    backend = sqlite.sqliteBackend()
    queries = backend.convert(rules)
    return queries[0]

def load_event(path):
    """Read one real Sysmon event (SigmaHQ test log) and keep only the fields we use."""
    data = json.load(open(path, encoding="utf-8-sig"))
    ed = data["Event"]["EventData"]
    return {k: ed.get(k, "") for k in FIELDS}

def rule_matches(rule_yaml_text, event):
    """True if the rule fires on this one event."""
    sql = rule_to_sql(rule_yaml_text)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE logs (" + ", ".join(f'"{f}" TEXT' for f in FIELDS) + ")")
    con.execute("INSERT INTO logs VALUES (" + ",".join("?" * len(FIELDS)) + ")",
                [event[f] for f in FIELDS])
    n = len(con.execute(sql).fetchall())
    con.close()
    return n > 0