import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))

from runner import rule_matches, rule_to_sql
from techniques_set3 import TECHNIQUES3, DESCRIPTIONS3, make_triple3
from generate import TECHNIQUES
from techniques_set2 import TECHNIQUES2

EXCLUDED_TECH_IDS = {
    # Set 1
    "T1003.001", "T1033", "T1047", "T1053.005", "T1059.001", "T1105",
    "T1136.001", "T1197", "T1218.005", "T1218.010", "T1218.011", "T1547.001",
    # Set 2
    "T1021.002", "T1059", "T1090", "T1218.001", "T1218.008", "T1222.001",
    "T1482", "T1485", "T1489", "T1490", "T1546.007", "T1560.001",
    # Prompt examples
    "T1016", "T1059.005", "T1497.003", "T1564.001"
}


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def copy_rule(event):
    program = event["Image"].split("\\")[-1]
    command = event["CommandLine"].replace("\\", "\\\\")
    return (
        "title: copy\nstatus: test\nlogsource:\n  category: process_creation\n"
        "  product: windows\ndetection:\n  selection:\n"
        f"    Image|endswith: {quote('\\' + program)}\n"
        f"    CommandLine|contains: {quote(command)}\n"
        "  condition: selection\nlevel: low\ntags: []\n"
    )


def single_pass(rule, shown, benign):
    rule_to_sql(rule)
    return rule_matches(rule, shown) and not rule_matches(rule, benign)


def strict_verdict(rule, shown, variant, benign):
    rule_to_sql(rule)
    if not rule_matches(rule, shown):
        return "MISSED_SHOWN"
    if rule_matches(rule, benign):
        return "NOISY"
    return "PASS" if rule_matches(rule, variant) else "TOO_NARROW"


def test_set3_technique_count_and_overlap():
    assert len(TECHNIQUES3) == 20, f"Expected 20 techniques, got {len(TECHNIQUES3)}"
    overlap = set(TECHNIQUES3.keys()).intersection(EXCLUDED_TECH_IDS)
    assert not overlap, f"Found overlapping technique IDs: {overlap}"


def test_set3_copy_rules_too_narrow():
    for tech in TECHNIQUES3:
        shown, variant, benign = make_triple3(tech)
        rule = copy_rule(shown)
        assert single_pass(rule, shown, benign), f"Copy rule did not pass single gate for {tech}"
        assert strict_verdict(rule, shown, variant, benign) == "TOO_NARROW", (
            f"Copy rule did not fail as TOO_NARROW for {tech}"
        )


def test_set3_variant_types():
    vtypes = {}
    for tech, data in TECHNIQUES3.items():
        vt = data.get("variant_type")
        assert vt in ("values", "order_or_prefix"), f"Invalid variant_type {vt} for {tech}"
        vtypes[vt] = vtypes.get(vt, 0) + 1
    assert vtypes.get("values", 0) >= 8, f"Expected at least 8 values variants, got {vtypes.get('values')}"
    assert vtypes.get("order_or_prefix", 0) >= 8, (
        f"Expected at least 8 order_or_prefix variants, got {vtypes.get('order_or_prefix')}"
    )


def test_set3_descriptions():
    for tech, desc in DESCRIPTIONS3.items():
        words = desc.split()
        assert len(words) <= 20, f"Description for {tech} has {len(words)} words (max 20 allowed): '{desc}'"


if __name__ == "__main__":
    test_set3_technique_count_and_overlap()
    test_set3_copy_rules_too_narrow()
    test_set3_variant_types()
    test_set3_descriptions()
    print("all set 3 sanity checks passed: 20 techniques, 0 overlap, 20/20 TOO_NARROW, balanced variants, valid descriptions")

