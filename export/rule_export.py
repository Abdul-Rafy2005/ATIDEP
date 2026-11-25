"""Convert Sigma YAML rules to Splunk SPL, Microsoft KQL, and other formats.

Uses pySigma backends. Each function takes a Sigma rule as YAML text
and returns the converted query string, or raises on bad input.
"""

from sigma.collection import SigmaCollection
from sigma.backends.splunk import SplunkBackend
from sigma.backends.microsoft365defender import KustoBackend
from sigma.backends.sqlite import sqlite as sqlite_mod

FORMATS = {
    "sigma": "Sigma YAML (original)",
    "splunk": "Splunk SPL",
    "kql": "Microsoft Defender KQL",
    "sqlite": "SQLite (pySigma test query)",
}


def to_splunk(rule_yaml: str) -> str:
    """Convert a Sigma rule to Splunk SPL."""
    col = SigmaCollection.from_yaml(rule_yaml)
    backend = SplunkBackend()
    queries = backend.convert(col)
    if not queries:
        raise ValueError("Splunk backend returned no queries")
    return queries[0]


def to_kql(rule_yaml: str) -> str:
    """Convert a Sigma rule to Microsoft Defender KQL."""
    col = SigmaCollection.from_yaml(rule_yaml)
    backend = KustoBackend()
    queries = backend.convert(col)
    if not queries:
        raise ValueError("KQL backend returned no queries")
    return queries[0]


def to_sqlite(rule_yaml: str) -> str:
    """Convert a Sigma rule to SQLite SQL (same as the validation gate)."""
    col = SigmaCollection.from_yaml(rule_yaml)
    backend = sqlite_mod.sqliteBackend()
    queries = backend.convert(col)
    if not queries:
        raise ValueError("SQLite backend returned no queries")
    return queries[0]


def convert(rule_yaml: str, fmt: str) -> str:
    """Convert a Sigma rule to the requested format.

    fmt: one of 'sigma', 'splunk', 'kql', 'sqlite'.
    Returns the converted string.
    """
    if fmt == "sigma":
        return rule_yaml
    if fmt == "splunk":
        return to_splunk(rule_yaml)
    if fmt == "kql":
        return to_kql(rule_yaml)
    if fmt == "sqlite":
        return to_sqlite(rule_yaml)
    raise ValueError(f"Unknown format: {fmt}. Supported: {', '.join(FORMATS)}")


def convert_all(rule_yaml: str) -> dict:
    """Convert a Sigma rule to all supported formats.

    Returns a dict of {format_name: converted_string_or_error}.
    """
    results = {"sigma": rule_yaml}
    for fmt in ("splunk", "kql", "sqlite"):
        try:
            results[fmt] = convert(rule_yaml, fmt)
        except Exception as e:
            results[fmt] = f"Error: {e}"
    return results
