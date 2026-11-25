"""Tests for the rule export module (Sigma to SPL, KQL, SQLite)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from export.rule_export import to_splunk, to_kql, to_sqlite, convert, convert_all, FORMATS

VALID_RULE = """
title: Test Export Rule
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\\\whoami.exe'
        CommandLine|contains: '/priv'
    condition: selection
"""

BAD_RULE = """
title: Broken Rule
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        CommandLine|contains|all:
            windash:
                - '/r'
    condition: selection
"""


class TestSplunkExport:
    def test_valid_rule_returns_spl(self):
        result = to_splunk(VALID_RULE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_spl_contains_field_names(self):
        result = to_splunk(VALID_RULE)
        assert "CommandLine" in result
        assert "/priv" in result

    def test_spl_contains_image(self):
        result = to_splunk(VALID_RULE)
        assert "whoami" in result.lower() or "Image" in result


class TestKqlExport:
    def test_valid_rule_returns_kql(self):
        result = to_kql(VALID_RULE)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_kql_contains_field_names(self):
        result = to_kql(VALID_RULE)
        assert "CommandLine" in result
        assert "/priv" in result

    def test_kql_uses_operators(self):
        result = to_kql(VALID_RULE)
        assert "contains" in result or "has" in result or "=~" in result


class TestSqliteExport:
    def test_valid_rule_returns_sql(self):
        result = to_sqlite(VALID_RULE)
        assert isinstance(result, str)
        assert "SELECT" in result or "select" in result.lower()

    def test_sql_references_logs_table(self):
        result = to_sqlite(VALID_RULE)
        assert "logs" in result.lower()


class TestConvert:
    def test_sigma_returns_original(self):
        result = convert(VALID_RULE, "sigma")
        assert result == VALID_RULE

    def test_splunk_format(self):
        result = convert(VALID_RULE, "splunk")
        assert len(result) > 0

    def test_kql_format(self):
        result = convert(VALID_RULE, "kql")
        assert len(result) > 0

    def test_sqlite_format(self):
        result = convert(VALID_RULE, "sqlite")
        assert len(result) > 0

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown format"):
            convert(VALID_RULE, "nosuchformat")


class TestConvertAll:
    def test_returns_all_formats(self):
        results = convert_all(VALID_RULE)
        assert "sigma" in results
        assert "splunk" in results
        assert "kql" in results
        assert "sqlite" in results

    def test_sigma_is_original(self):
        results = convert_all(VALID_RULE)
        assert results["sigma"] == VALID_RULE

    def test_all_formats_non_empty(self):
        results = convert_all(VALID_RULE)
        for fmt, val in results.items():
            assert len(val) > 0, f"Format {fmt} returned empty"


class TestFormats:
    def test_formats_dict_has_expected_keys(self):
        assert "sigma" in FORMATS
        assert "splunk" in FORMATS
        assert "kql" in FORMATS
        assert "sqlite" in FORMATS

    def test_formats_has_descriptions(self):
        for fmt, desc in FORMATS.items():
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestBadRuleHandling:
    def test_bad_rule_splunk_raises(self):
        with pytest.raises(Exception):
            to_splunk(BAD_RULE)

    def test_convert_all_bad_rule_has_error_strings(self):
        results = convert_all(BAD_RULE)
        error_count = sum(1 for v in results.values() if v.startswith("Error:"))
        assert error_count >= 1
