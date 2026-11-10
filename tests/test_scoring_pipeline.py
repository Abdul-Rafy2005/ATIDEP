"""
Tests for scoring pipeline through the real run_experiment.py path using mocked Ollama.
Verifies that results.csv and summary.md produced by run_experiment.py contain the correct verdicts.
Ensures the real results/ folder is never touched.
"""
import csv
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "validator"))
sys.path.insert(0, os.path.join(REPO_ROOT, "generator"))
sys.path.insert(0, os.path.join(REPO_ROOT, "llm"))

from generate import make_triple as make_triple_set1, TECHNIQUES
from techniques_set2 import make_triple as make_triple_set2, TECHNIQUES2
from techniques_set3 import make_triple3 as make_triple_set3, TECHNIQUES3
import run_experiment


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def copy_rule(shown_event):
    program = shown_event["Image"].split("\\")[-1]
    command = shown_event["CommandLine"].replace("\\", "\\\\")
    return (
        "title: copy\nstatus: test\nlogsource:\n  category: process_creation\n"
        "  product: windows\ndetection:\n  selection:\n"
        f"    Image|endswith: {quote('\\' + program)}\n"
        f"    CommandLine|contains: {quote(command)}\n"
        "  condition: selection\nlevel: low\ntags: []\n"
    )


BROKEN_YAML_RULE = "title: broken\nstatus: test\nlogsource:\n  category: process_creation\n  product: windows\ndetection:\n  selection:\n    CommandLine: [unterminated\n"

NEVER_FIRE_RULE = """title: never fire
status: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    CommandLine|contains: 'NONEXISTENT_NEVER_FIRE_TOKEN_XYZ_12345'
  condition: selection
level: low
tags: []
"""

ALWAYS_FIRE_RULE = """title: always fire
status: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    CommandLine|contains: '.exe'
  condition: selection
level: low
tags: []
"""

SET1_KEYWORD_RULES = {
    "T1059.001": "DownloadString",
    "T1218.011": ".sys,",
    "T1218.005": "javascript",
    "T1218.010": "scrobj",
    "T1105": "urlcache",
    "T1053.005": "\\Temp\\",
    "T1547.001": "CurrentVersion\\Run",
    "T1136.001": "/add",
    "T1003.001": "lsass",
    "T1197": "/transfer",
    "T1047": "process call create",
    "T1033": "priv",
}


class TestScoringPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="atidep_pipe_test_")
        # Ensure real set2_use_log and set3_use_log do not exist beforehand
        self.real_set2_log = os.path.join(REPO_ROOT, "results", "set2_use_log.csv")
        self.real_set3_log = os.path.join(REPO_ROOT, "results", "set3_use_log.csv")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(os.path.exists(self.real_set2_log), "Real set2_use_log.csv was touched!")
        self.assertFalse(os.path.exists(self.real_set3_log), "Real set3_use_log.csv was touched!")

    def _run_pipeline(self, set_id, mock_rule_fn, prompt="v2"):
        """Run run_experiment.main with patched ask and custom results-dir."""
        def fake_ask(url, model, prompt_text, max_tokens, temperature=0, seed=None):
            # Extract technique ID from prompt_text (the last Technique: line is the target)
            techs = [line.split(":", 1)[1].strip() for line in prompt_text.splitlines() if line.startswith("Technique:")]
            tech = techs[-1] if techs else None
            rule = mock_rule_fn(tech)
            return rule, 0.05, 50.0, "stop", 25

        args = [
            "--set", str(set_id),
            "--prompt", prompt,
            "--models", "qwen2.5-coder:7b",
            "--repeats", "1",
            "--results-dir", self.temp_dir,
        ]
        if set_id == 2:
            args.extend(["--allow-validation-set", "--reason", "pipeline test set 2"])
        elif set_id == 3:
            args.extend(["--final", "--reason", "pipeline test set 3"])

        with patch("run_experiment.ask", side_effect=fake_ask), \
             patch("run_experiment.tags", return_value=[{"name": "qwen2.5-coder:7b", "digest": "dae161e27b0e"}]), \
             patch("run_experiment.command_output", return_value="mocked"):
            code = run_experiment.main(args)
            self.assertEqual(code, 0)

        # Locate run folder inside temp_dir
        runs_dir = os.path.join(self.temp_dir, "runs")
        run_folders = os.listdir(runs_dir)
        self.assertEqual(len(run_folders), 1)
        folder = os.path.join(runs_dir, run_folders[0])

        with open(os.path.join(folder, "results.csv"), encoding="utf-8") as f:
            results_rows = list(csv.DictReader(f))
        with open(os.path.join(folder, "summary.md"), encoding="utf-8") as f:
            summary_content = f.read()

        return results_rows, summary_content

    # -------------------------------------------------------------------------
    # SET 1
    # -------------------------------------------------------------------------
    def test_pipeline_set1_copy_rules_too_narrow(self):
        def rule_fn(tech):
            shown, _, _ = make_triple_set1(tech)
            return copy_rule(shown)

        rows, summary = self._run_pipeline(1, rule_fn)
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertEqual(row["single_pass"], "True", f"{row['technique']} single_pass not True")
            self.assertEqual(row["strict_pass"], "False", f"{row['technique']} strict_pass not False")
            self.assertEqual(row["verdict"], "TOO_NARROW", f"{row['technique']} verdict not TOO_NARROW")
        self.assertIn("| 12 | 0 | TOO_NARROW=12 |", summary)

    def test_pipeline_set1_broken_yaml(self):
        rows, _ = self._run_pipeline(1, lambda tech: BROKEN_YAML_RULE)
        for row in rows:
            self.assertEqual(row["verdict"], "SYNTAX_ERROR")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set1_never_fires(self):
        rows, _ = self._run_pipeline(1, lambda tech: NEVER_FIRE_RULE)
        for row in rows:
            self.assertEqual(row["verdict"], "MISSED_SHOWN")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set1_always_fires_noisy(self):
        rows, _ = self._run_pipeline(1, lambda tech: ALWAYS_FIRE_RULE)
        for row in rows:
            self.assertEqual(row["verdict"], "NOISY")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set1_keywords_pass(self):
        def rule_fn(tech):
            kw = SET1_KEYWORD_RULES[tech].replace("\\", "\\\\")
            return f"""title: Keyword {tech}
status: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    CommandLine|contains: '{kw}'
  condition: selection
level: low
tags: []
"""

        rows, summary = self._run_pipeline(1, rule_fn)
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertEqual(row["single_pass"], "True", f"{row['technique']} single_pass not True")
            self.assertEqual(row["strict_pass"], "True", f"{row['technique']} strict_pass not True")
            self.assertEqual(row["verdict"], "PASS", f"{row['technique']} verdict not PASS")
        self.assertIn("| 12 | 12 | PASS=12 |", summary)

    # -------------------------------------------------------------------------
    # SET 2
    # -------------------------------------------------------------------------
    def test_pipeline_set2_copy_rules_too_narrow(self):
        def rule_fn(tech):
            shown, _, _ = make_triple_set2(tech)
            return copy_rule(shown)

        rows, summary = self._run_pipeline(2, rule_fn, prompt="v1")
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertEqual(row["single_pass"], "True", f"{row['technique']} single_pass not True")
            self.assertEqual(row["strict_pass"], "False", f"{row['technique']} strict_pass not False")
            self.assertEqual(row["verdict"], "TOO_NARROW", f"{row['technique']} verdict not TOO_NARROW")
        self.assertIn("| 12 | 0 | TOO_NARROW=12 |", summary)

    def test_pipeline_set2_broken_yaml(self):
        rows, _ = self._run_pipeline(2, lambda tech: BROKEN_YAML_RULE, prompt="v1")
        for row in rows:
            self.assertEqual(row["verdict"], "SYNTAX_ERROR")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set2_never_fires(self):
        rows, _ = self._run_pipeline(2, lambda tech: NEVER_FIRE_RULE, prompt="v1")
        for row in rows:
            self.assertEqual(row["verdict"], "MISSED_SHOWN")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set2_always_fires_noisy(self):
        rows, _ = self._run_pipeline(2, lambda tech: ALWAYS_FIRE_RULE, prompt="v1")
        for row in rows:
            self.assertEqual(row["verdict"], "NOISY")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    # -------------------------------------------------------------------------
    # SET 3
    # -------------------------------------------------------------------------
    def test_pipeline_set3_copy_rules_too_narrow(self):
        def rule_fn(tech):
            shown, _, _ = make_triple_set3(tech)
            return copy_rule(shown)

        rows, summary = self._run_pipeline(3, rule_fn, prompt="v2")
        self.assertEqual(len(rows), 20)
        for row in rows:
            self.assertEqual(row["single_pass"], "True", f"{row['technique']} single_pass not True")
            self.assertEqual(row["strict_pass"], "False", f"{row['technique']} strict_pass not False")
            self.assertEqual(row["verdict"], "TOO_NARROW", f"{row['technique']} verdict not TOO_NARROW")
        self.assertIn("| 20 | 0 | TOO_NARROW=20 |", summary)

    def test_pipeline_set3_broken_yaml(self):
        rows, _ = self._run_pipeline(3, lambda tech: BROKEN_YAML_RULE, prompt="v2")
        for row in rows:
            self.assertEqual(row["verdict"], "SYNTAX_ERROR")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set3_never_fires(self):
        rows, _ = self._run_pipeline(3, lambda tech: NEVER_FIRE_RULE, prompt="v2")
        for row in rows:
            self.assertEqual(row["verdict"], "MISSED_SHOWN")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")

    def test_pipeline_set3_always_fires_noisy(self):
        rows, _ = self._run_pipeline(3, lambda tech: ALWAYS_FIRE_RULE, prompt="v2")
        for row in rows:
            self.assertEqual(row["verdict"], "NOISY")
            self.assertEqual(row["single_pass"], "False")
            self.assertEqual(row["strict_pass"], "False")


if __name__ == "__main__":
    unittest.main()
