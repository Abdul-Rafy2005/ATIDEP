"""Tests for prompts v3a and v3b."""
import os
import re
import sys
import unittest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "llm"))

from runner import rule_to_sql, rule_matches
from generate import TECHNIQUES as TECH1, BASE
from techniques_set2 import TECHNIQUES2 as TECH2, DESCRIPTIONS2
from techniques_set3 import TECHNIQUES3 as TECH3, DESCRIPTIONS3
from compare_models import DESCRIPTIONS as DESC1
from prompts import v3a, v3b

FORBIDDEN_PROGRAMS = [
    "powershell", "rundll32", "mshta", "regsvr32", "certutil", "schtasks",
    "reg", "net", "net1", "procdump", "bitsadmin", "wmic", "whoami",
    "hh", "rar", "takeown", "dsquery", "odbcconf", "netsh", "cipher",
    "bcdedit", "forfiles", "pypykatz", "ruby", "tshark", "at", "dtrace",
    "vboxdrvinst", "psr", "soundrecorder", "dsacls", "chrome", "firefox",
    "runscripthelper", "amazon-ssm-agent", "msxsl", "shutdown", "printbrm",
    "ssh", "register-cimprovider", "gpresult", "mstsc"
]


def make_event(image, command_line):
    ev = dict(BASE)
    ev["Image"] = image
    ev["CommandLine"] = command_line
    ev["OriginalFileName"] = image.split("\\")[-1].upper()
    return ev


