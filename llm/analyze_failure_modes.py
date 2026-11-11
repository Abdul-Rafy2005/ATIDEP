"""Analyze failure modes and strict gate behavior on set 1.

Generates:
1. results/set1_strict_summary.md
2. results/set1_failure_modes.md
"""
import os
import sys
import re
import json
import yaml
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
sys.path.insert(0, os.path.dirname(__file__))

from runner import rule_matches, rule_to_sql
from generate import TECHNIQUES, make_triple
from scoring import score_rule
from compare_models import safe

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SET1_TECHNIQUES = [
    "T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105",
    "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197",
    "T1047", "T1033",
]

RUNS_3REPEAT = [
    ("v1", "20261021_1528_set1_v1", 0.2, 3),
    ("v2", "20261104_1503_set1_v2", 0.2, 3),
    ("v2_1", "20261106_1344_set1_v2_1", 0.2, 3),
    ("v3a", "20261111_1403_set1_v3a", 0.2, 3),
    ("v3b", "20261111_1413_set1_v3b", 0.2, 3),
]

RUNS_SINGLE = [
    ("v1", "20261021_1510_set1_v1", 0, 1),
    ("v1", "20261021_1510_01_set1_v1", 0, 1),
    ("v2", "20261021_1511_set1_v2", 0, 1),
]

MODELS = ["qwen2.5-coder:7b", "qwen2.5-coder:14b"]


def tokenize_spaces_quotes(line):
    """Split on spaces and quotes."""
    parts = re.split(r'[\s"\'`]+', line)
    return [p for p in parts if p]


def extract_subtokens(line):
    """Extract subtokens splitting on spaces, quotes, and punctuation."""
    parts = re.split(r'[\s"\'`(),;:.\=\\]+', line)
    return [p for p in parts if p]


def test_rule_condition(field_spec, val, shown_event, variant_event):
    """Test a single field condition alone on shown and variant events."""
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
    """Classify a blocking condition with the FIRST matching class."""
    d = TECHNIQUES[tech]
    shown_line = d["malicious"]
    variant_line = d["variant"]

    field_clean = field_spec.split("|")[0].strip()

    # 1. ALIAS_IMAGE: Image or OriginalFileName fails on variant (variant_image differs)
    if field_clean in ("Image", "OriginalFileName"):
        var_img = d.get("variant_image", d["image"])
        if var_img != d["image"]:
            return "ALIAS_IMAGE"

    # 2. VALUE: contains IPv4, URL, drive path, filename with extension, >=3 digits, or token in shown but not variant
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


