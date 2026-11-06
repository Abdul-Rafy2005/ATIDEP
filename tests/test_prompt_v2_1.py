import difflib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))

from generator.generate import build_event
from llm.prompts import v2, v2_1
from validator.runner import rule_matches, rule_to_sql


def test_v2_1_differs_from_v2_in_exactly_two_places():
    v2_path = os.path.join(os.path.dirname(__file__), "..", "llm", "prompts", "v2.py")
    v2_1_path = os.path.join(os.path.dirname(__file__), "..", "llm", "prompts", "v2_1.py")
    with open(v2_path, encoding="utf-8") as f:
        v2_lines = f.readlines()
    with open(v2_1_path, encoding="utf-8") as f:
        v2_1_lines = f.readlines()

    diff = list(difflib.unified_diff(v2_lines, v2_1_lines, n=0))
    # Count how many hunks (lines starting with @@) exist
    hunks = [line for line in diff if line.startswith("@@")]
    assert len(hunks) == 2, f"Expected 2 diff hunks between v2 and v2_1, got {len(hunks)}"

    # Check place 1: instruction line about windash
    old_line = "- Windows tools accept - and / for flags. Use the windash modifier and write the flag with a dash, for example CommandLine|contains|windash: '-all'.\n"
    new_line = "- Windows tools accept - and / for flags. To match both, add windash to the key name and write the flag with a dash, for example CommandLine|contains|windash: '-all'. For a list of several parts, put every modifier in the key name: CommandLine|contains|windash|all: followed by a list of plain text values. windash is never a list item and never a key inside a list.\n"
    assert old_line in v2_lines
    assert new_line in v2_1_lines

    # Check place 2: Example 3 at end of EXAMPLES
    assert "Example 3" not in v2.EXAMPLES
    assert "Example 3" in v2_1.EXAMPLES
    assert "Technique: T1497.003" in v2_1.EXAMPLES


def test_example_3_converts_and_fires():
    example_3_rule = """title: Ping Used As A Delay
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\ping.exe'
        CommandLine|contains|windash|all:
            - '127.0.0.1'
            - '-n'
    condition: selection
level: low
tags:
    - attack.defense-evasion
    - attack.t1497.003
"""
    sql = rule_to_sql(example_3_rule)
    assert sql is not None

    event = build_event("C:\\Windows\\System32\\ping.exe", "ping.exe 127.0.0.1 -n 30")
    assert rule_matches(example_3_rule, event) is True

    # Also test slash variant handled by windash
    event_slash = build_event("C:\\Windows\\System32\\ping.exe", "ping.exe 127.0.0.1 /n 30")
    assert rule_matches(example_3_rule, event_slash) is True

    # Unrelated ping command should not fire
    event_benign = build_event("C:\\Windows\\System32\\ping.exe", "ping.exe 8.8.8.8")
    assert rule_matches(example_3_rule, event_benign) is False


if __name__ == "__main__":
    test_v2_1_differs_from_v2_in_exactly_two_places()
    test_example_3_converts_and_fires()
    print("v2_1 prompt tests passed: exactly 2 differences from v2 and Example 3 rule verified")

