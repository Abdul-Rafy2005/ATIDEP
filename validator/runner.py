import json, sqlite3, os, sys
from sigma.collection import SigmaCollection
from sigma.backends.sqlite import sqlite

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
from logsources import FIELDS_PROCESS_CREATION, CATEGORY_FIELDS

FIELDS = FIELDS_PROCESS_CREATION

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

def _fields_for_event(event):
    """Pick the field list that covers all keys in the event."""
    keys = set(event.keys())
    for fields in CATEGORY_FIELDS.values():
        if keys <= set(fields):
            return fields
    return list(keys)

def rule_matches(rule_yaml_text, event, fields=None):
    """True if the rule fires on this one event.

    If fields is None, the field list is inferred from the event's keys.
    Existing callers that pass process_creation events work unchanged.
    """
    sql = rule_to_sql(rule_yaml_text)
    if fields is None:
        fields = _fields_for_event(event)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE logs (" + ", ".join(f'"{f}" TEXT' for f in fields) + ")")
    con.execute("INSERT INTO logs VALUES (" + ",".join("?" * len(fields)) + ")",
                [event.get(f, "") for f in fields])
    n = len(con.execute(sql).fetchall())
    con.close()
    return n > 0