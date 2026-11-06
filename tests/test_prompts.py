import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))

import compare_models
from generator.generate import TECHNIQUES, make_pair
from generator.techniques_set2 import TECHNIQUES2, DESCRIPTIONS2
from llm.prompts import v1


def test_v1_matches_set1():
    for tech in TECHNIQUES:
        expected = compare_models.build_prompt(tech)
        actual = v1.build_prompt(tech, TECHNIQUES, compare_models.DESCRIPTIONS)
        assert actual == expected, tech


def test_v1_matches_set2():
    import compare_set2
    for tech in TECHNIQUES2:
        expected = compare_set2.cm.build_prompt(tech)
        actual = v1.build_prompt(tech, TECHNIQUES2, DESCRIPTIONS2)
        assert actual == expected, tech


if __name__ == "__main__":
    test_v1_matches_set1()
    test_v1_matches_set2()
    print("v1 prompt tests passed for 24 techniques")