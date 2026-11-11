"""Unit tests for ATIDEP End-to-End Demo using mocked Ollama responses."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
DEMO_DIR = os.path.join(ROOT_DIR, "demo")
if DEMO_DIR not in sys.path:
    sys.path.insert(0, DEMO_DIR)

from demo import (
    load_supported_techniques,
    read_frozen_config,
    parse_extraction_json,
    evaluate_gate,
    run_demo,
)


VALID_RULE_YAML = """title: Persistence via Run Keys
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\reg.exe'
        CommandLine|contains|all:
            - 'add'
            - '\\CurrentVersion\\Run'
    condition: selection
level: high
tags:
    - attack.persistence
    - attack.t1547.001
"""

SYNTAX_ERROR_YAML = """title: Broken Rule
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\reg.exe'
    condition: selection and (unterminated
level: high
"""


class TestDemoMocked(unittest.TestCase):
    """Test demo pipeline under mocked Ollama responses."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        self.supported = load_supported_techniques()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_frozen_config(self):
        config = read_frozen_config()
        self.assertEqual(config["model"], "qwen2.5-coder:14b")
        self.assertEqual(config["prompt_version"], "v3b")
        self.assertEqual(config["seed"], 100)

    def test_load_supported_techniques(self):
        # 12 from set 1 and 12 from set 2 = 24 techniques
        self.assertEqual(len(self.supported), 24)
        self.assertIn("T1547.001", self.supported)
        self.assertIn("T1021.002", self.supported)

    def test_parse_extraction_json(self):
        # Plain json
        d1 = parse_extraction_json('{"technique": "T1547.001", "command_line": "reg.exe add"}')
        self.assertEqual(d1.get("technique"), "T1547.001")

        # In markdown block
        d2 = parse_extraction_json('```json\n{"technique": "T1003.001", "command_line": "procdump.exe -ma lsass.exe"}\n```')
        self.assertEqual(d2.get("technique"), "T1003.001")

        # With thoughts
        d3 = parse_extraction_json('<think>some thought</think>{"technique": "T1047", "command_line": "wmic.exe"}')
        self.assertEqual(d3.get("technique"), "T1047")

    def test_evaluate_gate_pass(self):
        tech_info = self.supported["T1547.001"]
        verdict, reason, sql = evaluate_gate(
            VALID_RULE_YAML,
            "T1547.001",
            r"reg.exe add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Updater /d C:\Users\student\x.exe",
            tech_info,
        )
        self.assertEqual(verdict, "PASS")
        self.assertIn("quiet on benign", reason)

    def test_evaluate_gate_bad_syntax(self):
        tech_info = self.supported["T1547.001"]
        verdict, reason, sql = evaluate_gate(
            SYNTAX_ERROR_YAML,
            "T1547.001",
            "reg.exe add",
            tech_info,
        )
        self.assertEqual(verdict, "FAIL")
        self.assertIn("Syntax error", reason)

    @patch("demo.call_ollama")
    def test_demo_success(self, mock_call):
        # Mock step 1: extraction JSON
        # Mock step 2: rule YAML
        mock_call.side_effect = [
            ('{"technique": "T1547.001", "command_line": "reg.exe add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run /v Updater /d C:\\\\Users\\\\student\\\\x.exe"}', 0.5),
            (VALID_RULE_YAML, 1.2),
        ]
        sample_text = "Adversary ran: reg.exe add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Updater /d C:\\Users\\student\\x.exe to persist."
        result = run_demo(sample_text, output_dir=self.output_dir)

        self.assertIsNotNone(result)
        self.assertEqual(result["technique"], "T1547.001")
        self.assertEqual(result["gate_verdict"], "PASS")

        # Verify json and yml files saved
        files = os.listdir(self.output_dir)
        json_files = [f for f in files if f.endswith(".json")]
        yml_files = [f for f in files if f.endswith(".yml")]
        self.assertEqual(len(json_files), 1)
        self.assertEqual(len(yml_files), 1)

    @patch("demo.call_ollama")
    def test_demo_wrong_technique(self, mock_call):
        # Model returns an unsupported technique ID
        mock_call.side_effect = [
            ('{"technique": "T9999", "command_line": "some command"}', 0.4),
        ]
        sample_text = "Adversary ran some command in network."
        with self.assertRaises(SystemExit) as cm:
            run_demo(sample_text, output_dir=self.output_dir)
        self.assertEqual(cm.exception.code, 2)

    @patch("demo.call_ollama")
    def test_demo_command_line_not_in_text(self, mock_call):
        # Model returns a valid technique, but a hallucinated command line not in text
        mock_call.side_effect = [
            ('{"technique": "T1547.001", "command_line": "reg.exe add HKLM\\\\Run /v Malware /d C:\\\\bad.exe"}', 0.4),
        ]
        sample_text = "The attacker used registry persistence but the details were not specified."
        with self.assertRaises(SystemExit) as cm:
            run_demo(sample_text, output_dir=self.output_dir)
        self.assertEqual(cm.exception.code, 2)

    @patch("demo.call_ollama")
    def test_demo_bad_yaml_fails_gate(self, mock_call):
        # Model extracts correctly, but generates invalid YAML
        mock_call.side_effect = [
            ('{"technique": "T1547.001", "command_line": "reg.exe add"}', 0.4),
            (SYNTAX_ERROR_YAML, 1.0),
        ]
        sample_text = "Attacker invoked: reg.exe add"
        result = run_demo(sample_text, output_dir=self.output_dir)

        self.assertIsNotNone(result)
        self.assertEqual(result["gate_verdict"], "FAIL")
        self.assertIn("Syntax error", result["gate_reason"])

        # Output json and yml should still be saved even on gate failure
        files = os.listdir(self.output_dir)
        json_files = [f for f in files if f.endswith(".json")]
        yml_files = [f for f in files if f.endswith(".yml")]
        self.assertEqual(len(json_files), 1)
        self.assertEqual(len(yml_files), 1)


if __name__ == "__main__":
    unittest.main()
