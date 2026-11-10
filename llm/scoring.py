"""
Unified scoring module for ATIDEP Sigma detection rules.
Evaluates rules across all sets (1, 2, 3) using a single consistent interface.
"""
import os
import sys

# Ensure validator and generator directories are on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for sub in ("validator", "generator"):
    p = os.path.join(REPO_ROOT, sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from runner import rule_to_sql, rule_matches
from generate import make_triple as make_triple_set1
from techniques_set2 import make_triple as make_triple_set2
from techniques_set3 import make_triple3 as make_triple_set3


class ScoreResult:
    __slots__ = (
        "syntax_ok", "fires_shown", "fires_variant", "fires_benign",
        "single_pass", "strict_pass", "verdict", "error"
    )

    def __init__(self, syntax_ok, fires_shown, fires_variant, fires_benign,
                 single_pass, strict_pass, verdict, error=""):
        self.syntax_ok = bool(syntax_ok)
        self.fires_shown = bool(fires_shown)
        self.fires_variant = bool(fires_variant)
        self.fires_benign = bool(fires_benign)
        self.single_pass = bool(single_pass)
        self.strict_pass = bool(strict_pass)
        self.verdict = verdict
        self.error = error

    def __iter__(self):
        yield self.syntax_ok
        yield self.fires_shown
        yield self.fires_variant
        yield self.fires_benign
        yield self.single_pass
        yield self.strict_pass
        yield self.verdict

    def __getitem__(self, item):
        if isinstance(item, int):
            return tuple(self)[item]
        return getattr(self, item)

    def __len__(self):
        return 7

    def __repr__(self):
        return (f"ScoreResult(syntax_ok={self.syntax_ok}, fires_shown={self.fires_shown}, "
                f"fires_variant={self.fires_variant}, fires_benign={self.fires_benign}, "
                f"single_pass={self.single_pass}, strict_pass={self.strict_pass}, "
                f"verdict='{self.verdict}')")


def score_rule(set_id, technique, rule_text):
    """
    Score a rule text against shown, variant, and benign events.

    Returns:
        syntax_ok, fires_shown, fires_variant, fires_benign, single_pass, strict_pass, verdict
    """
    set_num = int(set_id)
    syntax_error = ""
    try:
        rule_to_sql(rule_text)
        syntax_ok = True
    except Exception as e:
        syntax_ok = False
        syntax_error = str(e)[:150]

    if not syntax_ok:
        return ScoreResult(
            syntax_ok=False,
            fires_shown=False,
            fires_variant=False,
            fires_benign=False,
            single_pass=False,
            strict_pass=False,
            verdict="SYNTAX_ERROR",
            error=syntax_error,
        )

    if set_num == 1:
        shown, variant, benign = make_triple_set1(technique)
    elif set_num == 2:
        shown, variant, benign = make_triple_set2(technique)
    elif set_num == 3:
        shown, variant, benign = make_triple_set3(technique)
    else:
        raise ValueError(f"Unknown set_id: {set_id}")

    fires_shown = bool(rule_matches(rule_text, shown))
    fires_variant = bool(rule_matches(rule_text, variant))
    fires_benign = bool(rule_matches(rule_text, benign))

    single_pass = syntax_ok and fires_shown and not fires_benign
    strict_pass = single_pass and fires_variant

    if not syntax_ok:
        verdict = "SYNTAX_ERROR"
        error = syntax_error
    elif not fires_shown:
        verdict = "MISSED_SHOWN"
        error = "missed the shown attack"
    elif fires_benign:
        verdict = "NOISY"
        error = "fired on harmless benign line"
    elif not fires_variant:
        verdict = "TOO_NARROW"
        error = "too narrow: caught the shown attack but missed the hidden variant"
    else:
        verdict = "PASS"
        error = ""

    return ScoreResult(
        syntax_ok=syntax_ok,
        fires_shown=fires_shown,
        fires_variant=fires_variant,
        fires_benign=fires_benign,
        single_pass=single_pass,
        strict_pass=strict_pass,
        verdict=verdict,
        error=error,
    )
