import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECK_SCRIPT = os.path.join(REPO_ROOT, "tools", "check_frozen.py")


def test_check_frozen_current_passes():
    res = subprocess.run([sys.executable, CHECK_SCRIPT], cwd=REPO_ROOT, capture_output=True, text=True)
    assert res.returncode == 0, f"Expected returncode 0, got {res.returncode}. Output: {res.stdout}\n{res.stderr}"
    assert "verified successfully" in res.stdout


def test_check_frozen_detects_mismatch():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cf", CHECK_SCRIPT)
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
        tmp.write("# Test\n| llm/prompts/v1.py | 0000000000000000000000000000000000000000000000000000000000000000 |\n")
        tmp_name = tmp.name

    try:
        expected = cf.parse_frozen_hashes(tmp_name)
        assert len(expected) == 1
        assert "llm/prompts/v1.py" in expected
        actual = cf.compute_sha256(os.path.join(REPO_ROOT, "llm", "prompts", "v1.py"))
        assert expected["llm/prompts/v1.py"] != actual
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


if __name__ == "__main__":
    test_check_frozen_current_passes()
    test_check_frozen_detects_mismatch()
    print("all check_frozen tests passed")