def step1_strict_summary():
    """Build results/set1_strict_summary.md."""
    # 1. 3-repeat runs
    summary_3rep = []
    tech_passes_3rep = {}  # (model, prompt) -> dict(tech -> count)

    for prompt_ver, run_id, temp, reps in RUNS_3REPEAT:
        folder = os.path.join(REPO_ROOT, "results", "runs", run_id)
        for model in MODELS:
            counts = defaultdict(int)
            tech_counts = defaultdict(int)
            for tech in SET1_TECHNIQUES:
                for rep in range(1, reps + 1):
                    fn = f"{tech}_repeat{rep}.yml"
                    p = os.path.join(folder, "rules_first", safe(model), fn)
                    if not os.path.exists(p):
                        continue
                    counts["total"] += 1
                    with open(p, encoding="utf-8") as f:
                        text = f.read()
                    res = score_rule(1, tech, text)
                    if not res.syntax_ok:
                        counts["syntax_errors"] += 1
                    if res.single_pass:
                        counts["single_pass"] += 1
                    if res.strict_pass:
                        counts["strict_pass"] += 1
                        tech_counts[tech] += 1
                    counts[res.verdict] += 1

            summary_3rep.append({
                "run_id": run_id, "prompt": prompt_ver, "model": model,
                "temp": temp, "reps": reps, "counts": counts,
            })
            tech_passes_3rep[(model, prompt_ver)] = tech_counts

    # 2. Single-run (temp 0)
    summary_single = []
    for prompt_ver, run_id, temp, reps in RUNS_SINGLE:
        folder = os.path.join(REPO_ROOT, "results", "runs", run_id)
        with open(os.path.join(folder, "settings.json"), encoding="utf-8") as sf:
            settings = json.load(sf)
        for model in settings["models"]:
            counts = defaultdict(int)
            for tech in SET1_TECHNIQUES:
                fn = f"{tech}.yml"
                p = os.path.join(folder, "rules_first", safe(model), fn)
                if not os.path.exists(p):
                    continue
                counts["total"] += 1
                with open(p, encoding="utf-8") as f:
                    text = f.read()
                res = score_rule(1, tech, text)
                if not res.syntax_ok:
                    counts["syntax_errors"] += 1
                if res.single_pass:
                    counts["single_pass"] += 1
                if res.strict_pass:
                    counts["strict_pass"] += 1
                counts[res.verdict] += 1

            summary_single.append({
                "run_id": run_id, "prompt": prompt_ver, "model": model,
                "temp": temp, "reps": reps, "counts": counts,
            })

    out_path = os.path.join(REPO_ROOT, "results", "set1_strict_summary.md")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("# Set 1 Strict Summary\n\n")
        out.write("This document summarizes the first-try strict gate results for all complete set 1 evaluations.\n\n")
        out.write("## Variance Evaluations (Temperature 0.2, 3 Repeats, N=36)\n\n")
        headers = [
            "Model", "Prompt", "Run ID", "Syntax Errors", "Single Pass", "Strict Pass",
            "MISSED_SHOWN", "NOISY", "TOO_NARROW", "Total N",
        ]
        out.write("| " + " | ".join(headers) + " |\n")
        out.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in summary_3rep:
            c = row["counts"]
            out.write(
                f"| {row['model']} | {row['prompt']} | {row['run_id']} | "
                f"{c['syntax_errors']} | {c['single_pass']}/{c['total']} | {c['strict_pass']}/{c['total']} | "
                f"{c['MISSED_SHOWN']} | {c['NOISY']} | {c['TOO_NARROW']} | {c['total']} |\n"
            )

        out.write("\n## Single Runs (Temperature 0, 1 Repeat, N=12)\n\n")
        out.write("| " + " | ".join(headers) + " |\n")
        out.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in summary_single:
            c = row["counts"]
            out.write(
                f"| {row['model']} | {row['prompt']} | {row['run_id']} | "
                f"{c['syntax_errors']} | {c['single_pass']}/{c['total']} | {c['strict_pass']}/{c['total']} | "
                f"{c['MISSED_SHOWN']} | {c['NOISY']} | {c['TOO_NARROW']} | {c['total']} |\n"
            )

        out.write("\n## Strict Passes per Technique (out of 3 repeats, Temperature 0.2)\n\n")
        tech_headers = ["Model", "Prompt"] + SET1_TECHNIQUES + ["Total"]
        out.write("| " + " | ".join(tech_headers) + " |\n")
        out.write("| " + " | ".join(["---"] * len(tech_headers)) + " |\n")
        for row in summary_3rep:
            m = row["model"]
            p = row["prompt"]
            tc = tech_passes_3rep[(m, p)]
            passes = [f"{tc[t]}/3" for t in SET1_TECHNIQUES]
            total_pass = f"{sum(tc[t] for t in SET1_TECHNIQUES)}/36"
            out.write(f"| {m} | {p} | " + " | ".join(passes) + f" | {total_pass} |\n")

    print(f"Written {out_path}")
    return summary_3rep


