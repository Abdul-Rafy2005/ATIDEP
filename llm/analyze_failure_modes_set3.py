"""Analysis of Final Test Set 3 Results and Failure Modes.

Produces results/FINAL_set3_report.md
"""
import os
import sys
import re
import json
import csv
import yaml
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))

from runner import rule_matches, rule_to_sql
from techniques_set3 import TECHNIQUES3, make_triple3
from scoring import score_rule
from compare_models import safe

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Configurations to analyze
CONFIGS = [
    {
        "role": "PRIMARY",
        "model": "qwen2.5-coder:14b",
        "prompt": "v3b",
        "run_id": "20261111_1500_set3_v3b",
        "label": "14B Primary (v3b)",
    },
    {
        "role": "PRIMARY",
        "model": "qwen2.5-coder:7b",
        "prompt": "v3a",
        "run_id": "20261111_1507_set3_v3a",
        "label": "7B Primary (v3a)",
    },
    {
        "role": "BASELINE",
        "model": "qwen2.5-coder:14b",
        "prompt": "v1",
        "run_id": "20261111_1449_set3_v1",
        "label": "14B Baseline (v1)",
    },
    {
        "role": "BASELINE",
        "model": "qwen2.5-coder:7b",
        "prompt": "v1",
        "run_id": "20261111_1449_set3_v1",
        "label": "7B Baseline (v1)",
    },
    {
        "role": "EXPLORATORY",
        "model": "qwen2.5-coder:14b",
        "prompt": "v3a",
        "run_id": "20261111_1512_set3_v3a",
        "label": "14B Exploratory (v3a)",
    },
    {
        "role": "EXPLORATORY",
        "model": "qwen2.5-coder:7b",
        "prompt": "v3b",
        "run_id": "20261111_1518_set3_v3b",
        "label": "7B Exploratory (v3b)",
    },
]

SET3_TECHNIQUES = list(TECHNIQUES3.keys())


def tokenize_spaces_quotes(line):
    parts = re.split(r'[\s"\'`]+', line)
    return [p for p in parts if p]


def extract_subtokens(line):
    parts = re.split(r'[\s"\'`(),;:.\=\\]+', line)
    return [p for p in parts if p]


def test_rule_condition(field_spec, val, shown_event, variant_event):
    val_repr = [val] if ("|all" in field_spec or isinstance(val, str)) else val
    test_yaml = f"""title: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    {field_spec}: {json.dumps(val_repr)}
  condition: selection
"""
    try:
        fires_shown = rule_matches(test_yaml, shown_event)
        fires_variant = rule_matches(test_yaml, variant_event)
        return fires_shown, fires_variant
    except Exception:
        test_yaml_scalar = f"""title: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    {field_spec}: {json.dumps(val)}
  condition: selection
"""
        try:
            fires_shown = rule_matches(test_yaml_scalar, shown_event)
            fires_variant = rule_matches(test_yaml_scalar, variant_event)
            return fires_shown, fires_variant
        except Exception:
            return False, False


