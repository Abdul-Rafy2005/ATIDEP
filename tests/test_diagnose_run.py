import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from llm.diagnose_run import inspect_rule, modifier_chains


def rule(chain):
    values = "'value'" if chain != "contains|windash|all" else "\n      - '-one'\n      - '-two'"
    return ("title: test\nstatus: test\nlogsource:\n  category: process_creation\n"
            "  product: windows\ndetection:\n  selection:\n    " + chain + ": " + values +
            "\n  condition: selection\nlevel: low\ntags: []\n")


def test_bad_modifier_chain_is_syntax_error():
    result = inspect_rule(rule("CommandLine|contains|not_a_modifier"))
    assert not result["syntax"]
    assert result["error"]


def test_modifier_chain_extraction():
    result = inspect_rule(rule("CommandLine|contains|windash|all"))
    assert ("CommandLine", ("contains", "windash", "all")) in result["chains"]


if __name__ == "__main__":
    test_bad_modifier_chain_is_syntax_error()
    test_modifier_chain_extraction()
    print("diagnosis tests passed")