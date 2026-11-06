import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))
from analyze_results import analyze_rule, inspect_yaml


def rule(detection):
    return "title: test\nlogsource:\n  category: process_creation\ndetection:\n" + detection + "  condition: selection\n"


def test_duplicate_keys():
    _, duplicates = inspect_yaml(rule("  selection:\n    CommandLine|contains: one\n    CommandLine|contains: two\n"))
    assert duplicates == ["CommandLine|contains"]


def test_padded_value():
    result = analyze_rule(rule("  selection:\n    Image|endswith: ' foo.exe '\n"), "T1033", 1)
    assert result["padded_values"]


def test_set2_instance_specific_value():
    text = rule("  selection:\n    CommandLine|contains: 'hh.exe http://10.0.0.5/help.chm'\n")
    result = analyze_rule(text, "T1218.001", 2)
    assert result["instance_specific_values"]


def test_copied_line_is_too_narrow_on_set2():
    shown = "hh.exe http://10.0.0.5/help.chm"
    text = rule(f"  selection:\n    CommandLine|contains: '{shown}'\n")
    result = analyze_rule(text, "T1218.001", 2)
    assert result["verdict"] == "TOO_NARROW"
    assert result["copied"]


if __name__ == "__main__":
    for test in (test_duplicate_keys, test_padded_value,
                 test_set2_instance_specific_value,
                 test_copied_line_is_too_narrow_on_set2):
        test()
    print("4 tests passed")