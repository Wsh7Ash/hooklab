"""hooklab command line interface.

Corpus commands (validate / list / show / search / build) come from the pack
harness. The domain commands make a hook plan executable:

    hooklab check plan.json
    hooklab run plan.json --json
    hooklab emit plan.json --format frida --out agent.js
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .corpus import BY_SLUG, PACK, SKILLS
from .hooks import (
    EmitError,
    HookError,
    check_expectations,
    emit_frida,
    emit_gdb,
    emit_preload,
    load_module,
    run_exercise,
)
from .plan import PlanError, grade, load_plan, render_report, scaffold
from .render import build_pack, render_skill
from .validate import (
    MAX_DESCRIPTION,
    MIN_DONE,
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_SUMMARY,
    MIN_WORDS,
    Issue,
    validate_pack,
)

FLOORS = {
    "min_steps": MIN_STEPS,
    "min_signals": MIN_SIGNALS,
    "min_patterns": MIN_PATTERNS,
    "min_pitfalls": MIN_PITFALLS,
    "min_done_when": MIN_DONE,
    "min_summary_chars": MIN_SUMMARY,
    "min_words": MIN_WORDS,
    "max_description_chars": MAX_DESCRIPTION,
}

EMITTERS = {"frida": emit_frida, "gdb": emit_gdb, "preload": emit_preload}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _report(issues: list[Issue], total: int, as_json: bool, title: str) -> int:
    bad = {issue.slug for issue in issues if issue.slug}
    valid = total - len(bad)
    if as_json:
        print(
            json.dumps(
                {
                    "pack": title,
                    "checked": total,
                    "valid": valid,
                    "passed": not issues,
                    "floors": FLOORS,
                    "issues": [{"slug": i.slug, "rule": i.rule, "message": i.message} for i in issues],
                },
                indent=2,
            )
        )
    else:
        print(f"{title}: {valid}/{total} skills valid")
        for issue in issues:
            print(f"  FAIL {issue}")
        if not issues:
            print(
                f"  ok  steps>={MIN_STEPS} signals>={MIN_SIGNALS} patterns>={MIN_PATTERNS} "
                f"pitfalls>={MIN_PITFALLS} words>={MIN_WORDS} refs canonical https"
            )
    return 0 if not issues else 1


def cmd_validate(args: argparse.Namespace) -> int:
    return _report(validate_pack(PACK, SKILLS), len(SKILLS), args.json, PACK["name"])


def cmd_list(args: argparse.Namespace) -> int:
    rows = [
        skill
        for skill in SKILLS
        if (not args.tag or args.tag in skill.tags)
        and (not args.phase or skill.meta_get("phase") == args.phase)
    ]
    if args.json:
        print(
            json.dumps(
                [
                    {"slug": s.slug, "title": s.title, "phase": s.meta_get("phase"), "tags": list(s.tags)}
                    for s in rows
                ],
                indent=2,
            )
        )
        return 0
    for skill in rows:
        print(f"{skill.meta_get('phase'):11s} {skill.slug:38s} {skill.title}")
    print(f"# {len(rows)} skill(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    skill = BY_SLUG.get(args.slug)
    if skill is None:
        print(f"unknown skill: {args.slug}", file=sys.stderr)
        return 2
    text = render_skill(PACK, skill)
    print(text if args.raw else text.split("---\n", 2)[-1].lstrip())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    terms = [term.lower() for term in args.terms]

    def score(skill) -> int:
        blob = " ".join([skill.slug, skill.title, skill.summary, *skill.tags, *skill.steps]).lower()
        return sum(blob.count(term) for term in terms)

    ranked = sorted(
        ((score(skill), skill) for skill in SKILLS if score(skill)),
        key=lambda pair: (-pair[0], pair[1].slug),
    )[: args.limit]
    if not ranked:
        print("no matches", file=sys.stderr)
        return 1
    for points, skill in ranked:
        print(f"{points:3d}  {skill.slug:38s} {skill.title}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else repo_root()
    written = build_pack(root, PACK, SKILLS)
    print(f"wrote {len(written)} file(s) under {root}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(Path(args.plan))
    except PlanError as exc:
        print(f"cannot read plan: {exc}", file=sys.stderr)
        return 2
    report = grade(plan, Path.cwd())
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        verdict = "submittable" if report.submittable else "NOT submittable"
        print(f"{report.plan_id}: grade {report.grade} ({report.score}/100) {verdict}")
        for finding in report.findings:
            print(f"  {finding.severity:8s} {finding.rule}: {finding.message}")
            if finding.hint and args.verbose:
                print(f"           -> {finding.hint}")
    return 0 if report.submittable else 1


def cmd_run(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(Path(args.plan))
    except PlanError as exc:
        print(f"cannot read plan: {exc}", file=sys.stderr)
        return 2

    module_name = str(plan.get("module") or "")
    if not module_name:
        print("plan has no module, so there is nothing to run", file=sys.stderr)
        return 2
    try:
        module = load_module(Path(module_name))
        result = run_exercise(module, plan.get("hooks") or [], plan.get("exercise") or {})
    except HookError as exc:
        print(f"cannot run plan: {exc}", file=sys.stderr)
        return 2

    problems = check_expectations(result.captures, plan.get("expect") or [])
    if args.json:
        print(
            json.dumps(
                {
                    "plan": plan.get("id", "unnamed"),
                    "returned": result.returned,
                    "truncated": result.truncated,
                    "captures": [capture.as_dict() for capture in result.captures],
                    "problems": problems,
                    "passed": not problems,
                },
                indent=2,
            )
        )
    else:
        print(f"returned: {result.returned}")
        for capture in result.captures:
            pairs = " ".join(f"{name}={value}" for name, value in capture.values.items())
            print(f"{capture.event:6s} {capture.target:24s} {pairs}")
        if result.truncated:
            print("# capture limit reached; later events were dropped")
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"# {len(result.captures)} capture(s), {'PASS' if not problems else 'FAIL'}")
    return 0 if not problems else 1


def cmd_emit(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(Path(args.plan))
    except PlanError as exc:
        print(f"cannot read plan: {exc}", file=sys.stderr)
        return 2
    emitter = EMITTERS[args.format]
    try:
        text = emitter(plan)
    except EmitError as exc:
        print(f"cannot emit: {exc}", file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


def cmd_scaffold(args: argparse.Namespace) -> int:
    plan = scaffold(args.title, args.id)
    text = json.dumps(plan, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(Path(args.plan))
    except PlanError as exc:
        print(f"cannot read plan: {exc}", file=sys.stderr)
        return 2
    report = grade(plan, Path.cwd())
    text = render_report(plan, report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0 if report.submittable else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PACK["name"], description=PACK["description"])
    parser.add_argument("--version", action="version", version=f"{PACK['name']} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run every corpus rule")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--tag", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print one SKILL.md")
    p.add_argument("slug")
    p.add_argument("--raw", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="rank skills by keyword")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("build", help="regenerate skills/, pack.json and results/")
    p.add_argument("--root", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("check", help="grade a hook plan")
    p.add_argument("plan")
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("run", help="execute the plan's exercise under the tracer")
    p.add_argument("plan")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("emit", help="generate a Frida, GDB or LD_PRELOAD hook script")
    p.add_argument("plan")
    p.add_argument("--format", default="frida", choices=sorted(EMITTERS))
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_emit)

    p = sub.add_parser("scaffold", help="emit an empty hook plan")
    p.add_argument("title")
    p.add_argument("--id", default="new-hook")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_scaffold)

    p = sub.add_parser("report", help="render plan markdown")
    p.add_argument("plan")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
