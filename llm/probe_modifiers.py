"""Probe Sigma modifier chains through the repository's SQLite backend."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
from runner import rule_to_sql


CHAINS = [
    ("contains", "value"),
    ("contains|windash", "-all"),
    ("windash|contains", "-all"),
    ("contains|all", ["one", "two"]),
    ("contains|all|windash", ["-one", "-two"]),
    ("contains|windash|all", ["-one", "-two"]),
    ("all|contains", ["one", "two"]),
    ("windash", "-all"),
    ("endswith|windash", "-all"),
]


def yaml_rule(chain, value, image_list=False):
    if isinstance(value, list):
        rendered = "\n".join(f"            - '{item}'" for item in value)
        value_text = "\n" + rendered
    else:
        value_text = f" '{value}'"
    image = ("\n            - '\\tool.exe'\n            - '\\other.exe'"
             if image_list else " '\\tool.exe'")
    return ("title: Modifier probe\nstatus: test\nlogsource:\n"
            "    category: process_creation\n    product: windows\n"
            "detection:\n    selection:\n"
            f"        Image|endswith:{image}\n"
            f"        CommandLine|{chain}:{value_text}\n"
            "    condition: selection\nlevel: low\ntags:\n    - attack.execution\n")


def probe(chain, value, image_list=False):
    try:
        rule_to_sql(yaml_rule(chain, value, image_list))
    except Exception as error:
        return False, str(error)
    return True, ""


def main():
    rows = []
    for chain, value in CHAINS:
        converted, error = probe(chain, value)
        rows.append((chain, converted, error))
    image_chain, image_error = probe("contains|windash", "-all", image_list=True)
    rows.append(("Image list + contains|windash", image_chain, image_error))
    print("chain                         converts error")
    for chain, converted, error in rows:
        print(f"{chain:29} {'yes' if converted else 'no':8} {error}")
    path = "results/probe_modifiers.md"
    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    with open(path, "w", encoding="utf-8") as output:
        output.write("# Modifier probe\n\n")
        output.write("| Chain | Converts | Error |\n| --- | --- | --- |\n")
        for chain, converted, error in rows:
            output.write(f"| {chain.replace('|', '\\|')} | {'yes' if converted else 'no'} | "
                         f"{error.replace('|', '\\|')} |\n")
    print(f"SAVED {path}")


if __name__ == "__main__":
    main()