def step2_technique_changes():
    """Section 1: What changed between shown and variant for the 12 set 1 techniques."""
    results = []
    for tech in SET1_TECHNIQUES:
        d = TECHNIQUES[tech]
        shown = d["malicious"]
        variant = d["variant"]
        shown_toks = tokenize_spaces_quotes(shown)
        variant_toks = tokenize_spaces_quotes(variant)

        only_shown = [t for t in shown_toks if t not in variant_toks]
        only_variant = [t for t in variant_toks if t not in shown_toks]

        applies = []
        if d.get("variant_image") and d["variant_image"] != d["image"]:
            applies.append("different program name (variant_image)")

        shown_flags = {t[1:]: t[0] for t in shown_toks if t.startswith(("-", "/"))}
        variant_flags = {t[1:]: t[0] for t in variant_toks if t.startswith(("-", "/"))}
        has_prefix_diff = any(
            name in variant_flags and variant_flags[name] != p
            for name, p in shown_flags.items()
        )
        if has_prefix_diff or tech == "T1033":
            applies.append("flag prefix (- versus /)")

        shown_flag_set = {t for t in shown_toks if t.startswith(("-", "/"))}
        variant_flag_set = {t for t in variant_toks if t.startswith(("-", "/"))}
        flag_diff = (shown_flag_set - variant_flag_set) | (variant_flag_set - shown_flag_set)
        pure_extra_flags = [f for f in flag_diff if f[1:] not in shown_flags or f[1:] not in variant_flags]
        if pure_extra_flags:
            applies.append("extra or missing flags")

        common_flags_shown = [t for t in shown_toks if t.startswith(("-", "/")) and t in variant_flag_set]
        common_flags_var = [t for t in variant_toks if t.startswith(("-", "/")) and t in shown_flag_set]
        if common_flags_shown and common_flags_var and common_flags_shown != common_flags_var:
            applies.append("flag order")

        if tech in ["T1059.001", "T1218.011", "T1218.005", "T1218.010", "T1105", "T1053.005", "T1547.001", "T1136.001", "T1003.001", "T1197", "T1047"]:
            applies.append("values")

        results.append({
            "tech": tech,
            "image": d["image"],
            "variant_image": d.get("variant_image", d["image"]),
            "shown": shown,
            "variant": variant,
            "only_shown": only_shown,
            "only_variant": only_variant,
            "applies": applies,
        })
    return results


