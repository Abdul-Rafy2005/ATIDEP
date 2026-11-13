"""Tests for demo/gate_demo.py and sample rules."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "demo"))

from gate_demo import run_gate_demo, load_technique_triple


class TestGateDemo(unittest.TestCase):
    """Test gate demonstration script and four sample rules."""

    def test_rule_a_pass(self):
        rule_path = os.path.join(ROOT, "demo", "sample_rules", "rule_a_pass.yml")
        res = run_gate_demo(rule_path, 3, "T1615")
        self.assertEqual(res.verdict, "PASS")
        self.assertTrue(res.syntax_ok)
        self.assertTrue(res.fires_shown)
        self.assertTrue(res.fires_variant)
        self.assertFalse(res.fires_benign)

    def test_rule_b_narrow_padded(self):
        rule_path = os.path.join(ROOT, "demo", "sample_rules", "rule_b_narrow_padded.yml")
        res = run_gate_demo(rule_path, 3, "T1564.004")
        self.assertEqual(res.verdict, "TOO_NARROW")
        self.assertTrue(res.syntax_ok)
        self.assertTrue(res.fires_shown)
        self.assertFalse(res.fires_variant)
        self.assertFalse(res.fires_benign)

    def test_rule_c_narrow_copy(self):
        rule_path = os.path.join(ROOT, "demo", "sample_rules", "rule_c_narrow_copy.yml")
        res = run_gate_demo(rule_path, 3, "T1220")
        self.assertEqual(res.verdict, "TOO_NARROW")
        self.assertTrue(res.syntax_ok)
        self.assertTrue(res.fires_shown)
        self.assertFalse(res.fires_variant)
        self.assertFalse(res.fires_benign)

    def test_rule_d_syntax_error(self):
        rule_path = os.path.join(ROOT, "demo", "sample_rules", "rule_d_syntax_error.yml")
        res = run_gate_demo(rule_path, 3, "T1529")
        self.assertEqual(res.verdict, "SYNTAX_ERROR")
        self.assertFalse(res.syntax_ok)
        self.assertIn("Unsupported type", res.error)

    def test_results_directory_unchanged(self):
        """Ensure running gate_demo leaves results/ directory untouched."""
        results_dir = os.path.join(ROOT, "results")
        snapshot_before = {}
        for root_path, _, files in os.walk(results_dir):
            for fn in files:
                full_p = os.path.join(root_path, fn)
                snapshot_before[full_p] = os.path.getmtime(full_p)

        # Run on all sample rules
        samples = [
            ("rule_a_pass.yml", 3, "T1615"),
            ("rule_b_narrow_padded.yml", 3, "T1564.004"),
            ("rule_c_narrow_copy.yml", 3, "T1220"),
            ("rule_d_syntax_error.yml", 3, "T1529"),
        ]
        for fn, s, t in samples:
            p = os.path.join(ROOT, "demo", "sample_rules", fn)
            run_gate_demo(p, s, t)

        snapshot_after = {}
        for root_path, _, files in os.walk(results_dir):
            for fn in files:
                full_p = os.path.join(root_path, fn)
                snapshot_after[full_p] = os.path.getmtime(full_p)

        self.assertEqual(
            snapshot_before,
            snapshot_after,
            "Files in results/ were modified or created during gate_demo execution",
        )


if __name__ == "__main__":
    unittest.main()

