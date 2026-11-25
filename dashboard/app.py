"""ATIDEP Dashboard - Flask application.

Run with: python dashboard/app.py
Open: http://127.0.0.1:5000
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Flask, jsonify, render_template, request, send_from_directory

from dashboard.data_loader import (
    load_overview,
    load_runs,
    load_run_detail,
    load_tactic_coverage,
    load_techniques,
    load_technique_detail,
    load_prompt_comparison,
    load_rule_text,
)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)


FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")


# ---- HTML pages ----

@app.route("/app")
@app.route("/app/")
@app.route("/app/<path:path>")
def serve_react_app(path=""):
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return "React frontend build not found. Run: npm --prefix dashboard/frontend run build", 404

@app.route("/")
def page_overview():
    return render_template("overview.html")


@app.route("/coverage")
def page_coverage():
    return render_template("coverage_map.html")


@app.route("/technique/<technique_id>")
def page_technique(technique_id):
    return render_template("technique.html", technique_id=technique_id)


@app.route("/runs")
def page_runs():
    return render_template("runs.html")


@app.route("/run/<folder>")
def page_run_detail(folder):
    return render_template("run_detail.html", folder=folder)


@app.route("/gate")
def page_gate():
    return render_template("gate_tester.html")


@app.route("/pipeline")
def page_pipeline():
    return render_template("pipeline.html")


# ---- API endpoints ----

@app.route("/api/overview")
def api_overview():
    return jsonify(load_overview())


@app.route("/api/tactics")
def api_tactics():
    return jsonify(load_tactic_coverage())


@app.route("/api/techniques")
def api_techniques():
    techniques = load_techniques()
    # Strip configs for the list view (too large)
    result = []
    for tid, tech in sorted(techniques.items()):
        entry = {k: v for k, v in tech.items() if k != "configs"}
        # Count configs
        entry["num_configs"] = len(tech["configs"])
        # Count passes
        entry["num_pass"] = sum(1 for c in tech["configs"].values() if c["strict_pass"])
        result.append(entry)
    return jsonify(result)


@app.route("/api/technique/<technique_id>")
def api_technique(technique_id):
    detail = load_technique_detail(technique_id)
    if not detail:
        return jsonify({"error": "Technique not found"}), 404
    return jsonify(detail)


@app.route("/api/runs")
def api_runs():
    runs = load_runs()
    # Strip full results for the list view
    result = []
    for run in runs:
        entry = {k: v for k, v in run.items() if k != "results"}
        result.append(entry)
    return jsonify(result)


@app.route("/api/run/<folder>")
def api_run(folder):
    detail = load_run_detail(folder)
    if not detail:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(detail)


@app.route("/api/comparison")
def api_comparison():
    return jsonify(load_prompt_comparison())


@app.route("/api/rule/<folder>/<model>/<technique>/<int:repeat>")
def api_rule(folder, model, technique, repeat):
    text = load_rule_text(folder, model, technique, repeat)
    if text is None:
        return jsonify({"error": "Rule not found"}), 404
    return jsonify({"rule_text": text})


@app.route("/api/gate", methods=["POST"])
def api_gate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    rule_yaml = data.get("rule_yaml", "")
    try:
        set_id = int(data.get("set", 1))
    except (ValueError, TypeError):
        set_id = 1
    technique = (data.get("technique") or "").strip()
    if not rule_yaml or not technique:
        return jsonify({"error": "Missing rule_yaml or technique"}), 400
    try:
        from llm.scoring import score_rule
        res = score_rule(set_id, technique, rule_yaml)
        # Load test events
        from dashboard.data_loader import load_technique_detail
        detail = load_technique_detail(technique)
        events = detail.get("events", {}).get(str(set_id), {}) if detail else {}

        reason = res.error
        if not reason:
            if res.verdict == "PASS":
                reason = "Caught shown attack and hidden variant, quiet on harmless near-miss line"
            elif res.verdict == "TOO_NARROW":
                reason = "Caught shown line but missed hidden evasion variant"
            elif res.verdict == "NOISY":
                reason = "Fired on harmless near-miss baseline commands"
            elif res.verdict == "MISSED_SHOWN":
                reason = "Missed the shown attack line"
            elif res.verdict == "SYNTAX_ERROR":
                reason = f"Syntax error: {res.error}"

        return jsonify({
            "syntax_ok": res.syntax_ok,
            "fires_shown": res.fires_shown,
            "fires_variant": res.fires_variant,
            "fires_benign": res.fires_benign,
            "single_pass": res.single_pass,
            "strict_pass": res.strict_pass,
            "verdict": res.verdict,
            "error": res.error,
            "reason": reason,
            "events": events,
        })
    except Exception as e:
        return jsonify({"error": str(e), "reason": f"Evaluation error: {str(e)}"}), 500


@app.route("/api/pipeline", methods=["POST"])
@app.route("/api/pipeline/run", methods=["POST"])
def api_pipeline():
    """Run the CTI-to-Detection pipeline on input threat report."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    report_text = data.get("text") or data.get("report_text") or ""
    if not report_text.strip():
        return jsonify({"error": "Missing report text"}), 400
    try:
        from dashboard.pipeline_service import run_pipeline
        result = run_pipeline(report_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sets")
def api_sets():
    """Return available sets and their technique lists."""
    from generator.generate import TECHNIQUES as T1
    from generator.techniques_set2 import TECHNIQUES2 as T2
    from generator.techniques_set3 import TECHNIQUES3 as T3
    return jsonify({
        "1": sorted(T1.keys()),
        "2": sorted(T2.keys()),
        "3": sorted(T3.keys()),
    })


# ---- TAXII ingestion endpoints ----

@app.route("/api/taxii/status")
def api_taxii_status():
    """Check whether the TAXII server is reachable."""
    try:
        from data.taxii_connector import fetch_objects
        objs = fetch_objects(timeout=15)
        return jsonify({"status": "connected", "techniques": len(objs)})
    except Exception as e:
        return jsonify({"status": "unavailable", "error": str(e)})


@app.route("/api/taxii/groups")
def api_taxii_groups():
    """List threat groups and how many of their techniques we can cover."""
    try:
        from data.taxii_ingest import ingest_all_groups
        groups = ingest_all_groups(timeout=30)
        if groups is None:
            return jsonify({"error": "TAXII server unreachable"}), 503
        return jsonify(groups)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/taxii/ingest", methods=["POST"])
def api_taxii_ingest():
    """Ingest techniques for a threat group from TAXII.

    Request body: {"group": "APT29"}
    Returns the group's techniques filtered to what our pipeline supports.
    """
    data = request.get_json()
    if not data or not data.get("group"):
        return jsonify({"error": "Missing 'group' in request body"}), 400
    try:
        from data.taxii_ingest import ingest_by_group
        result = ingest_by_group(data["group"], timeout=30)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/taxii/refresh", methods=["POST"])
def api_taxii_refresh():
    """Pull latest ATT&CK data from TAXII and update the local lookup."""
    try:
        from data.taxii_connector import fetch_objects, update_lookup
        objects = fetch_objects(timeout=60)
        new, old = update_lookup(objects, write=True)
        added = sorted(set(new) - set(old))
        removed = sorted(set(old) - set(new))
        return jsonify({
            "status": "updated",
            "total": len(new),
            "added": len(added),
            "removed": len(removed),
            "added_ids": added[:20],
        })
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 503


# ---- Rule export endpoints ----

@app.route("/api/export", methods=["POST"])
def api_export():
    """Convert a Sigma rule to another format (splunk, kql, sqlite).

    Request body: {"rule_yaml": "...", "format": "splunk"}
    Optional: {"format": "all"} returns all formats at once.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    rule_yaml = data.get("rule_yaml", "")
    fmt = data.get("format", "splunk")
    if not rule_yaml.strip():
        return jsonify({"error": "Missing rule_yaml"}), 400
    try:
        from export.rule_export import convert, convert_all, FORMATS
        if fmt == "all":
            results = convert_all(rule_yaml)
            return jsonify({"formats": results})
        if fmt not in FORMATS:
            return jsonify({"error": f"Unknown format: {fmt}. Supported: {', '.join(FORMATS)}"}), 400
        converted = convert(rule_yaml, fmt)
        return jsonify({"format": fmt, "result": converted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/formats")
def api_export_formats():
    """List available export formats."""
    from export.rule_export import FORMATS
    return jsonify(FORMATS)


# ---- IOC extraction endpoint ----

@app.route("/api/ioc/extract", methods=["POST"])
def api_ioc_extract():
    """Extract IOCs (IPs, domains, URLs, hashes) from text.

    Request body: {"text": "..."}
    Returns: {"ipv4": [...], "domains": [...], "urls": [...], "hashes": [...]}
    """
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify({"error": "Missing text"}), 400
    try:
        from export.ioc_extract import extract_iocs, has_iocs
        iocs = extract_iocs(data["text"])
        iocs["has_iocs"] = has_iocs(iocs)
        return jsonify(iocs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---- Prioritisation endpoints ----

@app.route("/api/priority-backlog")
def api_priority_backlog():
    """Return the threat-informed priority backlog.

    Optional query params:
        limit: max rows to return (default 100, 0 for all)
        filter: "uncovered", "in_pipeline", "all" (default "all")
    """
    try:
        from export.prioritisation import build_priority_backlog
        result = build_priority_backlog(timeout=15)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    filt = request.args.get("filter", "all")
    try:
        limit = int(request.args.get("limit", 100))
    except (ValueError, TypeError):
        limit = 100

    backlog = result["backlog"]
    if filt == "uncovered":
        backlog = [r for r in backlog if not r["covered"]]
    elif filt == "in_pipeline":
        backlog = [r for r in backlog if r["in_pipeline"]]

    if limit > 0:
        backlog = backlog[:limit]

    result["backlog"] = backlog
    return jsonify(result)


if __name__ == "__main__":
    print("Starting ATIDEP Dashboard at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