def step3_and_step4_failure_modes():
    """Analyze failure modes, extract blocking conditions and extra counts."""
    configs = [
        ("v3b", "20261111_1413_set1_v3b"),
        ("v3a", "20261111_1403_set1_v3a"),
        ("v2_1", "20261106_1344_set1_v2_1"),
        ("v2", "20261104_1503_set1_v2"),
        ("v1", "20261021_1528_set1_v1"),
    ]

    analysis = {}
    extra_counts = {
        "windash_in_too_narrow": defaultdict(int),
        "padded_space": defaultdict(int),
        "keyword_only_rules": defaultdict(int),
        "keyword_only_strict_pass": defaultdict(int),
    }

    for prompt_ver, run_id in configs:
        folder = os.path.join(REPO_ROOT, "results", "runs", run_id)
        for model in MODELS:
            tn_rules = []
            cfg_key = (model, prompt_ver)
            for tech in SET1_TECHNIQUES:
                shown, variant, benign = make_triple(tech)
                for repeat in (1, 2, 3):
                    fn = f"{tech}_repeat{repeat}.yml"
                    p = os.path.join(folder, "rules_first", safe(model), fn)
                    if not os.path.exists(p):
                        continue
                    with open(p, encoding="utf-8") as f:
                        text = f.read()

                    # Check Step 4 keyword condition across all rules
                    try:
                        parsed_yaml = yaml.safe_load(text)
                        det_all = parsed_yaml.get("detection", {})
                    except Exception:
                        det_all = {}

                    # Check padded space across all rules
                    has_padded = False
                    # Check keyword-only structure: Image check + single CommandLine value
                    is_keyword_only = False
                    cli_values = []
                    image_checks = 0
                    other_fields = 0

                    for sname, sdict in det_all.items():
                        if sname == "condition" or not isinstance(sdict, dict):
                            continue
                        for fspec, fval in sdict.items():
                            fclean = fspec.split("|")[0].strip()
                            vlist = fval if isinstance(fval, list) else [fval]
                            for v in vlist:
                                if isinstance(v, str) and (v.startswith(" ") or v.endswith(" ")):
                                    has_padded = True
                            if fclean == "Image":
                                image_checks += 1
                            elif fclean == "CommandLine":
                                cli_values.extend(vlist)
                            else:
                                other_fields += 1

                    if has_padded:
                        extra_counts["padded_space"][cfg_key] += 1

                    if image_checks == 1 and other_fields == 0 and len(cli_values) == 1:
                        extra_counts["keyword_only_rules"][cfg_key] += 1
                        res_kw = score_rule(1, tech, text)
                        if res_kw.strict_pass:
                            extra_counts["keyword_only_strict_pass"][cfg_key] += 1

                    res = score_rule(1, tech, text)
                    if res.verdict != "TOO_NARROW":
                        continue

                    # Count windash usage in TOO_NARROW rules
                    if "windash" in text.lower():
                        extra_counts["windash_in_too_narrow"][cfg_key] += 1

                    # Find blocking conditions
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
                                    blockers.append({
                                        "field_spec": fspec,
                                        "val": str(v),
                                        "cls": cls,
                                    })

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

                    tn_rules.append({
                        "tech": tech,
                        "repeat": repeat,
                        "shown": shown["CommandLine"],
                        "variant": variant["CommandLine"],
                        "blockers": blockers,
                        "det_block": det_block_str,
                    })

            # Tally classifications
            main_classes = defaultdict(int)
            any_classes = defaultdict(int)
            tech_counts = defaultdict(int)
            class_examples = defaultdict(list)

            for r in tn_rules:
                tech_counts[r["tech"]] += 1
                if r["blockers"]:
                    main_c = r["blockers"][0]["cls"]
                    main_classes[main_c] += 1
                    seen_in_rule = set()
                    for b in r["blockers"]:
                        c = b["cls"]
                        seen_in_rule.add(c)
                        if len(class_examples[c]) < 3:
                            # Avoid duplicates of same tech in examples if possible
                            if not any(ex["tech"] == r["tech"] and ex["val"] == b["val"] for ex in class_examples[c]):
                                class_examples[c].append({
                                    "tech": r["tech"],
                                    "shown": r["shown"],
                                    "variant": r["variant"],
                                    "val": b["val"],
                                    "field": b["field_spec"],
                                    "det_block": r["det_block"],
                                })
                    for c in seen_in_rule:
                        any_classes[c] += 1

            analysis[cfg_key] = {
                "run_id": run_id,
                "total_tn": len(tn_rules),
                "main_classes": main_classes,
                "any_classes": any_classes,
                "top_techs": sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "class_examples": class_examples,
                "rules": tn_rules,
            }

    return analysis, extra_counts


