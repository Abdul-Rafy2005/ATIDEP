"""Tests for multi-logsource support: field schemas, registry events, and gate."""

import sys
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generator.logsources import (
    FIELDS_PROCESS_CREATION, FIELDS_REGISTRY, FIELDS_FILE_CREATE,
    FIELDS_NETWORK, CATEGORY_FIELDS, CATEGORY_BASE,
)
from generator.techniques_registry import (
    TECHNIQUES_REGISTRY, DESCRIPTIONS_REGISTRY,
    build_registry_event, make_triple_registry, LOGSOURCE_CATEGORY,
)
from validator.runner import rule_to_sql, rule_matches, _fields_for_event


class TestFieldSchemas(unittest.TestCase):
    def test_process_creation_has_image_and_commandline(self):
        self.assertIn("Image", FIELDS_PROCESS_CREATION)
        self.assertIn("CommandLine", FIELDS_PROCESS_CREATION)

    def test_registry_has_target_object(self):
        self.assertIn("TargetObject", FIELDS_REGISTRY)
        self.assertIn("EventType", FIELDS_REGISTRY)
        self.assertIn("Details", FIELDS_REGISTRY)

    def test_file_create_has_target_filename(self):
        self.assertIn("TargetFilename", FIELDS_FILE_CREATE)

    def test_network_has_destination_fields(self):
        self.assertIn("DestinationIp", FIELDS_NETWORK)
        self.assertIn("DestinationPort", FIELDS_NETWORK)

    def test_category_lookup_covers_process_creation(self):
        self.assertIn("process_creation", CATEGORY_FIELDS)
        self.assertEqual(CATEGORY_FIELDS["process_creation"], FIELDS_PROCESS_CREATION)

    def test_category_lookup_covers_registry(self):
        self.assertIn("registry_set", CATEGORY_FIELDS)
        self.assertEqual(CATEGORY_FIELDS["registry_set"], FIELDS_REGISTRY)

    def test_base_events_have_all_fields(self):
        for cat, fields in CATEGORY_FIELDS.items():
            base = CATEGORY_BASE[cat]
            for f in fields:
                self.assertIn(f, base, f"field {f} missing from BASE for {cat}")


class TestRegistryTechniques(unittest.TestCase):
    def test_eight_techniques(self):
        self.assertEqual(len(TECHNIQUES_REGISTRY), 8)

    def test_descriptions_match_techniques(self):
        self.assertEqual(set(TECHNIQUES_REGISTRY.keys()), set(DESCRIPTIONS_REGISTRY.keys()))

    def test_logsource_category(self):
        self.assertEqual(LOGSOURCE_CATEGORY, "registry_set")

    def test_each_technique_has_shown_variant_benign(self):
        for tid, t in TECHNIQUES_REGISTRY.items():
            self.assertIn("shown", t, f"{tid} missing shown")
            self.assertIn("variant", t, f"{tid} missing variant")
            self.assertIn("benign", t, f"{tid} missing benign")

    def test_shown_and_variant_differ(self):
        for tid, t in TECHNIQUES_REGISTRY.items():
            self.assertNotEqual(t["shown"], t["variant"],
                                f"{tid} shown and variant are identical")

    def test_shown_and_benign_differ(self):
        for tid, t in TECHNIQUES_REGISTRY.items():
            self.assertNotEqual(t["shown"], t["benign"],
                                f"{tid} shown and benign are identical")

    def test_build_registry_event_has_all_fields(self):
        ev = build_registry_event(TECHNIQUES_REGISTRY["T1547.001-reg"]["shown"])
        for f in FIELDS_REGISTRY:
            self.assertIn(f, ev)

    def test_make_triple_returns_three(self):
        shown, variant, benign = make_triple_registry("T1547.001-reg")
        self.assertIsInstance(shown, dict)
        self.assertIsInstance(variant, dict)
        self.assertIsInstance(benign, dict)


class TestFieldInference(unittest.TestCase):
    def test_process_creation_event(self):
        ev = {f: "" for f in FIELDS_PROCESS_CREATION}
        fields = _fields_for_event(ev)
        self.assertEqual(fields, FIELDS_PROCESS_CREATION)

    def test_registry_event(self):
        ev = {f: "" for f in FIELDS_REGISTRY}
        fields = _fields_for_event(ev)
        self.assertEqual(fields, FIELDS_REGISTRY)


class TestRegistryRuleMatching(unittest.TestCase):
    """Test that the gate can evaluate a Sigma rule against registry events."""

    GOOD_RULE = """
title: Run Key Persistence
status: test
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|contains: 'CurrentVersion\\Run'
    filter_legit:
        Image|endswith:
            - '\\msiexec.exe'
            - '\\explorer.exe'
    condition: selection and not filter_legit
level: medium
tags:
    - attack.persistence
    - attack.t1547.001
"""

    NARROW_RULE = """
title: Narrow Run Key Rule
status: test
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|endswith: 'Run\\Updater'
        Details: 'C:\\Users\\Public\\malware.exe'
    condition: selection
level: medium
tags:
    - attack.persistence
    - attack.t1547.001
"""

    def test_good_rule_fires_on_shown(self):
        shown, _, _ = make_triple_registry("T1547.001-reg")
        self.assertTrue(rule_matches(self.GOOD_RULE, shown))

    def test_good_rule_fires_on_variant(self):
        _, variant, _ = make_triple_registry("T1547.001-reg")
        self.assertTrue(rule_matches(self.GOOD_RULE, variant))

    def test_good_rule_quiet_on_benign(self):
        _, _, benign = make_triple_registry("T1547.001-reg")
        self.assertFalse(rule_matches(self.GOOD_RULE, benign))

    def test_narrow_rule_fires_on_shown(self):
        shown, _, _ = make_triple_registry("T1547.001-reg")
        self.assertTrue(rule_matches(self.NARROW_RULE, shown))

    def test_narrow_rule_misses_variant(self):
        _, variant, _ = make_triple_registry("T1547.001-reg")
        self.assertFalse(rule_matches(self.NARROW_RULE, variant))

    def test_syntax_check_works(self):
        sql = rule_to_sql(self.GOOD_RULE)
        self.assertIn("SELECT", sql.upper())


class TestScoringWithRegistry(unittest.TestCase):
    """Test that score_rule works with set_id='registry'."""

    GOOD_RULE = TestRegistryRuleMatching.GOOD_RULE

    def test_score_rule_pass(self):
        from llm.scoring import score_rule
        result = score_rule("registry", "T1547.001-reg", self.GOOD_RULE)
        self.assertTrue(result.syntax_ok)
        self.assertTrue(result.fires_shown)
        self.assertTrue(result.fires_variant)
        self.assertFalse(result.fires_benign)
        self.assertTrue(result.strict_pass)
        self.assertEqual(result.verdict, "PASS")

    def test_score_rule_too_narrow(self):
        from llm.scoring import score_rule
        narrow = TestRegistryRuleMatching.NARROW_RULE
        result = score_rule("registry", "T1547.001-reg", narrow)
        self.assertTrue(result.syntax_ok)
        self.assertTrue(result.fires_shown)
        self.assertFalse(result.fires_variant)
        self.assertEqual(result.verdict, "TOO_NARROW")


if __name__ == "__main__":
    unittest.main()
