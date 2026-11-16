"""Unit tests for the ATIDEP Dashboard Flask app and data loader."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dashboard.app import app
from dashboard.data_loader import (
    load_overview,
    load_runs,
    load_techniques,
    load_tactic_coverage,
    load_technique_detail,
    load_prompt_comparison,
)


class TestDataLoader(unittest.TestCase):
    """Test data extraction from results and coverage files."""

    def test_load_overview(self):
        ov = load_overview()
        self.assertIn("total_techniques", ov)
        self.assertEqual(ov["total_techniques"], 44)
        self.assertGreaterEqual(ov["covered"], 20)
        self.assertGreater(ov["total_rules_tested"], 500)

    def test_load_runs(self):
        runs = load_runs()
        self.assertGreaterEqual(len(runs), 10)
        for r in runs:
            self.assertIn("folder", r)
            self.assertIn("strict_pass", r)
            self.assertIn("total", r)

    def test_load_techniques(self):
        techs = load_techniques()
        self.assertEqual(len(techs), 44)
        self.assertIn("T1615", techs)
        self.assertIn("tactics", techs["T1615"])
        self.assertIn("best_verdict", techs["T1615"])

    def test_load_tactic_coverage(self):
        tactics = load_tactic_coverage()
        self.assertGreater(len(tactics), 5)
        for t in tactics:
            self.assertIn("tactic_name", t)
            self.assertIn("coverage_pct", t)

    def test_load_technique_detail(self):
        detail = load_technique_detail("T1615")
        self.assertIsNotNone(detail)
        self.assertEqual(detail["id"], "T1615")
        self.assertIn("events", detail)
        self.assertIn("3", detail["events"])

    def test_load_prompt_comparison(self):
        comp = load_prompt_comparison()
        self.assertGreater(len(comp), 0)


class TestDashboardRoutes(unittest.TestCase):
    """Test Flask web pages and API endpoints."""

    def setUp(self):
        self.client = app.test_client()

    def test_html_pages(self):
        routes = [
            "/",
            "/coverage",
            "/runs",
            "/gate",
            "/pipeline",
            "/technique/T1615",
            "/run/20261111_1500_set3_v3b",
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Page {route} failed")

    def test_json_api_endpoints(self):
        routes = [
            "/api/overview",
            "/api/tactics",
            "/api/techniques",
            "/api/technique/T1615",
            "/api/runs",
            "/api/run/20261111_1500_set3_v3b",
            "/api/comparison",
            "/api/sets",
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Endpoint {route} failed")
            data = res.get_json()
            self.assertIsNotNone(data, f"Endpoint {route} did not return valid JSON")

    def test_gate_api_post(self):
        rule = (
            "title: Gpresult Discovery\n"
            "status: test\n"
            "logsource:\n"
            "    category: process_creation\n"
            "    product: windows\n"
            "detection:\n"
            "    selection:\n"
            "        Image|endswith: '\\gpresult.exe'\n"
            "        CommandLine|contains|windash|all:\n"
            "            - '/z'\n"
            "            - '/user'\n"
            "    condition: selection\n"
            "level: low\n"
        )
        payload = {
            "rule_yaml": rule,
            "set": 3,
            "technique": "T1615",
        }
        res = self.client.post("/api/gate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["verdict"], "PASS")
        self.assertTrue(data["syntax_ok"])
        self.assertTrue(data["fires_shown"])
        self.assertTrue(data["fires_variant"])
        self.assertFalse(data["fires_benign"])


if __name__ == "__main__":
    unittest.main()

