"""Lock Test Set 3 artifacts by recording their SHA-256 hashes in SET3_LOCK.md."""
import glob
import hashlib
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(REPO_ROOT, "SET3_LOCK.md")


def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def lock_set3():
    files_to_hash = [
        "generator/techniques_set3.py",
        "results/techniques_set3.csv",
    ]

    rules_dir = os.path.join(REPO_ROOT, "data", "sigmahq_rules_set3")
    rule_files = sorted(glob.glob(os.path.join(rules_dir, "*.yml")))
    for rf in rule_files:
        rel = os.path.relpath(rf, REPO_ROOT).replace("\\", "/")
        files_to_hash.append(rel)

    hashes = []
    for rel_path in files_to_hash:
        full_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            print(f"Error: Required file missing: {rel_path}")
            sys.exit(1)
        h = compute_sha256(full_path)
        hashes.append((rel_path, h))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Test Set 3 Lock\n\n")
        out.write("This file locks the ground truth artifacts for Test Set 3.\n\n")
        out.write("| File | SHA-256 |\n")
        out.write("| --- | --- |\n")
        for rel_path, h in hashes:
            out.write(f"| {rel_path} | {h} |\n")

    print(f"Locked {len(hashes)} Test Set 3 files into {OUTPUT_FILE}")


if __name__ == "__main__":
    lock_set3()

