import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_experiment_cmd(args):
    cmd = [sys.executable, "llm/run_experiment.py"] + args
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return res


def test_guard_refuses_no_final():
    # Attempt set 3 without --final
    res = run_experiment_cmd([
        "--set", "3",
        "--prompt", "v2_1",
        "--models", "qwen2.5-coder:7b",
        "--reason", "testing guard"
    ])
    assert res.returncode != 0, f"Expected non-zero returncode, got {res.returncode}"
    assert "Refusing run" in res.stdout or "Refusing run" in res.stderr


def test_guard_refuses_no_reason():
    # Attempt set 3 with --final but no --reason
    res = run_experiment_cmd([
        "--set", "3",
        "--prompt", "v2_1",
        "--models", "qwen2.5-coder:7b",
        "--final"
    ])
    assert res.returncode != 0, f"Expected non-zero returncode, got {res.returncode}"
    assert "Refusing run" in res.stdout or "Refusing run" in res.stderr


def test_guard_refuses_when_frozen_missing():
    # Attempt set 3 with --final and --reason, but FROZEN.md temporarily absent
    frozen_path = os.path.join(REPO_ROOT, "FROZEN.md")
    backup_path = os.path.join(REPO_ROOT, "FROZEN.md.tmp_test_guard")
    if os.path.exists(frozen_path):
        os.rename(frozen_path, backup_path)
    try:
        res = run_experiment_cmd([
            "--set", "3",
            "--prompt", "v2_1",
            "--models", "qwen2.5-coder:7b",
            "--final",
            "--reason", "testing guard without frozen files"
        ])
        assert res.returncode != 0, f"Expected non-zero returncode, got {res.returncode}"
        assert "Refusing run" in res.stdout or "Refusing run" in res.stderr
    finally:
        if os.path.exists(backup_path):
            os.rename(backup_path, frozen_path)


def test_no_log_or_folder_created():
    # Ensure set3_use_log.csv was not created during these refused attempts
    log_file = os.path.join(REPO_ROOT, "results", "set3_use_log.csv")
    assert not os.path.exists(log_file), f"results/set3_use_log.csv should not exist, but found it"


if __name__ == "__main__":
    test_guard_refuses_no_final()
    test_guard_refuses_no_reason()
    test_guard_refuses_when_frozen_missing()
    test_no_log_or_folder_created()
    print("all set 3 guard tests passed: guard strictly refuses unauthorized runs")

