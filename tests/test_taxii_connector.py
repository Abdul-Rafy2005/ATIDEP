"""Tests for data/taxii_connector.py. No network is used."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data"))

import taxii_connector  # noqa: E402


def _pattern(tid, name="Name"):
    return {
        "type": "attack-pattern",
        "name": name,
        "external_references": [
            {"source_name": "mitre-attack", "external_id": tid, "url": "u"}
        ],
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
        ],
    }


class TestTaxiiConnector(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.lookup = os.path.join(self.tmp, "attack_lookup.json")
        self.fetched = os.path.join(self.tmp, "fetched.json")
        with open(self.lookup, "w", encoding="utf-8") as f:
            json.dump({"T0000": {"name": "old", "tactics": [], "url": ""}}, f)
        p1 = mock.patch.object(taxii_connector, "LOOKUP_PATH", self.lookup)
        p2 = mock.patch.object(taxii_connector, "FETCHED_PATH", self.fetched)
        p1.start()
        p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _lookup_text(self):
        with open(self.lookup, encoding="utf-8") as f:
            return f.read()

    def test_server_down_keeps_local_lookup(self):
        before = self._lookup_text()
        with mock.patch.object(
            taxii_connector, "fetch_objects", side_effect=OSError("no network")
        ), mock.patch.object(sys, "argv", ["taxii_connector.py"]):
            self.assertEqual(taxii_connector.main(), 1)
        self.assertEqual(self._lookup_text(), before)

    def test_too_few_techniques_is_rejected(self):
        before = self._lookup_text()
        with self.assertRaises(RuntimeError):
            taxii_connector.update_lookup([_pattern("T1001")])
        self.assertEqual(self._lookup_text(), before)

    def test_good_result_updates_lookup(self):
        objs = [_pattern(f"T{2000 + i}") for i in range(taxii_connector.MIN_TECHNIQUES)]
        new, old = taxii_connector.update_lookup(objs)
        self.assertEqual(len(new), taxii_connector.MIN_TECHNIQUES)
        self.assertIn("T0000", old)
        self.assertEqual(len(json.loads(self._lookup_text())), len(new))

    def test_check_mode_writes_nothing(self):
        before = self._lookup_text()
        objs = [_pattern(f"T{2000 + i}") for i in range(taxii_connector.MIN_TECHNIQUES)]
        taxii_connector.update_lookup(objs, write=False)
        self.assertEqual(self._lookup_text(), before)


if __name__ == "__main__":
    unittest.main()
