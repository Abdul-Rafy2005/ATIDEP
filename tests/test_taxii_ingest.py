"""Tests for data/taxii_ingest.py. No network is used."""
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


FAKE_GROUPS = {
    "APT29": ["T1547.001", "T1059.001", "T9999"],
    "FIN7": ["T1082", "T9998"],
}


class TestTaxiiIngest(unittest.TestCase):

    @mock.patch("data.taxii_ingest.list_groups", return_value=FAKE_GROUPS)
    def test_ingest_known_group(self, _):
        from data.taxii_ingest import ingest_by_group
        result = ingest_by_group("APT29")
        self.assertEqual(result["source"], "taxii")
        self.assertEqual(result["group"], "APT29")
        self.assertEqual(result["total_techniques"], 3)
        # T1547.001 and T1059.001 are in our sets; T9999 is not
        self.assertEqual(result["supported_techniques"], 2)
        ids = [t["id"] for t in result["techniques"]]
        self.assertIn("T1547.001", ids)
        self.assertIn("T9999", ids)
        unsupported = [t for t in result["techniques"] if t["id"] == "T9999"][0]
        self.assertFalse(unsupported["supported"])
        self.assertIsNone(unsupported["set"])

    @mock.patch("data.taxii_ingest.list_groups", return_value=FAKE_GROUPS)
    def test_ingest_unknown_group(self, _):
        from data.taxii_ingest import ingest_by_group
        result = ingest_by_group("DOESNOTEXIST")
        self.assertEqual(result["source"], "taxii")
        self.assertEqual(result["total_techniques"], 0)

    @mock.patch("data.taxii_ingest.list_groups", return_value=None)
    def test_fallback_when_taxii_down(self, _):
        from data.taxii_ingest import ingest_by_group
        result = ingest_by_group("APT29")
        self.assertEqual(result["source"], "local_fallback")
        self.assertIsNone(result["group"])
        self.assertGreater(result["supported_techniques"], 0)

    @mock.patch("data.taxii_ingest.list_groups", return_value=FAKE_GROUPS)
    def test_ingest_all_groups(self, _):
        from data.taxii_ingest import ingest_all_groups
        result = ingest_all_groups()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # Sorted by supported desc
        self.assertEqual(result[0]["group"], "APT29")
        self.assertEqual(result[0]["supported"], 2)

    @mock.patch("data.taxii_ingest.list_groups", return_value=None)
    def test_ingest_all_groups_offline(self, _):
        from data.taxii_ingest import ingest_all_groups
        result = ingest_all_groups()
        self.assertIsNone(result)


class TestBuildGroupTechniques(unittest.TestCase):

    def test_builds_group_map(self):
        from data.taxii_connector import build_group_techniques
        all_objects = {
            "attack-pattern": [
                {
                    "id": "attack-pattern--1",
                    "type": "attack-pattern",
                    "name": "Test",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1234"}
                    ],
                }
            ],
            "intrusion-set": [
                {
                    "id": "intrusion-set--1",
                    "type": "intrusion-set",
                    "name": "TestGroup",
                }
            ],
            "relationship": [
                {
                    "id": "relationship--1",
                    "type": "relationship",
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--1",
                    "target_ref": "attack-pattern--1",
                }
            ],
        }
        groups = build_group_techniques(all_objects)
        self.assertIn("TestGroup", groups)
        self.assertEqual(groups["TestGroup"], ["T1234"])

    def test_skips_revoked(self):
        from data.taxii_connector import build_group_techniques
        all_objects = {
            "attack-pattern": [
                {
                    "id": "attack-pattern--1",
                    "type": "attack-pattern",
                    "name": "Revoked",
                    "revoked": True,
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1234"}
                    ],
                }
            ],
            "intrusion-set": [
                {"id": "intrusion-set--1", "type": "intrusion-set", "name": "G"}
            ],
            "relationship": [
                {
                    "id": "relationship--1",
                    "type": "relationship",
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--1",
                    "target_ref": "attack-pattern--1",
                }
            ],
        }
        groups = build_group_techniques(all_objects)
        self.assertEqual(groups, {})


if __name__ == "__main__":
    unittest.main()
