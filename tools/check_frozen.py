"""Verify all files recorded in FROZEN.md match their expected SHA-256 hashes."""
import hashlib
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FROZEN_MD = os.path.join(REPO_ROOT, "FROZEN.md")


def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_frozen_hashes(frozen_path):
    if not os.path.exists(frozen_path):
        print(f"Error: {frozen_path} does not exist.")
        sys.exit(1)

    expected = {}
    table_pattern = re.compile(r"^\|\s*([A-Za-z0-9_./\\]+)\s*\|\s*([a-f0-9]{64})\s*\|$")
    with open(frozen_path, "r", encoding="utf-8") as f:
        for line in f:
            match = table_pattern.match(line.strip())
            if match:
                rel_path = match.group(1).replace("\\", "/")
                expected[rel_path] = match.group(2)
    return expected


def check_frozen():
    expected = parse_frozen_hashes(FROZEN_MD)
    if not expected:
        print(f"Error: No file hashes found in {FROZEN_MD}.")
        sys.exit(1)

    mismatches = []
    missing = []

    for rel_path, expected_hash in expected.items():
        full_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            missing.append(rel_path)
            continue
        actual_hash = compute_sha256(full_path)
        if actual_hash != expected_hash:
            mismatches.append((rel_path, expected_hash, actual_hash))

    if missing or mismatches:
        print("FROZEN INTEGRITY CHECK FAILED:")
        for path in missing:
            print(f"  MISSING: {path}")
        for path, exp, act in mismatches:
            print(f"  CHANGED: {path}")
            print(f"    Expected: {exp}")
            print(f"    Actual:   {act}")
        sys.exit(1)

    print(f"All {len(expected)} frozen file hashes verified successfully.")
    return 0


if __name__ == "__main__":
    check_frozen()

