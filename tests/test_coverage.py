"""Tests for ATT&CK coverage template builder."""
import csv
import html.parser
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "coverage"))
from build_coverage import (
    build_coverage_table,
    find_complete_runs,
    format_verdict,
    read_rule_metadata,
    read_techniques_csv,
    select_newest_runs,
    write_csv,
    write_html,
    write_readme,
    ROOT,
)


class TestCoverageFakeRun(unittest.TestCase):
    """Test coverage builder functions with a small isolated fake run folder."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.runs_dir = os.path.join(self.temp_dir, "runs")
        os.makedirs(self.runs_dir)

        # Create fake complete run
        self.fake_run = os.path.join(self.runs_dir, "20261101_1200_set1_v1")
        os.makedirs(self.fake_run)
        settings = {
            "models": ["fake-model:7b"],
            "prompt": "v1",
            "set": 1,
            "repeats": 2,
        }
        with open(os.path.join(self.fake_run, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(settings, f)

        results_header = ["model", "technique", "repeat", "strict_pass", "verdict"]
        results_rows = [
            ["fake-model:7b", "T1059.001", "1", "True", "PASS"],
            ["fake-model:7b", "T1059.001", "2", "True", "PASS"],
            ["fake-model:7b", "T1218.011", "1", "True", "PASS"],
            ["fake-model:7b", "T1218.011", "2", "False", "SYNTAX_ERROR"],
        ]
        with open(os.path.join(self.fake_run, "results.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(results_header)
            writer.writerows(results_rows)

        # Create fake partial run that must be ignored
        self.fake_partial = os.path.join(self.runs_dir, "20261101_1300_set1_v1")
        os.makedirs(self.fake_partial)
        with open(os.path.join(self.fake_partial, "INVALID_PARTIAL.txt"), "w", encoding="utf-8") as f:
            f.write("stalled run")
        with open(os.path.join(self.fake_partial, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(settings, f)
        with open(os.path.join(self.fake_partial, "results.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("model,technique\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_complete_runs_ignores_partial(self):
        runs = find_complete_runs(self.runs_dir)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0][0], "20261101_1200_set1_v1")

    def test_select_newest_runs(self):
        runs = find_complete_runs(self.runs_dir)
        configs = select_newest_runs(runs)
        self.assertIn("fake-model:7b|v1|1", configs)
        folder, settings, rows = configs["fake-model:7b|v1|1"]
        self.assertEqual(len(rows), 4)

    def test_format_verdict(self):
        self.assertEqual(format_verdict([]), "NOT_TESTED")
        self.assertEqual(format_verdict(["PASS"]), "PASS")
        self.assertEqual(format_verdict(["SYNTAX"]), "SYNTAX")
        self.assertEqual(format_verdict(["PASS", "PASS"]), "2/2")
        self.assertEqual(format_verdict(["PASS", "SYNTAX"]), "1/2")
        self.assertEqual(format_verdict(["SYNTAX", "MISSED"]), "0/2")

    def test_write_and_parse_html(self):
        rows = [
            {
                "technique_id": "T1059.001",
                "tactic": "Execution",
                "reference_rule_title": "Test Title",
                "reference_rule_file": "test.yml",
                "reference_rule_status": "PASS",
                "fake-model:7b|v1|1": "2/2",
            }
        ]
        html_path = os.path.join(self.temp_dir, "test.html")
        write_html(rows, ["fake-model:7b|v1|1"], path=html_path)
        self.assertTrue(os.path.exists(html_path))

        class StrictParser(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.tag_count = 0

            def handle_starttag(self, tag, attrs):
                self.tag_count += 1

        parser = StrictParser()
        with open(html_path, encoding="utf-8") as f:
            parser.feed(f.read())
        self.assertGreater(parser.tag_count, 10)


class TestCoverageRealData(unittest.TestCase):
    """Test coverage output against actual repository data and rules."""

    def test_rows_count(self):
        rows, config_keys, _ = build_coverage_table()
        runs = find_complete_runs()
        sets_with_runs = {s.get("set") for _, s, _ in runs}
        if 3 in sets_with_runs:
            self.assertEqual(len(rows), 44, f"Expected 44 rows with set 3, got {len(rows)}")
        else:
            self.assertEqual(len(rows), 24, f"Expected exactly 24 rows, got {len(rows)}")

    def test_set_3_results_consistency(self):
        rows, config_keys, _ = build_coverage_table()
        runs = find_complete_runs()
        sets_with_runs = {s.get("set") for _, s, _ in runs}
        if 3 in sets_with_runs:
            has_set3 = any(row["technique_id"].startswith("T1003.002") for row in rows)
            self.assertTrue(has_set3, "Set 3 techniques should be present now that set 3 was run")
        else:
            for row in rows:
                self.assertFalse(row["technique_id"].startswith("T1003.002"),
                                "Set 3 technique should not be present")
            for ck in config_keys:
                self.assertFalse(ck.endswith("|3"),
                                f"Configuration {ck} should not be for set 3")

    def test_all_set1_and_set2_techniques_present(self):
        rows, _, _ = build_coverage_table()
        tech_ids = {r["technique_id"] for r in rows}
        set1_csv = os.path.join(ROOT, "results", "techniques.csv")
        set2_csv = os.path.join(ROOT, "results", "techniques_set2.csv")
        s1 = [r["technique"] for r in read_techniques_csv(set1_csv)]
        s2 = [r["technique"] for r in read_techniques_csv(set2_csv)]
        for t in s1:
            self.assertIn(t, tech_ids, f"Set 1 technique {t} missing")
        for t in s2:
            self.assertIn(t, tech_ids, f"Set 2 technique {t} missing")

    def test_html_parses_without_error(self):
        html_path = os.path.join(ROOT, "coverage", "coverage.html")
        self.assertTrue(os.path.exists(html_path))

        class ValidatingParser(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.errors = []

            def error(self, message):
                self.errors.append(message)

        parser = ValidatingParser()
        with open(html_path, encoding="utf-8") as f:
            parser.feed(f.read())
        self.assertEqual(len(parser.errors), 0)

    def test_totals_match_results_summary(self):
        rows, config_keys, config_summaries = build_coverage_table()
        # Verify strict pass totals match RESULTS_SUMMARY.md and Set 3 final report
        expected_passes = {
            "qwen2.5-coder:7b|v1|1": 7,
            "qwen2.5-coder:14b|v1|1": 3,
            "qwen2.5-coder:7b|v2|1": 9,
            "qwen2.5-coder:14b|v2|1": 8,
            "qwen2.5-coder:7b|v2_1|1": 11,
            "qwen2.5-coder:14b|v2_1|1": 8,
            "qwen2.5-coder:7b|v3a|1": 16,
            "qwen2.5-coder:14b|v3a|1": 19,
            "qwen2.5-coder:7b|v3b|1": 15,
            "qwen2.5-coder:14b|v3b|1": 21,
            "qwen2.5-coder:7b|v1|2": 2,
            "qwen2.5-coder:14b|v1|2": 2,
            "mistral-rules|v1|2": 0,
            "qwen2.5-coder:7b|v1|3": 35,
            "qwen2.5-coder:14b|v1|3": 47,
            "qwen2.5-coder:7b|v3a|3": 58,
            "qwen2.5-coder:14b|v3a|3": 55,
            "qwen2.5-coder:7b|v3b|3": 54,
            "qwen2.5-coder:14b|v3b|3": 57,
        }
        for ck, expected in expected_passes.items():
            self.assertIn(ck, config_summaries, f"Config {ck} not found")
            actual = config_summaries[ck]["passes"]
            self.assertEqual(actual, expected,
                             f"Config {ck}: expected {expected} passes, got {actual}")

    def test_set2_baseline_numbers(self):
        rows, config_keys, config_summaries = build_coverage_table()
        self.assertIn("qwen2.5-coder:7b|v1|2", config_summaries)
        self.assertEqual(config_summaries["qwen2.5-coder:7b|v1|2"]["passes"], 2)
        self.assertEqual(config_summaries["qwen2.5-coder:7b|v1|2"]["attempts"], 12)

        self.assertIn("qwen2.5-coder:14b|v1|2", config_summaries)
        self.assertEqual(config_summaries["qwen2.5-coder:14b|v1|2"]["passes"], 2)
        self.assertEqual(config_summaries["qwen2.5-coder:14b|v1|2"]["attempts"], 12)

        self.assertIn("mistral-rules|v1|2", config_summaries)
        self.assertEqual(config_summaries["mistral-rules|v1|2"]["passes"], 0)
        self.assertEqual(config_summaries["mistral-rules|v1|2"]["attempts"], 12)

    def test_dynamic_header_in_html(self):
        html_path = os.path.join(ROOT, "coverage", "coverage.html")
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("has not been run", content)
        self.assertIn("sets 1, 2, and 3", content)
        self.assertIn("Sets with results:", content)

    def test_no_all_not_tested_rows(self):
        rows, config_keys, _ = build_coverage_table()
        for r in rows:
            tech = r["technique_id"]
            verdicts = [r.get(ck) for ck in config_keys]
            has_tested = any(v != "NOT_TESTED" for v in verdicts)
            self.assertTrue(has_tested, f"Technique {tech} has NOT_TESTED in all columns")

    def test_multi_tactic_metadata(self):
        # T1033 has Privilege Escalation and Discovery
        rule_p = os.path.join(ROOT, "data", "sigmahq_rules", "proc_creation_win_whoami_priv_discovery.yml")
        _, tactic = read_rule_metadata(rule_p)
        self.assertIn(";", tactic)
        self.assertIn("Privilege Escalation", tactic)
        self.assertIn("Discovery", tactic)

        # T1003.001 has Defense Evasion and Credential Access
        rule_p2 = os.path.join(ROOT, "data", "sigmahq_rules", "proc_creation_win_sysinternals_procdump_lsass.yml")
        _, tactic2 = read_rule_metadata(rule_p2)
        self.assertIn(";", tactic2)
        self.assertIn("Defense Evasion", tactic2)
        self.assertIn("Credential Access", tactic2)


if __name__ == "__main__":
    unittest.main()

