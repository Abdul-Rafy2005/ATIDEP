"""Tests for the ATT&CK STIX lookup module."""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOKUP_PATH = os.path.join(ROOT, "data", "attack_lookup.json")


class TestAttackLookupFile(unittest.TestCase):
    """Test that attack_lookup.json exists and has valid structure."""

    def test_lookup_file_exists(self):
        self.assertTrue(os.path.isfile(LOOKUP_PATH), "attack_lookup.json must exist")

    def test_lookup_is_valid_json(self):
        with open(LOOKUP_PATH, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 500, "Should have 500+ techniques")

    def test_every_entry_has_required_fields(self):
        with open(LOOKUP_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for tid, entry in data.items():
            self.assertTrue(tid.startswith("T"), f"{tid} should start with T")
            self.assertIn("name", entry, f"{tid} missing name")
            self.assertIn("tactics", entry, f"{tid} missing tactics")
            self.assertIsInstance(entry["tactics"], list)
            self.assertTrue(len(entry["name"]) > 0, f"{tid} has empty name")


class TestAttackLookupModule(unittest.TestCase):
    """Test the accessor functions in data/attack_lookup.py."""

    def test_get_technique_known(self):
        from data.attack_lookup import get_technique
        t = get_technique("T1547.001")
        self.assertIsNotNone(t)
        self.assertEqual(t["name"], "Registry Run Keys / Startup Folder")
        self.assertIn("Persistence", t["tactics"])

    def test_get_technique_unknown(self):
        from data.attack_lookup import get_technique
        self.assertIsNone(get_technique("T9999.999"))

    def test_get_name_known(self):
        from data.attack_lookup import get_name
        self.assertEqual(get_name("T1059.001"), "PowerShell")

    def test_get_name_fallback(self):
        from data.attack_lookup import get_name
        self.assertEqual(get_name("T9999"), "T9999")

    def test_get_tactics_known(self):
        from data.attack_lookup import get_tactics
        tactics = get_tactics("T1547.001")
        self.assertIn("Persistence", tactics)
        self.assertIn("Privilege Escalation", tactics)

    def test_get_tactics_unknown(self):
        from data.attack_lookup import get_tactics
        self.assertEqual(get_tactics("T9999"), [])

    def test_stealth_maps_to_defense_evasion(self):
        from data.attack_lookup import get_tactics
        tactics = get_tactics("T1564.004")
        self.assertIn("Defense Evasion", tactics)

    def test_all_our_techniques_present(self):
        """Every technique in our 3 sets should be in the lookup."""
        from data.attack_lookup import get_technique
        import csv
        for csv_name in ["techniques.csv", "techniques_set2.csv", "techniques_set3.csv"]:
            csv_path = os.path.join(ROOT, "results", csv_name)
            if not os.path.isfile(csv_path):
                continue
            with open(csv_path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    tid = row["technique"]
                    entry = get_technique(tid)
                    self.assertIsNotNone(entry, f"{tid} from {csv_name} not in ATT&CK lookup")


class TestBuildScript(unittest.TestCase):
    """Test the build script produces consistent output."""

    def test_tactic_display_covers_all_slugs(self):
        from data.build_attack_lookup import TACTIC_DISPLAY
        expected_slugs = [
            "reconnaissance", "resource-development", "initial-access",
            "execution", "persistence", "privilege-escalation",
            "defense-evasion", "stealth", "defense-impairment",
            "credential-access", "discovery", "lateral-movement",
            "collection", "command-and-control", "exfiltration", "impact",
        ]
        for slug in expected_slugs:
            self.assertIn(slug, TACTIC_DISPLAY, f"Missing slug: {slug}")


if __name__ == "__main__":
    unittest.main()
