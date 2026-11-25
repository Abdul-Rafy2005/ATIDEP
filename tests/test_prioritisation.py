"""Tests for the threat-informed prioritisation module."""

import sys
import os
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from export.prioritisation import (
    _invert_groups,
    _supported_technique_ids,
    build_priority_backlog,
)


class TestInvertGroups(unittest.TestCase):
    def test_basic_inversion(self):
        groups = {
            "APT29": ["T1059.001", "T1547.001"],
            "APT28": ["T1059.001", "T1105"],
        }
        result = _invert_groups(groups)
        self.assertEqual(len(result["T1059.001"]), 2)
        self.assertIn("APT29", result["T1059.001"])
        self.assertIn("APT28", result["T1059.001"])
        self.assertEqual(len(result["T1547.001"]), 1)
        self.assertEqual(len(result["T1105"]), 1)

    def test_empty_groups(self):
        result = _invert_groups({})
        self.assertEqual(result, {})

    def test_single_group_single_technique(self):
        result = _invert_groups({"FIN7": ["T1059"]})
        self.assertEqual(len(result), 1)
        self.assertIn("FIN7", result["T1059"])


class TestSupportedTechniques(unittest.TestCase):
    def test_returns_44(self):
        supported = _supported_technique_ids()
        self.assertEqual(len(supported), 44)

    def test_known_techniques_present(self):
        supported = _supported_technique_ids()
        self.assertIn("T1059.001", supported)
        self.assertIn("T1615", supported)
        self.assertIn("T1485", supported)


class TestBuildPriorityBacklog(unittest.TestCase):
    """All tests patch list_groups to avoid TAXII network calls."""

    def _backlog_no_taxii(self):
        with patch("data.taxii_ingest.list_groups", return_value=None):
            return build_priority_backlog(timeout=1)

    def test_local_fallback(self):
        result = self._backlog_no_taxii()
        self.assertEqual(result["source"], "local_only")
        self.assertIn("backlog", result)
        self.assertEqual(result["our_techniques"], 44)
        self.assertIsInstance(result["backlog"], list)
        self.assertGreater(len(result["backlog"]), 0)

    def test_backlog_entries_have_required_fields(self):
        result = self._backlog_no_taxii()
        for entry in result["backlog"][:5]:
            self.assertIn("id", entry)
            self.assertIn("name", entry)
            self.assertIn("tactics", entry)
            self.assertIn("group_count", entry)
            self.assertIn("top_groups", entry)
            self.assertIn("in_pipeline", entry)
            self.assertIn("covered", entry)
            self.assertIn("set", entry)
            self.assertIsInstance(entry["group_count"], int)
            self.assertIsInstance(entry["in_pipeline"], bool)
            self.assertIsInstance(entry["covered"], bool)

    def test_pipeline_techniques_flagged(self):
        result = self._backlog_no_taxii()
        pipeline_entries = [e for e in result["backlog"] if e["in_pipeline"]]
        self.assertEqual(len(pipeline_entries), 44)
        for entry in pipeline_entries:
            self.assertIn(entry["set"], [1, 2, 3])

    def test_non_pipeline_set_is_none(self):
        result = self._backlog_no_taxii()
        non_pipeline = [e for e in result["backlog"] if not e["in_pipeline"]]
        for entry in non_pipeline[:10]:
            self.assertIsNone(entry["set"])

    def test_covered_count_matches(self):
        result = self._backlog_no_taxii()
        covered_in_backlog = sum(1 for e in result["backlog"] if e["covered"])
        self.assertEqual(covered_in_backlog, result["covered"])

    def test_sort_order_uncovered_first(self):
        result = self._backlog_no_taxii()
        backlog = result["backlog"]
        pipeline_entries = [e for e in backlog if e["in_pipeline"]]
        if len(pipeline_entries) < 2:
            return
        uncovered_pipeline = [e for e in pipeline_entries if not e["covered"]]
        covered_pipeline = [e for e in pipeline_entries if e["covered"]]
        if uncovered_pipeline and covered_pipeline:
            first_uncov_idx = backlog.index(uncovered_pipeline[0])
            last_covered_idx = backlog.index(covered_pipeline[-1])
            self.assertLess(first_uncov_idx, last_covered_idx)

    def test_top_groups_limited_to_5(self):
        result = self._backlog_no_taxii()
        for entry in result["backlog"]:
            self.assertLessEqual(len(entry["top_groups"]), 5)

    def test_with_mock_taxii(self):
        mock_groups = {
            "TestGroup1": ["T1059.001", "T1105", "T1047"],
            "TestGroup2": ["T1059.001", "T1615"],
            "TestGroup3": ["T1059.001"],
        }
        with patch("data.taxii_ingest.list_groups", return_value=mock_groups):
            result = build_priority_backlog(timeout=1)
        self.assertEqual(result["source"], "taxii")
        self.assertEqual(result["total_groups"], 3)
        t1059 = next(e for e in result["backlog"] if e["id"] == "T1059.001")
        self.assertEqual(t1059["group_count"], 3)
        self.assertTrue(t1059["in_pipeline"])


class TestDashboardPriorityEndpoint(unittest.TestCase):
    def setUp(self):
        from dashboard.app import app
        self.client = app.test_client()
        self._patcher = patch("data.taxii_ingest.list_groups", return_value=None)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

    def test_priority_backlog_endpoint(self):
        res = self.client.get("/api/priority-backlog")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("backlog", data)
        self.assertIn("our_techniques", data)
        self.assertEqual(data["our_techniques"], 44)

    def test_priority_backlog_filter_uncovered(self):
        res = self.client.get("/api/priority-backlog?filter=uncovered")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for entry in data["backlog"]:
            self.assertFalse(entry["covered"])

    def test_priority_backlog_filter_in_pipeline(self):
        res = self.client.get("/api/priority-backlog?filter=in_pipeline")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for entry in data["backlog"]:
            self.assertTrue(entry["in_pipeline"])

    def test_priority_backlog_limit(self):
        res = self.client.get("/api/priority-backlog?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertLessEqual(len(data["backlog"]), 5)


if __name__ == "__main__":
    unittest.main()