class TestPromptsV3(unittest.TestCase):

    def test_a_both_prompts_build_for_all_sets(self):
        """(a) both prompts build for sets 1, 2 and 3."""
        for tech in TECH1:
            p3a = v3a.build_prompt(tech, TECH1, DESC1)
            p3b = v3b.build_prompt(tech, TECH1, DESC1)
            self.assertIn(f"Technique: {tech}", p3a)
            self.assertIn(f"Technique: {tech}", p3b)

        for tech in TECH2:
            p3a = v3a.build_prompt(tech, TECH2, DESCRIPTIONS2)
            p3b = v3b.build_prompt(tech, TECH2, DESCRIPTIONS2)
            self.assertIn(f"Technique: {tech}", p3a)
            self.assertIn(f"Technique: {tech}", p3b)

        for tech in TECH3:
            p3a = v3a.build_prompt(tech, TECH3, DESCRIPTIONS3)
            p3b = v3b.build_prompt(tech, TECH3, DESCRIPTIONS3)
            self.assertIn(f"Technique: {tech}", p3a)
            self.assertIn(f"Technique: {tech}", p3b)

    def test_b_v3a_examples_valid_and_fire_accurately(self):
        """(b) in v3a every example rule converts with pySigma, fires on its own observed line, and quiet on harmless."""
        # Extract the 3 example rules from v3a.EXAMPLES
        # Example 1
        ex1_rule = """title: Nslookup Used To Query TXT Records
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\nslookup.exe'
        CommandLine|contains|windash: '-type=txt'
    condition: selection
level: low
tags:
    - attack.command-and-control
    - attack.t1071.004"""
        sql1 = rule_to_sql(ex1_rule)
        self.assertTrue(sql1)
        ev1_obs = make_event(r"C:\Windows\System32\nslookup.exe", "nslookup.exe -type=txt data.example.com 10.0.0.53")
        ev1_harmless = make_event(r"C:\Windows\System32\nslookup.exe", "nslookup.exe example.com")
        self.assertTrue(rule_matches(ex1_rule, ev1_obs))
        self.assertFalse(rule_matches(ex1_rule, ev1_harmless))

        # Example 2
        ex2_rule = """title: Script Host Runs JavaScript In Batch Mode
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection_img:
        Image|endswith:
            - '\\wscript.exe'
            - '\\cscript.exe'
    selection_cli:
        CommandLine|contains|all:
            - '//B'
            - '//E:jscript'
    condition: all of selection_*
level: medium
tags:
    - attack.execution
    - attack.t1059.007"""
        sql2 = rule_to_sql(ex2_rule)
        self.assertTrue(sql2)
        ev2_obs = make_event(r"C:\Windows\System32\wscript.exe", "wscript.exe //B //E:jscript C:\\Users\\Public\\a.js")
        ev2_harmless = make_event(r"C:\Windows\System32\wscript.exe", "wscript.exe C:\\Scripts\\backup.vbs")
        self.assertTrue(rule_matches(ex2_rule, ev2_obs))
        self.assertFalse(rule_matches(ex2_rule, ev2_harmless))

        # Example 3
        ex3_rule = """title: Sdelete Used To Overwrite Files
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\sdelete.exe'
        CommandLine|contains|windash|all:
            - '-accepteula'
            - '-p'
    condition: selection
level: medium
tags:
    - attack.defense-evasion
    - attack.t1070.004"""
        sql3 = rule_to_sql(ex3_rule)
        self.assertTrue(sql3)
        ev3_obs = make_event(r"C:\Tools\sdelete.exe", "sdelete.exe -accepteula -p 3 C:\\Users\\student\\Documents")
        ev3_harmless = make_event(r"C:\Tools\sdelete.exe", "sdelete.exe -accepteula C:\\x.txt")
        self.assertTrue(rule_matches(ex3_rule, ev3_obs))
        self.assertFalse(rule_matches(ex3_rule, ev3_harmless))

    def test_c_no_sensitive_values_in_example_commandline(self):
        """(c) no CommandLine value in example rules contains a digit, IPv4, 'http', drive path (':\') or space."""
        for ex_yaml in [
            v3a.EXAMPLES[v3a.EXAMPLES.find("title: Nslookup"):v3a.EXAMPLES.find("Example 2")],
            v3a.EXAMPLES[v3a.EXAMPLES.find("title: Script Host"):v3a.EXAMPLES.find("Example 3")],
            v3a.EXAMPLES[v3a.EXAMPLES.find("title: Sdelete"):],
        ]:
            data = yaml.safe_load(ex_yaml)
            det = data["detection"]
            for sname, sdict in det.items():
                if sname == "condition" or not isinstance(sdict, dict):
                    continue
                for fspec, fval in sdict.items():
                    if fspec.startswith("CommandLine"):
                        vals = fval if isinstance(fval, list) else [fval]
                        for v in vals:
                            self.assertFalse(any(c.isdigit() for c in v), f"Digit found in value: {v}")
                            self.assertNotIn("http", v.lower(), f"'http' found in value: {v}")
                            self.assertNotIn(":\\", v, f"Drive path found in value: {v}")
                            self.assertNotIn(" ", v, f"Space found in value: {v}")
                            self.assertFalse(re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', v), f"IPv4 in {v}")

    def test_d_no_forbidden_program_names(self):
        """(d) none of the specified program names appears as a whole word in either prompt."""
        full_text_3a = v3a.INSTRUCTIONS + " " + v3a.EXAMPLES
        full_text_3b = v3b.INSTRUCTIONS + " " + v3b.EXAMPLES

        for prog in FORBIDDEN_PROGRAMS:
            if prog == "at":
                # 'at' as a program name (at.exe) is forbidden; the English preposition 'at'
                # in 'at the start or end of a value' is part of the required instruction text.
                pattern = re.compile(r'\bat\.exe\b', re.IGNORECASE)
            else:
                pattern = re.compile(r'\b' + re.escape(prog) + r'\b', re.IGNORECASE)
            m_a = pattern.search(full_text_3a)
            self.assertIsNone(m_a, f"Forbidden program '{prog}' found in v3a: {m_a}")
            m_b = pattern.search(full_text_3b)
            self.assertIsNone(m_b, f"Forbidden program '{prog}' found in v3b: {m_b}")

    def test_e_v3b_equals_v3a_except_two_changes(self):
        """(e) v3b equals v3a except for the two changes."""
        # Change 1: in INSTRUCTIONS
        old_inst_line = "- Output ONLY the Sigma rule as YAML. No explanation and no comments."
        new_inst_line = "- Start with two comment lines. The first starts with \"# keep:\" and lists the parts of the command line that make the behaviour dangerous. The second starts with \"# ignore:\" and lists the parts the attacker can change. Then write the Sigma rule as YAML, using only the \"keep\" parts. Write nothing else and no explanation."
        self.assertIn(old_inst_line, v3a.INSTRUCTIONS)
        self.assertIn(new_inst_line, v3b.INSTRUCTIONS)
        self.assertEqual(v3b.INSTRUCTIONS.replace(new_inst_line, old_inst_line), v3a.INSTRUCTIONS)

        # Change 2: in EXAMPLES
        # Example 1 comments
        ex1_c = "# keep: -type=txt\n# ignore: data.example.com, 10.0.0.53\n"
        ex2_c = "# keep: //B, //E:jscript\n# ignore: C:\\Users\\Public\\a.js\n"
        ex3_c = "# keep: -accepteula, -p\n# ignore: 3, C:\\Users\\student\\Documents\n"

        self.assertIn(ex1_c, v3b.EXAMPLES)
        self.assertIn(ex2_c, v3b.EXAMPLES)
        self.assertIn(ex3_c, v3b.EXAMPLES)

        reverted_ex = v3b.EXAMPLES.replace(ex1_c, "").replace(ex2_c, "").replace(ex3_c, "")
        self.assertEqual(reverted_ex, v3a.EXAMPLES)


if __name__ == "__main__":
    unittest.main()
