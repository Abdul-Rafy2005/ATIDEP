import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))

from analyze_results import analyze_rule
from generate import TECHNIQUES, make_pair, make_triple
from runner import rule_matches, rule_to_sql
from techniques_set2 import TECHNIQUES2, make_triple as make_triple_set2

KEYWORDS = {
    "T1059.001": "DownloadString",
    "T1218.011": ".sys,",
    "T1218.005": "javascript",
    "T1218.010": "scrobj",
    "T1105": "urlcache",
    "T1053.005": "\\Temp\\",
    "T1547.001": r"CurrentVersion\Run",
    "T1136.001": "/add",
    "T1003.001": "lsass",
    "T1197": "/transfer",
    "T1047": "process call create",
    "T1033": "priv",
}


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def copy_rule(event):
    program = event["Image"].split("\\")[-1]
    command = event["CommandLine"].replace("\\", "\\\\")
    return ("title: copy\nstatus: test\nlogsource:\n  category: process_creation\n"
            "  product: windows\ndetection:\n  selection:\n"
            f"    Image|endswith: {quote('\\' + program)}\n"
            f"    CommandLine|contains: {quote(command)}\n"
            "  condition: selection\nlevel: low\ntags: []\n")


def keyword_rule(keyword):
    return ("title: keyword\nstatus: test\nlogsource:\n  category: process_creation\n"
            "  product: windows\ndetection:\n  selection:\n"
            f"    CommandLine|contains: {quote(keyword)}\n"
            "  condition: selection\nlevel: low\ntags: []\n")


def single_pass(rule, shown, benign):
    rule_to_sql(rule)
    return rule_matches(rule, shown) and not rule_matches(rule, benign)


def strict_set1_verdict(rule, tech):
    shown, variant, benign = make_triple(tech)
    rule_to_sql(rule)
    if not rule_matches(rule, shown):
        return "MISSED_SHOWN"
    if rule_matches(rule, benign):
        return "NOISY"
    return "PASS" if rule_matches(rule, variant) else "TOO_NARROW"


def test_copy_rules_pass_single_and_fail_strict():
    for tech in TECHNIQUES:
        shown, benign = make_pair(tech)
        rule = copy_rule(shown)
        assert single_pass(rule, shown, benign), tech
        assert strict_set1_verdict(rule, tech) == "TOO_NARROW", tech
    for tech in TECHNIQUES2:
        shown, _, benign = make_triple_set2(tech)
        rule = copy_rule(shown)
        assert single_pass(rule, shown, benign), tech
        assert analyze_rule(rule, tech, 2)["verdict"] == "TOO_NARROW", tech


def test_set1_keyword_rules_pass_strict():
    for tech, keyword in KEYWORDS.items():
        shown, benign = make_pair(tech)
        assert strict_set1_verdict(keyword_rule(keyword), tech) == "PASS", tech


if __name__ == "__main__":
    test_copy_rules_pass_single_and_fail_strict()
    test_set1_keyword_rules_pass_strict()
    print("copy rules: 24 single-gate passes and strict TOO_NARROW results")
    print("keyword rules: 12 strict-gate passes")