def write_failure_modes_document(changes, analysis, extra_counts):
    """Write results/set1_failure_modes.md."""
    out_path = os.path.join(REPO_ROOT, "results", "set1_failure_modes.md")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("# Set 1 Failure Modes and Generalisation Analysis\n\n")

        # -------------------------------------------------------------
        # Section 1
        # -------------------------------------------------------------
        out.write("## Section 1: Differences Between Shown Lines and Hidden Variants\n\n")
        out.write("For each of the 12 set 1 techniques, the attack was evaluated with a shown command line and a hidden variant line.\n\n")
        for c in changes:
            out.write(f"### {c['tech']}\n\n")
            out.write(f"- Program image: `{c['image']}`\n")
            if c["variant_image"] != c["image"]:
                out.write(f"- Variant program image: `{c['variant_image']}` (different program name)\n")
            out.write(f"- Shown command line: `{c['shown']}`\n")
            out.write(f"- Variant command line: `{c['variant']}`\n")
            out.write(f"- Tokens only in shown line: `{c['only_shown']}`\n")
            out.write(f"- Tokens only in variant line: `{c['only_variant']}`\n")
            out.write(f"- Applicable differences: **{', '.join(c['applies'])}**\n\n")

        # -------------------------------------------------------------
        # Section 2
        # -------------------------------------------------------------
        out.write("## Section 2: Failure Modes Classification\n\n")
        out.write("Every TOO_NARROW rule caught the shown attack line but failed the hidden variant line. Each blocking condition was tested alone using the validator SQLite conversion code and classified under the first matching class:\n\n")
        out.write("1. `ALIAS_IMAGE`: an Image or OriginalFileName condition fails on the variant because the executable name differs.\n")
        out.write("2. `VALUE`: the value contains an IPv4 address, a URL, a drive path, a filename with extension, >=3 digits, or a token unique to the shown line.\n")
        out.write("3. `FLAG_INCIDENTAL`: the value is a command-line flag present in the shown line but absent in the variant line.\n")
        out.write("4. `ADJACENT`: two or more words where every word exists in the variant line, but not adjacent in that specific sequence.\n")
        out.write("5. `PREFIX`: a flag whose prefix (- versus /) differs from the variant and the rule does not use windash.\n")
        out.write("6. `OTHER`: any other blocking condition.\n\n")

        # Tables for v2_1, then v2, then v1
        prompt_groups = [
            ("Prompt v3b (Run 20261111_1413, Temp 0.2, 3 Repeats)", ["v3b"]),
            ("Prompt v3a (Run 20261111_1403, Temp 0.2, 3 Repeats)", ["v3a"]),
            ("Prompt v2_1 (Frozen Candidates, Run 20261106_1344, Temp 0.2, 3 Repeats)", ["v2_1"]),
            ("Prompt v2 (Run 20261104_1503, Temp 0.2, 3 Repeats)", ["v2"]),
            ("Prompt v1 (Baseline, Run 20261021_1528, Temp 0.2, 3 Repeats)", ["v1"]),
        ]

        classes_order = ["ALIAS_IMAGE", "VALUE", "FLAG_INCIDENTAL", "ADJACENT", "PREFIX", "OTHER"]

        for title, p_list in prompt_groups:
            out.write(f"### {title}\n\n")
            for p_ver in p_list:
                for model in MODELS:
                    cfg = analysis.get((model, p_ver))
                    if not cfg:
                        continue
                    tot = cfg["total_tn"]
                    out.write(f"#### {model} under prompt {p_ver} ({tot} TOO_NARROW rules)\n\n")

                    # Counts table
                    out.write("| Classification | Rules with this Blocker (Any) | Primary Blocker (First Match) | Share of Rules (Any) |\n")
                    out.write("| --- | ---: | ---: | ---: |\n")
                    for cls_name in classes_order:
                        any_cnt = cfg["any_classes"].get(cls_name, 0)
                        main_cnt = cfg["main_classes"].get(cls_name, 0)
                        pct = f"{(any_cnt / tot * 100):.1f}%" if tot > 0 else "0.0%"
                        out.write(f"| {cls_name} | {any_cnt} | {main_cnt} | {pct} |\n")

                    # Top 5 techniques
                    top_techs_str = ", ".join(f"{t}: {cnt}" for t, cnt in cfg["top_techs"])
                    out.write(f"\n**Top 5 techniques with most TOO_NARROW rules**: {top_techs_str}\n\n")

                    # 3 real examples per class
                    out.write("##### Examples by Failure Class\n\n")
                    for cls_name in classes_order:
                        ex_list = cfg["class_examples"].get(cls_name, [])
                        if not ex_list:
                            continue
                        out.write(f"**Class: {cls_name}** ({len(ex_list)} examples shown):\n\n")
                        for i, ex in enumerate(ex_list[:3], 1):
                            out.write(f"- Example {i} ({ex['tech']}):\n")
                            out.write(f"  - Shown line: `{ex['shown']}`\n")
                            out.write(f"  - Variant line: `{ex['variant']}`\n")
                            out.write(f"  - Blocking condition: `{ex['field']}: {ex['val']}`\n")
                            out.write("  - Detection block written by model:\n```yaml\n")
                            out.write(ex["det_block"].strip() + "\n```\n\n")

        # -------------------------------------------------------------
        # Section 3
        # -------------------------------------------------------------
        out.write("## Section 3: Extra Observations\n\n")
        out.write("### 1. Windash Modifier Usage in TOO_NARROW Rules\n\n")
        out.write("Count of TOO_NARROW rules that used the `windash` modifier anywhere in their YAML:\n\n")
        out.write("| Model | Prompt | Total TOO_NARROW | Uses Windash | Percentage |\n")
        out.write("| --- | --- | ---: | ---: | ---: |\n")
        for p_ver in ["v3b", "v3a", "v2_1", "v2", "v1"]:
            for model in MODELS:
                cfg = analysis.get((model, p_ver))
                tot = cfg["total_tn"] if cfg else 0
                w_cnt = extra_counts["windash_in_too_narrow"][(model, p_ver)]
                pct = f"{(w_cnt / tot * 100):.1f}%" if tot > 0 else "0.0%"
                out.write(f"| {model} | {p_ver} | {tot} | {w_cnt} | {pct} |\n")

        out.write("\n### 2. Value Padded with Spaces\n\n")
        out.write("Count of all rules in the run having at least one selection value that starts or ends with a space:\n\n")
        out.write("| Model | Prompt | Total Rules | Rules with Padded Value | Percentage |\n")
        out.write("| --- | --- | ---: | ---: | ---: |\n")
        for p_ver in ["v3b", "v3a", "v2_1", "v2", "v1"]:
            for model in MODELS:
                p_cnt = extra_counts["padded_space"][(model, p_ver)]
                pct = f"{(p_cnt / 36 * 100):.1f}%"
                out.write(f"| {model} | {p_ver} | 36 | {p_cnt} | {pct} |\n")

        out.write("\n### 3. Image Check Plus Single Keyword Rule Generalisation\n\n")
        out.write("Rules that use only an Image check plus a single CommandLine keyword value, and their strict pass rate:\n\n")
        out.write("| Model | Prompt | Total Rules | Keyword-Only Rules | Strict Passes | Strict Pass Rate |\n")
        out.write("| --- | --- | ---: | ---: | ---: | ---: |\n")
        for p_ver in ["v3b", "v3a", "v2_1", "v2", "v1"]:
            for model in MODELS:
                kw_cnt = extra_counts["keyword_only_rules"][(model, p_ver)]
                kw_pass = extra_counts["keyword_only_strict_pass"][(model, p_ver)]
                pct = f"{(kw_pass / kw_cnt * 100):.1f}%" if kw_cnt > 0 else "N/A"
                out.write(f"| {model} | {p_ver} | 36 | {kw_cnt} | {kw_pass} | {pct} |\n")

    print(f"Written {out_path}")


def main():
    print("=== STEP 1: Strict Summary for Set 1 ===")
    summary_3rep = step1_strict_summary()

    print("\n=== STEP 2: Technique Changes Analysis ===")
    changes = step2_technique_changes()
    print(f"Analyzed {len(changes)} techniques.")

    print("\n=== STEP 3 & 4: Failure Modes and Extra Counts ===")
    analysis, extra_counts = step3_and_step4_failure_modes()

    print("\n=== STEP 5: Writing results/set1_failure_modes.md ===")
    write_failure_modes_document(changes, analysis, extra_counts)

    print("\n=== SUMMARY OF KEY FINDINGS ===")
    for p_ver in ["v3b", "v3a", "v2_1", "v2", "v1"]:
        for model in MODELS:
            cfg = analysis.get((model, p_ver))
            if not cfg:
                continue
            tot = cfg["total_tn"]
            main_c = cfg["main_classes"]
            print(f"[{model} | {p_ver}] TOO_NARROW={tot} | Main breakdown: {dict(main_c)}")


if __name__ == "__main__":
    main()