def classify_condition(field_spec, val_str, tech, rule_text):
    """Classify a blocking condition for Set 3 with the FIRST matching class."""
    d = TECHNIQUES3[tech]
    shown_line = d["malicious"]
    variant_line = d["variant"]

    field_clean = field_spec.split("|")[0].strip()

    # 1. ALIAS_IMAGE: Image or OriginalFileName fails on variant because executable name differs
    if field_clean in ("Image", "OriginalFileName"):
        var_img = d.get("variant_image", d["image"])
        var_base = os.path.basename(var_img).lower()
        shown_base = os.path.basename(d["image"]).lower()
        if var_base != shown_base:
            return "ALIAS_IMAGE"

    # 2. VALUE: contains IPv4, URL, drive path, filename with extension, >=3 digits, or token unique to shown
    if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', val_str):
        return "VALUE"
    if re.search(r'https?://|script:http', val_str, re.IGNORECASE):
        return "VALUE"
    if re.search(r'[a-zA-Z]:\\|\\temp\\|\\windows\\|\\appdata\\', val_str, re.IGNORECASE):
        return "VALUE"
    if re.search(r'\b[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]{2,4}\b|\.[a-zA-Z0-9]{2,4}\b', val_str):
        return "VALUE"
    if re.search(r'\b\d{3,}\b', val_str):
        return "VALUE"

    shown_subtoks = extract_subtokens(shown_line)
    var_subtoks = extract_subtokens(variant_line)
    var_subtoks_lower = set(t.lower() for t in var_subtoks)
    only_shown_subtoks = [t for t in shown_subtoks if t.lower() not in var_subtoks_lower and not t.startswith(("-", "/"))]
    for t in only_shown_subtoks:
        if len(t) >= 2 and t.lower() in val_str.lower():
            return "VALUE"

    # 3. FLAG_INCIDENTAL: value is a flag (starts with - or /) in shown line but not in variant line
    stripped_val = val_str.strip()
    if stripped_val.startswith(("-", "/")):
        flag_token = stripped_val.split()[0]
        flag_name = flag_token.lstrip("-/")
        var_flags = [vt for vt in tokenize_spaces_quotes(variant_line) if vt.startswith(("-", "/"))]
        var_has_diff_prefix = any(
            (vt.lstrip("-/").lower() == flag_name.lower() and vt[0] != flag_token[0])
            for vt in var_flags
        )
        if not var_has_diff_prefix:
            if flag_token in tokenize_spaces_quotes(shown_line) and flag_token not in variant_line:
                return "FLAG_INCIDENTAL"

    # 4. ADJACENT: two or more words, every word in variant line, but not next to each other in that order
    words = [w for w in re.split(r'\s+', stripped_val) if w]
    if len(words) >= 2:
        all_words_in_var = all(w in variant_line for w in words)
        if all_words_in_var and (stripped_val not in variant_line):
            return "ADJACENT"

    # 5. PREFIX: flag whose - or / prefix differs from variant and rule does not use windash
    if stripped_val.startswith(("-", "/")):
        flag_token = stripped_val.split()[0]
        flag_name = flag_token.lstrip("-/")
        var_flags = [vt for vt in tokenize_spaces_quotes(variant_line) if vt.startswith(("-", "/"))]
        var_has_diff_prefix = any(
            (vt.lstrip("-/").lower() == flag_name.lower() and vt[0] != flag_token[0])
            for vt in var_flags
        )
        has_windash = "windash" in field_spec.lower() or "windash" in rule_text.lower()
        if var_has_diff_prefix and not has_windash:
            return "PREFIX"

    # Fallback flag check
    if stripped_val.startswith(("-", "/")) and stripped_val not in variant_line:
        return "FLAG_INCIDENTAL"

    return "OTHER"


