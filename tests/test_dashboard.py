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
            "/app",
            "/app/",
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
        self.assertIn("reason", data)

    def test_gate_api_noisy(self):
        rule = (
            "title: Overly Broad Reg Add\n"
            "status: test\n"
            "logsource:\n"
            "    category: process_creation\n"
            "    product: windows\n"
            "detection:\n"
            "    selection:\n"
            "        Image|endswith: '\\reg.exe'\n"
            "        CommandLine|contains: 'add'\n"
            "    condition: selection\n"
            "level: low\n"
        )
        payload = {
            "rule_yaml": rule,
            "set": 1,
            "technique": "T1547.001",
        }
        res = self.client.post("/api/gate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["verdict"], "NOISY")
        self.assertTrue(data["fires_benign"])
        self.assertIn("reason", data)

    def test_gate_api_syntax_error(self):
        rule = "invalid: yaml: [syntax error"
        payload = {
            "rule_yaml": rule,
            "set": 3,
            "technique": "T1615",
        }
        res = self.client.post("/api/gate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["verdict"], "SYNTAX_ERROR")
        self.assertFalse(data["syntax_ok"])
        self.assertIn("reason", data)

    def test_pipeline_run_endpoint(self):
        text = "The attacker executed reg.exe add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Updater /d C:\\Users\\student\\x.exe to establish persistence."
        res = self.client.post("/api/pipeline/run", json={"text": text})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["technique_id"], "T1547.001")
        self.assertIn("reg.exe", data["extracted_command"])
        self.assertIn("rule_yaml", data)
        self.assertIn("verdict", data)
        self.assertIn("model", data)

    def test_pipeline_legacy_endpoint(self):
        text = "During lateral movement net.exe use \\\\10.0.0.5\\C$ /user:admin Passw0rd was executed."
        res = self.client.post("/api/pipeline", json={"report_text": text})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["technique_id"], "T1021.002")
        self.assertIn("net", data["extracted_command"].lower())
        self.assertIn("rule_yaml", data)


    def test_export_api_splunk(self):
        rule = (
            "title: Test Export\n"
            "status: test\n"
            "logsource:\n"
            "    category: process_creation\n"
            "    product: windows\n"
            "detection:\n"
            "    selection:\n"
            "        Image|endswith: '\\\\whoami.exe'\n"
            "        CommandLine|contains: '/priv'\n"
            "    condition: selection\n"
        )
        res = self.client.post("/api/export", json={"rule_yaml": rule, "format": "splunk"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["format"], "splunk")
        self.assertIn("CommandLine", data["result"])

    def test_export_api_kql(self):
        rule = (
            "title: Test Export KQL\n"
            "status: test\n"
            "logsource:\n"
            "    category: process_creation\n"
            "    product: windows\n"
            "detection:\n"
            "    selection:\n"
            "        Image|endswith: '\\\\whoami.exe'\n"
            "        CommandLine|contains: '/priv'\n"
            "    condition: selection\n"
        )
        res = self.client.post("/api/export", json={"rule_yaml": rule, "format": "kql"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["format"], "kql")
        self.assertIn("CommandLine", data["result"])

    def test_export_api_all_formats(self):
        rule = (
            "title: Test All Formats\n"
            "status: test\n"
            "logsource:\n"
            "    category: process_creation\n"
            "    product: windows\n"
            "detection:\n"
            "    selection:\n"
            "        Image|endswith: '\\\\whoami.exe'\n"
            "    condition: selection\n"
        )
        res = self.client.post("/api/export", json={"rule_yaml": rule, "format": "all"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("formats", data)
        self.assertIn("splunk", data["formats"])
        self.assertIn("kql", data["formats"])
        self.assertIn("sqlite", data["formats"])
        self.assertIn("sigma", data["formats"])

    def test_export_api_bad_format(self):
        rule = "title: T\nstatus: test\nlogsource:\n    category: process_creation\n    product: windows\ndetection:\n    sel:\n        Image: x\n    condition: sel\n"
        res = self.client.post("/api/export", json={"rule_yaml": rule, "format": "nosuchformat"})
        self.assertEqual(res.status_code, 400)

    def test_export_api_missing_rule(self):
        res = self.client.post("/api/export", json={"format": "splunk"})
        self.assertEqual(res.status_code, 400)

    def test_export_formats_endpoint(self):
        res = self.client.get("/api/export/formats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("splunk", data)
        self.assertIn("kql", data)


if __name__ == "__main__":
    unittest.main()

