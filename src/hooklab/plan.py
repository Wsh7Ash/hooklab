"""Hook plan rules, grading and report rendering.

A hook plan is a claim that instrumenting a function is both safe and useful.
The rules check the parts researchers skip: why the hook exists, what proves it
fired, how the target is cleaned up afterwards, and whether the plan admits it
runs inside a live process.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "hooklab/v1"
RISKS = ("read-only", "intrusive")
EVENTS = ("call", "return", "enter", "leave")

BLOCKING = "blocking"
MAJOR = "major"
MINOR = "minor"
PENALTY = {BLOCKING: 25, MAJOR: 10, MINOR: 3}


class PlanError(RuntimeError):
    """Raised when a hook plan cannot be read."""


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    hint: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"rule": self.rule, "severity": self.severity, "message": self.message, "hint": self.hint}


@dataclass
class Report:
    plan_id: str
    score: int
    grade: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocking(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == BLOCKING]

    @property
    def submittable(self) -> bool:
        return not self.blocking

    def as_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan_id,
            "score": self.score,
            "grade": self.grade,
            "submittable": self.submittable,
            "findings": [f.as_dict() for f in self.findings],
        }


def load_plan(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PlanError(f"plan not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PlanError(f"plan is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PlanError("plan must be a JSON object")
    return data


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _hooks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _items(plan.get("hooks")) if isinstance(item, dict)]


def _native(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _items(plan.get("native")) if isinstance(item, dict)]


def grade(plan: dict[str, Any], root: Path | None = None) -> Report:
    findings: list[Finding] = []

    def add(rule: str, severity: str, message: str, hint: str = "") -> None:
        findings.append(Finding(rule, severity, message, hint))

    if _text(plan.get("schema")) != SCHEMA:
        add("schema", BLOCKING, f"plan schema must be {SCHEMA!r}")

    plan_id = _text(plan.get("id")) or "unnamed"
    if not _text(plan.get("id")):
        add("id", MAJOR, "plan has no stable id")
    if len(_text(plan.get("objective"))) < 20:
        add(
            "objective",
            MAJOR,
            "objective is missing or too short",
            "State the question the hook answers; a hook without a question is surveillance.",
        )
    if not _text(plan.get("scope_ref")):
        add("scope-ref", BLOCKING, "plan has no scope reference for the target")

    risk = _text(plan.get("risk")).lower()
    if risk not in RISKS:
        add("risk", MAJOR, f"risk must be one of {RISKS}")

    cleanup = [item for item in _items(plan.get("cleanup")) if _text(item)]
    if risk == "intrusive" and not cleanup:
        add(
            "cleanup",
            BLOCKING,
            "intrusive plan declares no cleanup",
            "Say how the hook is removed and how the process is returned to its original state.",
        )

    hooks = _hooks(plan)
    if not hooks:
        add("hooks", BLOCKING, "plan declares no hooks")
    targets = set()
    for index, hook in enumerate(hooks, start=1):
        target = _text(hook.get("target"))
        if not target:
            add("hook-target", BLOCKING, f"hook {index} has no target")
            continue
        targets.add(target)
        if len(_text(hook.get("why"))) < 15:
            add(
                "hook-why",
                MAJOR,
                f"hook {index} ({target}) does not say why it exists",
                "Name the value this hook reveals that no other observation provides.",
            )
        event = _text(hook.get("event")) or "call"
        if event not in EVENTS:
            add("hook-event", MAJOR, f"hook {index} has unknown event {event!r}")
        if not [name for name in _items(hook.get("capture")) if _text(name)]:
            add("hook-capture", MINOR, f"hook {index} ({target}) captures no named value")

    exercise = plan.get("exercise")
    if not isinstance(exercise, dict) or not _text(exercise.get("function")):
        add(
            "exercise",
            BLOCKING,
            "no exercise call, so nothing proves the hook fires",
            "Give the function and JSON arguments that reach the hook.",
        )
    else:
        if not isinstance(exercise.get("args", []), list):
            add("exercise-args", MAJOR, "exercise args must be a list")
        if not isinstance(exercise.get("kwargs", {}), dict):
            add("exercise-kwargs", MAJOR, "exercise kwargs must be an object")

    module = _text(plan.get("module"))
    if not module:
        add(
            "module",
            MAJOR,
            "plan names no module for the Python hooks",
            "Native-only plans can still run emit; a runnable plan needs a module.",
        )
    elif root is not None:
        candidate = Path(module)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.is_file():
            add("module-exists", BLOCKING, f"module does not exist: {module}")

    expect = [item for item in _items(plan.get("expect")) if isinstance(item, dict)]
    if not expect:
        add("expect", BLOCKING, "no expectations, so the hook cannot be verified")
    for index, rule in enumerate(expect, start=1):
        target = _text(rule.get("target"))
        if target not in targets:
            add(
                "expect-target",
                MAJOR,
                f"expectation {index} targets {target!r}, which no hook records",
            )
        if not [name for name in _items(rule.get("has")) if _text(name)] and not _items(
            rule.get("absent")
        ):
            add("expect-values", MAJOR, f"expectation {index} asserts nothing")

    for index, item in enumerate(_native(plan), start=1):
        if not _text(item.get("library")):
            add("native-library", MAJOR, f"native hook {index} names no library")
        if not _text(item.get("symbol")):
            add("native-symbol", BLOCKING, f"native hook {index} names no symbol")

    penalty = sum(PENALTY[f.severity] for f in findings)
    score = max(0, 100 - penalty)
    if any(f.severity == BLOCKING for f in findings):
        letter = "D"
    elif score >= 90:
        letter = "A"
    elif score >= 75:
        letter = "B"
    elif score >= 55:
        letter = "C"
    else:
        letter = "D"

    return Report(plan_id, score, letter, findings)


def scaffold(title: str, plan_id: str = "new-hook") -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "id": plan_id,
        "title": title,
        "objective": "",
        "scope_ref": "",
        "risk": "read-only",
        "module": "",
        "hooks": [
            {"target": "", "event": "call", "capture": [], "why": ""}
        ],
        "exercise": {"function": "", "args": []},
        "expect": [],
        "native": [],
        "cleanup": [],
        "reproduction": {"command": ""},
    }


def render_report(plan: dict[str, Any], report: Report) -> str:
    lines = [
        f"# {_text(plan.get('title')) or report.plan_id}",
        "",
        f"**Plan:** `{report.plan_id}`  ",
        f"**Scope reference:** {_text(plan.get('scope_ref')) or '(none)'}  ",
        f"**Risk:** {_text(plan.get('risk'))}",
        "",
        "## Objective",
        "",
        _text(plan.get("objective")) or "(none)",
        "",
        "## Hooks",
        "",
        "| # | Target | Event | Captures | Why |",
        "|---|---|---|---|---|",
    ]
    for index, hook in enumerate(_hooks(plan), start=1):
        captures = ", ".join(str(name) for name in _items(hook.get("capture"))) or "-"
        lines.append(
            f"| {index} | `{_text(hook.get('target'))}` | {_text(hook.get('event')) or 'call'} "
            f"| {captures} | {_text(hook.get('why'))} |"
        )
    lines += ["", "## Verification", ""]
    for rule in _items(plan.get("expect")):
        if isinstance(rule, dict):
            lines.append(
                f"- `{rule.get('target')}` on {rule.get('event', 'call')}: "
                f"{', '.join(str(n) for n in _items(rule.get('has'))) or 'no values'}"
            )
    lines += [
        "",
        "## Cleanup",
        "",
    ]
    lines += [f"- {item}" for item in _items(plan.get("cleanup"))] or ["- (none declared)"]
    lines += [
        "",
        "## Reproduction",
        "",
        "```text",
        _text((plan.get("reproduction") or {}).get("command")) or "(none)",
        "```",
        "",
        "## Plan grade",
        "",
        f"- Grade: **{report.grade}** ({report.score}/100), submittable: "
        f"{'yes' if report.submittable else 'no'}",
    ]
    for finding in report.findings:
        lines.append(f"- `{finding.severity}` {finding.rule}: {finding.message}")
    lines.append("")
    return "\n".join(lines)
