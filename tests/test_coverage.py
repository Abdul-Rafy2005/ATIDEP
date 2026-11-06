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

    def test_24_rows_for_sets_1_and_2(self):
        rows, config_keys, _ = build_coverage_table()
        self.assertEqual(len(rows), 24, f"Expected exactly 24 rows, got {len(rows)}")

    def test_no_set_3_results_shown(self):
        rows, config_keys, _ = build_coverage_table()
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
        # Verify strict pass totals match RESULTS_SUMMARY.md
        expected_passes = {
            "qwen2.5-coder:7b|v1|1": 28,
            "qwen2.5-coder:14b|v1|1": 35,
            "qwen2.5-coder:7b|v2|1": 36,
            "qwen2.5-coder:14b|v2|1": 26,
            "qwen2.5-coder:7b|v2_1|1": 36,
            "qwen2.5-coder:14b|v2_1|1": 36,
        }
        for ck, expected in expected_passes.items():
            self.assertIn(ck, config_summaries, f"Config {ck} not found")
            actual = config_summaries[ck]["passes"]
            self.assertEqual(actual, expected,
                             f"Config {ck}: expected {expected} passes, got {actual}")


if __name__ == "__main__":
    unittest.main()

