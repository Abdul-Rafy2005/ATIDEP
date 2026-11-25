"""Tests for the IOC extraction module."""

import sys
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from export.ioc_extract import extract_iocs, has_iocs, _refang


class TestRefang(unittest.TestCase):
    def test_hxxp(self):
        self.assertEqual(_refang("hxxp://evil.com"), "http://evil.com")

    def test_hxxps(self):
        self.assertEqual(_refang("hxxps://evil.com"), "https://evil.com")

    def test_defanged_dot(self):
        self.assertEqual(_refang("evil[.]com"), "evil.com")

    def test_defanged_dot_word(self):
        self.assertEqual(_refang("evil[dot]com"), "evil.com")

    def test_defanged_colon(self):
        self.assertEqual(_refang("http[:]//evil.com"), "http://evil.com")


class TestIPv4Extraction(unittest.TestCase):
    def test_basic_ip(self):
        result = extract_iocs("The server at 10.0.0.5 was compromised.")
        self.assertIn("10.0.0.5", result["ipv4"])

    def test_multiple_ips(self):
        result = extract_iocs("Traffic from 192.168.1.10 to 10.20.30.40.")
        self.assertEqual(len(result["ipv4"]), 2)

    def test_defanged_ip(self):
        result = extract_iocs("C2 at 192.168.1[.]100 was active.")
        self.assertIn("192.168.1.100", result["ipv4"])

    def test_loopback_excluded(self):
        result = extract_iocs("Listening on 127.0.0.1 and 10.0.0.1.")
        self.assertNotIn("127.0.0.1", result["ipv4"])
        self.assertIn("10.0.0.1", result["ipv4"])

    def test_dedup(self):
        result = extract_iocs("10.0.0.5 connected to 10.0.0.5 again.")
        self.assertEqual(result["ipv4"].count("10.0.0.5"), 1)


class TestDomainExtraction(unittest.TestCase):
    def test_basic_domain(self):
        result = extract_iocs("The beacon called home to malware-c2.evil.com.")
        self.assertIn("malware-c2.evil.com", result["domains"])

    def test_defanged_domain(self):
        result = extract_iocs("Callback to evil[.]xyz observed.")
        self.assertIn("evil.xyz", result["domains"])

    def test_common_fp_excluded(self):
        result = extract_iocs("See https://attack.mitre.org/techniques/T1059.")
        self.assertNotIn("attack.mitre.org", result["domains"])

    def test_domain_from_url_not_duplicated(self):
        result = extract_iocs("Downloaded from http://dropper.net/payload.exe.")
        # dropper.net should be in URLs but not separately in domains
        self.assertTrue(any("dropper.net" in u for u in result["urls"]))
        self.assertNotIn("dropper.net", result["domains"])


class TestURLExtraction(unittest.TestCase):
    def test_basic_url(self):
        result = extract_iocs("Payload at http://evil.com/malware.exe was fetched.")
        self.assertTrue(any("evil.com/malware.exe" in u for u in result["urls"]))

    def test_https_url(self):
        result = extract_iocs("Beaconing to https://c2.bad.org/api/check.")
        self.assertTrue(any("c2.bad.org" in u for u in result["urls"]))

    def test_defanged_url(self):
        result = extract_iocs("Stage 2 from hxxp://malware-c2.evil.xyz/stage2.bin.")
        self.assertTrue(any("malware-c2.evil.xyz" in u for u in result["urls"]))


class TestHashExtraction(unittest.TestCase):
    def test_md5(self):
        result = extract_iocs("MD5: d41d8cd98f00b204e9800998ecf8427e found in memory.")
        self.assertEqual(len(result["hashes"]), 1)
        self.assertEqual(result["hashes"][0]["type"], "md5")
        self.assertEqual(result["hashes"][0]["value"], "d41d8cd98f00b204e9800998ecf8427e")

    def test_sha1(self):
        result = extract_iocs("SHA1: da39a3ee5e6b4b0d3255bfef95601890afd80709 on disk.")
        self.assertEqual(len(result["hashes"]), 1)
        self.assertEqual(result["hashes"][0]["type"], "sha1")

    def test_sha256(self):
        h = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        result = extract_iocs(f"SHA256: {h}.")
        self.assertEqual(len(result["hashes"]), 1)
        self.assertEqual(result["hashes"][0]["type"], "sha256")
        self.assertEqual(result["hashes"][0]["value"], h)

    def test_sha256_not_also_md5(self):
        h = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        result = extract_iocs(f"Hash: {h}.")
        # Should only appear once as sha256, not also as md5 substring
        self.assertEqual(len(result["hashes"]), 1)
        self.assertEqual(result["hashes"][0]["type"], "sha256")


class TestHasIocs(unittest.TestCase):
    def test_empty(self):
        result = extract_iocs("No indicators here, just plain text about attacks.")
        self.assertFalse(has_iocs(result))

    def test_with_ip(self):
        result = extract_iocs("Connected to 10.0.0.5.")
        self.assertTrue(has_iocs(result))

    def test_with_hash(self):
        result = extract_iocs("MD5: d41d8cd98f00b204e9800998ecf8427e.")
        self.assertTrue(has_iocs(result))


class TestMixedReport(unittest.TestCase):
    def test_realistic_report(self):
        text = (
            "The attacker used net.exe use \\\\10.0.0.5\\C$ /user:admin Passw0rd "
            "to access the share. The payload (SHA256: "
            "7b3a9f2e1d4c5a8b6e0f3d2c1a9b8e7f6d5c4a3b2e1f0d9c8b7a6f5e4d3c2b1a) "
            "was downloaded from hxxp://malware-c2.evil.xyz/stage2.bin and "
            "beaconed to 192.168.44.100."
        )
        result = extract_iocs(text)
        self.assertIn("10.0.0.5", result["ipv4"])
        self.assertIn("192.168.44.100", result["ipv4"])
        self.assertTrue(any("malware-c2.evil.xyz" in u for u in result["urls"]))
        self.assertEqual(len(result["hashes"]), 1)
        self.assertEqual(result["hashes"][0]["type"], "sha256")


class TestDashboardIocEndpoint(unittest.TestCase):
    def setUp(self):
        from dashboard.app import app
        self.client = app.test_client()

    def test_ioc_extract_endpoint(self):
        res = self.client.post("/api/ioc/extract", json={
            "text": "C2 at 10.0.0.5 and hash d41d8cd98f00b204e9800998ecf8427e."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("10.0.0.5", data["ipv4"])
        self.assertEqual(len(data["hashes"]), 1)
        self.assertTrue(data["has_iocs"])

    def test_ioc_extract_empty_text(self):
        res = self.client.post("/api/ioc/extract", json={"text": ""})
        self.assertEqual(res.status_code, 400)

    def test_ioc_extract_no_body(self):
        res = self.client.post("/api/ioc/extract", json={})
        self.assertEqual(res.status_code, 400)

    def test_pipeline_includes_iocs(self):
        text = (
            "The attacker executed net.exe use \\\\10.0.0.5\\C$ "
            "/user:admin Passw0rd to mount an admin share."
        )
        res = self.client.post("/api/pipeline/run", json={"text": text})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("iocs", data)
        self.assertIn("10.0.0.5", data["iocs"]["ipv4"])


if __name__ == "__main__":
    unittest.main()
