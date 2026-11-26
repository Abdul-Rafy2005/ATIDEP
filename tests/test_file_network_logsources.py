"""Tests for file creation and network connection logsource support."""

import sys
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generator.logsources import FIELDS_FILE_CREATE, FIELDS_NETWORK
from generator.techniques_file_create import (
    TECHNIQUES_FILE, DESCRIPTIONS_FILE, build_file_event, make_triple_file,
)
from generator.techniques_network import (
    TECHNIQUES_NETWORK, DESCRIPTIONS_NETWORK, build_network_event, make_triple_network,
)
from validator.runner import rule_to_sql, rule_matches


class TestFileTechniques(unittest.TestCase):
    def test_eight_techniques(self):
        self.assertEqual(len(TECHNIQUES_FILE), 8)

    def test_descriptions_match(self):
        self.assertEqual(set(TECHNIQUES_FILE.keys()), set(DESCRIPTIONS_FILE.keys()))

    def test_each_has_shown_variant_benign(self):
        for tid, t in TECHNIQUES_FILE.items():
            self.assertIn("shown", t, f"{tid} missing shown")
            self.assertIn("variant", t, f"{tid} missing variant")
            self.assertIn("benign", t, f"{tid} missing benign")

    def test_shown_and_variant_differ(self):
        for tid, t in TECHNIQUES_FILE.items():
            self.assertNotEqual(t["shown"], t["variant"], f"{tid}")

    def test_build_event_has_all_fields(self):
        ev = build_file_event(TECHNIQUES_FILE["T1105-file"]["shown"])
        for f in FIELDS_FILE_CREATE:
            self.assertIn(f, ev)

    def test_make_triple_returns_three(self):
        s, v, b = make_triple_file("T1105-file")
        self.assertIsInstance(s, dict)
        self.assertIsInstance(v, dict)
        self.assertIsInstance(b, dict)


class TestNetworkTechniques(unittest.TestCase):
    def test_eight_techniques(self):
        self.assertEqual(len(TECHNIQUES_NETWORK), 8)

    def test_descriptions_match(self):
        self.assertEqual(set(TECHNIQUES_NETWORK.keys()), set(DESCRIPTIONS_NETWORK.keys()))

    def test_each_has_shown_variant_benign(self):
        for tid, t in TECHNIQUES_NETWORK.items():
            self.assertIn("shown", t, f"{tid} missing shown")
            self.assertIn("variant", t, f"{tid} missing variant")
            self.assertIn("benign", t, f"{tid} missing benign")

    def test_shown_and_variant_differ(self):
        for tid, t in TECHNIQUES_NETWORK.items():
            self.assertNotEqual(t["shown"], t["variant"], f"{tid}")

    def test_build_event_has_all_fields(self):
        ev = build_network_event(TECHNIQUES_NETWORK["T1071.001-net"]["shown"])
        for f in FIELDS_NETWORK:
            self.assertIn(f, ev)

    def test_make_triple_returns_three(self):
        s, v, b = make_triple_network("T1071.001-net")
        self.assertIsInstance(s, dict)
        self.assertIsInstance(v, dict)
        self.assertIsInstance(b, dict)


class TestFileRuleMatching(unittest.TestCase):
    GOOD_RULE = """
title: Executable Dropped In Public Folder
status: test
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|contains: '\\Users\\Public\\'
        TargetFilename|endswith: '.exe'
    condition: selection
level: medium
tags:
    - attack.command-and-control
    - attack.t1105
"""

    def test_fires_on_shown(self):
        shown, _, _ = make_triple_file("T1105-file")
        self.assertTrue(rule_matches(self.GOOD_RULE, shown))

    def test_quiet_on_benign(self):
        _, _, benign = make_triple_file("T1105-file")
        self.assertFalse(rule_matches(self.GOOD_RULE, benign))


class TestNetworkRuleMatching(unittest.TestCase):
    GOOD_RULE = """
title: Rundll32 Outbound Connection
status: test
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        Image|endswith:
            - '\\rundll32.exe'
            - '\\regsvr32.exe'
        Initiated: 'true'
    condition: selection
level: high
tags:
    - attack.command-and-control
    - attack.t1071.001
"""

    def test_fires_on_shown(self):
        shown, _, _ = make_triple_network("T1071.001-net")
        self.assertTrue(rule_matches(self.GOOD_RULE, shown))

    def test_fires_on_variant(self):
        _, variant, _ = make_triple_network("T1071.001-net")
        self.assertTrue(rule_matches(self.GOOD_RULE, variant))

    def test_quiet_on_benign(self):
        _, _, benign = make_triple_network("T1071.001-net")
        self.assertFalse(rule_matches(self.GOOD_RULE, benign))


class TestScoringIntegration(unittest.TestCase):
    def test_file_scoring(self):
        from llm.scoring import score_rule
        rule = TestFileRuleMatching.GOOD_RULE
        result = score_rule("file", "T1105-file", rule)
        self.assertTrue(result.syntax_ok)
        self.assertTrue(result.fires_shown)

    def test_network_scoring(self):
        from llm.scoring import score_rule
        rule = TestNetworkRuleMatching.GOOD_RULE
        result = score_rule("network", "T1071.001-net", rule)
        self.assertTrue(result.syntax_ok)
        self.assertTrue(result.strict_pass)


if __name__ == "__main__":
    unittest.main()