def analyze_all():
    results = []

    for cfg in CONFIGS:
        model = cfg["model"]
        prompt = cfg["prompt"]
        run_id = cfg["run_id"]
        role = cfg["role"]
        label = cfg["label"]

        run_folder = os.path.join(REPO_ROOT, "results", "runs", run_id)
        timings = []
        with open(os.path.join(run_folder, "results.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r["model"] == model and "seconds" in r and r["seconds"]:
                    timings.append(float(r["seconds"]))

        counts = defaultdict(int)
        tech_passes = defaultdict(int)
        tech_repeats_pass = defaultdict(list)
        variant_type_passes = defaultdict(int)
        variant_type_totals = defaultdict(int)
        failed_rules = []
        too_narrow_blockers = []

        for tech in SET3_TECHNIQUES:
            shown, variant, benign = make_triple3(tech)
            v_type = TECHNIQUES3[tech]["variant_type"]
            for rep in (1, 2, 3):
                variant_type_totals[v_type] += 1
                fn = f"{tech}_repeat{rep}.yml"
                p = os.path.join(run_folder, "rules_first", safe(model), fn)
                with open(p, encoding="utf-8") as rf:
                    text = rf.read()

                res = score_rule(3, tech, text)
                counts["total"] += 1
                if not res.syntax_ok:
                    counts["syntax_errors"] += 1
                if res.single_pass:
                    counts["single_pass"] += 1
                if res.strict_pass:
                    counts["strict_pass"] += 1
                    tech_passes[tech] += 1
                    tech_repeats_pass[tech].append(rep)
                    variant_type_passes[v_type] += 1
                counts[res.verdict] += 1

                # Extract detection block representation
                det_block_lines = []
                for line in text.splitlines():
                    if line.startswith("detection:"):
                        det_block_lines.append(line)
                    elif det_block_lines:
                        if re.match(r'^[a-zA-Z_]+:', line) and not line.startswith(" "):
                            break
                        det_block_lines.append(line)
                det_block_str = "\n".join(det_block_lines)

                if not res.strict_pass:
                    failed_rules.append({
                        "tech": tech,
                        "repeat": rep,
                        "verdict": res.verdict,
                        "shown": shown["CommandLine"],
                        "variant": variant["CommandLine"],
                        "det_block": det_block_str,
                        "text": text,
                    })

                if res.verdict == "TOO_NARROW":
                    try:
                        parsed_yaml = yaml.safe_load(text)
                        det_all = parsed_yaml.get("detection", {})
                    except Exception:
                        det_all = {}
                    blockers = []
                    for sname, sdict in det_all.items():
                        if sname == "condition" or not isinstance(sdict, dict):
                            continue
                        for fspec, fval in sdict.items():
                            vlist = fval if isinstance(fval, list) else [fval]
                            for v in vlist:
                                if not isinstance(v, (str, int, float)):
                                    continue
                                f_shown, f_var = test_rule_condition(fspec, v, shown, variant)
                                if f_shown and not f_var:
                                    cls = classify_condition(fspec, str(v), tech, text)
                                    blockers.append({"field": fspec, "val": str(v), "cls": cls})
                    too_narrow_blockers.append({
                        "tech": tech,
                        "repeat": rep,
                        "blockers": blockers,
                    })

        # Count techniques with >= 2 of 3 passes
        techs_passed_ge2 = sum(1 for tech in SET3_TECHNIQUES if tech_passes[tech] >= 2)
        avg_sec = sum(timings) / len(timings) if timings else 0.0

        # Classify TOO_NARROW primary blockers
        tn_classes = defaultdict(int)
        for item in too_narrow_blockers:
            if item["blockers"]:
                primary_cls = item["blockers"][0]["cls"]
                tn_classes[primary_cls] += 1
            else:
                tn_classes["OTHER"] += 1

        results.append({
            "cfg": cfg,
            "counts": counts,
            "tech_passes": tech_passes,
            "techs_passed_ge2": techs_passed_ge2,
            "variant_type_passes": variant_type_passes,
            "variant_type_totals": variant_type_totals,
            "avg_sec": avg_sec,
            "failed_rules": failed_rules,
            "tn_classes": tn_classes,
        })

    return results


def write_report(results):
    out_path = os.path.join(REPO_ROOT, "results", "FINAL_set3_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Final Test on Set 3: Evaluation Report\n\n")
        f.write("This report presents the final evaluation of ATIDEP on locked Test Set 3 (20 techniques, 3 repeats, N=60 per configuration, temperature 0.2, seed 100).\n\n")

        # -------------------------------------------------------------
        # Section 1: Overview Table
        # -------------------------------------------------------------
        f.write("## 1. Overall Performance by Configuration\n\n")
        headers = [
            "Configuration", "Role", "Model", "Prompt", "Syntax Errors",
            "Single Pass (/60)", "Strict Pass (/60)", "Strict Pass (%)",
            "MISSED_SHOWN", "TOO_NARROW", "NOISY", "Techniques Passed (>=2/3)", "Avg Sec/Rule"
        ]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

        for r in results:
            cfg = r["cfg"]
            c = r["counts"]
            pct = (c["strict_pass"] / c["total"]) * 100
            f.write(
                f"| {cfg['label']} | **{cfg['role']}** | `{cfg['model']}` | `{cfg['prompt']}` | "
                f"{c['syntax_errors']} | {c['single_pass']}/{c['total']} | **{c['strict_pass']}/{c['total']}** | "
                f"{pct:.1f}% | {c['MISSED_SHOWN']} | {c['TOO_NARROW']} | {c['NOISY']} | "
                f"**{r['techs_passed_ge2']}/20** | {r['avg_sec']:.2f}s |\n"
            )

        # -------------------------------------------------------------
        # Section 2: Paired Comparisons (v1 vs Frozen)
        # -------------------------------------------------------------
        f.write("\n## 2. Primary Comparison: Frozen Prompt vs. Baseline v1 Prompt\n\n")
        f.write("Comparison of each model under its frozen prompt against baseline prompt v1.\n\n")

        # Find results
        res_by_key = {(r["cfg"]["model"], r["cfg"]["prompt"]): r for r in results}
        paired_models = [
            ("qwen2.5-coder:14b", "v3b", "PRIMARY MODEL"),
            ("qwen2.5-coder:7b", "v3a", "COMPARISON MODEL"),
        ]

        p_headers = ["Model", "Metric", "Baseline (v1)", "Frozen Prompt", "Absolute Difference", "Relative Change"]
        f.write("| " + " | ".join(p_headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(p_headers)) + " |\n")

        for model, frozen_p, m_role in paired_models:
            r_v1 = res_by_key[(model, "v1")]
            r_fr = res_by_key[(model, frozen_p)]
            pass_v1 = r_v1["counts"]["strict_pass"]
            pass_fr = r_fr["counts"]["strict_pass"]
            diff = pass_fr - pass_v1
            rel = ((diff) / pass_v1 * 100) if pass_v1 > 0 else 0.0

            ge2_v1 = r_v1["techs_passed_ge2"]
            ge2_fr = r_fr["techs_passed_ge2"]
            ge2_diff = ge2_fr - ge2_v1

            f.write(f"| `{model}` ({m_role}) | Strict Pass (/60) | {pass_v1}/60 | **{pass_fr}/60** | **+{diff}** | **+{rel:.1f}%** |\n")
            f.write(f"| `{model}` ({m_role}) | Techs Passed (>=2/3) | {ge2_v1}/20 | **{ge2_fr}/20** | +{ge2_diff} | - |\n")

        # Per-technique paired table
        f.write("\n### Per-Technique Paired Breakdown (Improved / Same / Worse)\n\n")
        pt_headers = ["Technique", "Variant Type", "14B v1", "14B v3b (Primary)", "14B Shift", "7B v1", "7B v3a (Primary)", "7B Shift"]
        f.write("| " + " | ".join(pt_headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(pt_headers)) + " |\n")

        shifts_14b = {"improved": 0, "same": 0, "worse": 0}
        shifts_7b = {"improved": 0, "same": 0, "worse": 0}

        for tech in SET3_TECHNIQUES:
            v_type = TECHNIQUES3[tech]["variant_type"]
            p_14_v1 = res_by_key[("qwen2.5-coder:14b", "v1")]["tech_passes"][tech]
            p_14_fr = res_by_key[("qwen2.5-coder:14b", "v3b")]["tech_passes"][tech]
            if p_14_fr > p_14_v1:
                s14 = "improved"
                shifts_14b["improved"] += 1
            elif p_14_fr == p_14_v1:
                s14 = "same"
                shifts_14b["same"] += 1
            else:
                s14 = "worse"
                shifts_14b["worse"] += 1

            p_7_v1 = res_by_key[("qwen2.5-coder:7b", "v1")]["tech_passes"][tech]
            p_7_fr = res_by_key[("qwen2.5-coder:7b", "v3a")]["tech_passes"][tech]
            if p_7_fr > p_7_v1:
                s7 = "improved"
                shifts_7b["improved"] += 1
            elif p_7_fr == p_7_v1:
                s7 = "same"
                shifts_7b["same"] += 1
            else:
                s7 = "worse"
                shifts_7b["worse"] += 1

            f.write(f"| `{tech}` | {v_type} | {p_14_v1}/3 | {p_14_fr}/3 | **{s14}** | {p_7_v1}/3 | {p_7_fr}/3 | **{s7}** |\n")

        f.write(f"\n**Summary of paired technique shifts**:\n")
        f.write(f"- `qwen2.5-coder:14b` (v1 -> v3b): **{shifts_14b['improved']} improved**, **{shifts_14b['same']} same**, **{shifts_14b['worse']} worse**.\n")
        f.write(f"- `qwen2.5-coder:7b` (v1 -> v3a): **{shifts_7b['improved']} improved**, **{shifts_7b['same']} same**, **{shifts_7b['worse']} worse**.\n")

        # -------------------------------------------------------------
        # Section 3: Strict Passes Split by Variant Type
        # -------------------------------------------------------------
        f.write("\n## 3. Strict Passes Split by Variant Type\n\n")
        f.write("Set 3 contains 12 `values` variants and 8 `order_or_prefix` variants (36 and 24 evaluations per configuration respectively):\n\n")
        vt_headers = ["Configuration", "Role", "Values Passes (/36)", "Values Pass Rate", "Order/Prefix Passes (/24)", "Order/Prefix Pass Rate", "Total Strict Pass (/60)"]
        f.write("| " + " | ".join(vt_headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(vt_headers)) + " |\n")

        for r in results:
            cfg = r["cfg"]
            v_p = r["variant_type_passes"]["values"]
            v_t = r["variant_type_totals"]["values"]
            op_p = r["variant_type_passes"]["order_or_prefix"]
            op_t = r["variant_type_totals"]["order_or_prefix"]
            v_pct = (v_p / v_t * 100) if v_t > 0 else 0.0
            op_pct = (op_p / op_t * 100) if op_t > 0 else 0.0
            f.write(f"| {cfg['label']} | {cfg['role']} | {v_p}/{v_t} | {v_pct:.1f}% | {op_p}/{op_t} | {op_pct:.1f}% | **{r['counts']['strict_pass']}/60** |\n")

        # -------------------------------------------------------------
        # Section 4: Pass Count per Technique across Configurations
        # -------------------------------------------------------------
        f.write("\n## 4. Strict Pass Count per Technique across Configurations (out of 3 repeats)\n\n")
        tc_headers = ["Technique", "Variant Type"] + [r["cfg"]["label"] for r in results]
        f.write("| " + " | ".join(tc_headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(tc_headers)) + " |\n")

        for tech in SET3_TECHNIQUES:
            v_type = TECHNIQUES3[tech]["variant_type"]
            row_cols = [f"{r['tech_passes'][tech]}/3" for r in results]
            f.write(f"| `{tech}` | {v_type} | " + " | ".join(row_cols) + " |\n")

        totals_cols = [f"**{r['counts']['strict_pass']}/60**" for r in results]
        f.write("| **Total Strict** | - | " + " | ".join(totals_cols) + " |\n")

        # -------------------------------------------------------------
        # Section 5: TOO_NARROW Failure Mode Classification
        # -------------------------------------------------------------
        f.write("\n## 5. TOO_NARROW Failure Mode Classification\n\n")
        f.write("Classification of all TOO_NARROW rules across configurations into primary blocking condition classes:\n\n")
        fm_classes = ["ALIAS_IMAGE", "VALUE", "FLAG_INCIDENTAL", "ADJACENT", "PREFIX", "OTHER"]
        fm_headers = ["Configuration", "Total TOO_NARROW"] + fm_classes
        f.write("| " + " | ".join(fm_headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(fm_headers)) + " |\n")

        for r in results:
            cfg = r["cfg"]
            tot_tn = r["counts"]["TOO_NARROW"]
            cls_cols = [str(r["tn_classes"].get(c, 0)) for c in fm_classes]
            f.write(f"| {cfg['label']} | {tot_tn} | " + " | ".join(cls_cols) + " |\n")

        f.write("\nAs anticipated, `ALIAS_IMAGE` is 0 across all configurations because all Set 3 techniques retain consistent executable names across shown and variant lines.\n")

        # -------------------------------------------------------------
        # Section 6: Comprehensive Failed Rules Catalog
        # -------------------------------------------------------------
        f.write("\n## 6. Catalog of Failed Rules\n\n")
        f.write("Full listing of all first-try rules that did not pass the strict gate:\n\n")

        total_failed = sum(len(r["failed_rules"]) for r in results)
        f.write(f"Total non-pass first-try rules across all 360 evaluations: **{total_failed}**.\n\n")

        for r in results:
            cfg = r["cfg"]
            if not r["failed_rules"]:
                continue
            f.write(f"### {cfg['label']} ({len(r['failed_rules'])} failed rules)\n\n")
            for fr in r["failed_rules"]:
                f.write(f"#### `{fr['tech']}` (Repeat {fr['repeat']}) - Verdict: `{fr['verdict']}`\n\n")
                f.write(f"- **Shown line**: `{fr['shown']}`\n")
                f.write(f"- **Variant line**: `{fr['variant']}`\n")
                f.write(f"- **Detection Block**:\n```yaml\n{fr['det_block']}\n```\n\n")

    print(f"Written {out_path}")


def main():
    print("Analyzing Set 3 runs...")
    results = analyze_all()
    print("Writing results/FINAL_set3_report.md...")
    write_report(results)
    print("Done.")


if __name__ == "__main__":
    main()

