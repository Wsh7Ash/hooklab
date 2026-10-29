"""Corpus, tracer, emitter and plan-grading tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hooklab.corpus import BY_SLUG, PACK, SKILLS  # noqa: E402
from hooklab.hooks import (  # noqa: E402
    EmitError,
    HookError,
    Tracer,
    check_expectations,
    emit_frida,
    emit_gdb,
    emit_preload,
    load_module,
    run_exercise,
)
from hooklab.plan import PlanError, grade, load_plan, render_report, scaffold  # noqa: E402
from hooklab.render import render_skill, word_count  # noqa: E402
from hooklab.validate import validate_pack  # noqa: E402

PLAN = ROOT / "examples" / "plan" / "password-capture.json"
TARGET = ROOT / "examples" / "target_app.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "hooklab", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=300,
    )


# ---------------------------------------------------------------- corpus shape


def test_pack_declares_fifty_and_delivers_fifty() -> None:
    assert PACK["expected_skills"] == 50
    assert len(SKILLS) == 50
    assert len({skill.slug for skill in SKILLS}) == 50
    assert len({skill.title.lower() for skill in SKILLS}) == 50


def test_every_skill_passes_the_strict_gate() -> None:
    assert validate_pack(PACK, SKILLS) == []


def test_phases_cover_a_hooking_session() -> None:
    phases = {skill.meta_get("phase") for skill in SKILLS}
    assert phases == {"resolve", "instrument", "hook", "capture", "verify", "teardown"}
    for phase in phases:
        assert len([skill for skill in SKILLS if skill.meta_get("phase") == phase]) >= 8


def test_skills_stay_substantial() -> None:
    for skill in SKILLS:
        assert word_count(render_skill(PACK, skill)) >= 180, skill.slug


def test_committed_skills_match_a_fresh_render() -> None:
    for skill in SKILLS:
        path = ROOT / "skills" / skill.slug / "SKILL.md"
        assert path.is_file(), f"missing {path}"
        assert path.read_text(encoding="utf-8") == render_skill(PACK, skill), skill.slug


def test_lookup_matches_corpus() -> None:
    assert set(BY_SLUG) == {skill.slug for skill in SKILLS}


# -------------------------------------------------------------------- tracer


def test_tracer_records_call_and_return() -> None:
    plan = load_plan(PLAN)
    module = load_module(TARGET)
    result = run_exercise(module, plan["hooks"], plan["exercise"])

    assert result.returned.startswith("{'ok': True")
    assert len(result.captures) == 2

    call = result.captures[0]
    assert call.event == "call"
    assert call.values["username"] == "'alice'"
    assert call.values["password"] == "'hunter2'"

    back = result.captures[1]
    assert back.event == "return"
    assert back.values["__return__"] == "True"


def test_expectations_pass_and_fail() -> None:
    plan = load_plan(PLAN)
    module = load_module(TARGET)
    result = run_exercise(module, plan["hooks"], plan["exercise"])
    assert check_expectations(result.captures, plan["expect"]) == []

    problems = check_expectations(
        result.captures, [{"target": "check_password", "event": "call", "has": ["nope"]}]
    )
    assert problems and "nope" in problems[0]

    problems = check_expectations(
        result.captures, [{"target": "missing_fn", "event": "call", "has": ["x"]}]
    )
    assert "no capture recorded" in problems[0]


def test_absent_expectation_detects_a_leak() -> None:
    plan = load_plan(PLAN)
    module = load_module(TARGET)
    result = run_exercise(module, plan["hooks"], plan["exercise"])
    problems = check_expectations(
        result.captures,
        [{"target": "check_password", "event": "call", "absent": ["password"]}],
    )
    assert problems and "should not have been captured" in problems[0]


def test_event_cap_truncates() -> None:
    plan = load_plan(PLAN)
    module = load_module(TARGET)
    tracer = Tracer(plan["hooks"], max_events=1)
    with tracer:
        module.login("alice", "hunter2")
    assert len(tracer.captures) == 1
    assert tracer.truncated is True


def test_tracer_restores_previous_profiler() -> None:
    previous = sys.getprofile()
    with Tracer([]):
        assert sys.getprofile() is not None
    assert sys.getprofile() is previous


def test_run_exercise_reports_target_exceptions() -> None:
    module = load_module(TARGET)
    result = run_exercise(module, [], {"function": "login", "args": ["nobody", "x"]})
    assert result.returned.startswith("{'ok': False")


def test_missing_module_and_function_raise(tmp_path: Path) -> None:
    with pytest.raises(HookError):
        load_module(tmp_path / "nope.py")
    module = load_module(TARGET)
    with pytest.raises(HookError):
        run_exercise(module, [], {"function": "does_not_exist", "args": []})
    with pytest.raises(HookError):
        run_exercise(module, [], {"function": ""})


# ------------------------------------------------------------------ emitters


def test_frida_and_gdb_emitters_use_the_plan_symbols() -> None:
    plan = load_plan(PLAN)
    frida = emit_frida(plan)
    assert "strcmp" in frida
    assert "Interceptor.attach" in frida
    assert "interceptor" not in frida.lower().replace("interceptor.attach", "")

    gdb = emit_gdb(plan)
    assert "HooklabBreakpoint" in gdb
    assert "strcmp" in gdb
    assert "return False" in gdb


def test_preload_emitter_is_typed_and_rejects_unknown_symbols() -> None:
    plan = load_plan(PLAN)
    source = emit_preload(plan)
    assert "dlsym(RTLD_NEXT" in source
    assert "real_strcmp" in source
    assert "strcmp(const char * a0, const char * a1)" in source

    plan["native"] = [{"library": "libc.so.6", "symbol": "frobnicate"}]
    with pytest.raises(EmitError):
        emit_preload(plan)


def test_emitters_need_a_native_hook() -> None:
    plan = load_plan(PLAN)
    plan["native"] = []
    for emitter in (emit_frida, emit_gdb, emit_preload):
        with pytest.raises(EmitError):
            emitter(plan)


# -------------------------------------------------------------------- grading


def test_example_plan_is_submittable() -> None:
    plan = load_plan(PLAN)
    report = grade(plan, ROOT)
    assert report.submittable, [f.message for f in report.blocking]
    assert report.grade == "A"
    assert report.score == 100


def test_missing_exercise_blocks() -> None:
    plan = load_plan(PLAN)
    plan["exercise"] = {}
    report = grade(plan, ROOT)
    assert "exercise" in {f.rule for f in report.blocking}


def test_intrusive_plan_needs_cleanup() -> None:
    plan = load_plan(PLAN)
    plan["risk"] = "intrusive"
    plan["cleanup"] = []
    report = grade(plan, ROOT)
    assert "cleanup" in {f.rule for f in report.blocking}


def test_expectation_for_unhooked_target_is_major() -> None:
    plan = load_plan(PLAN)
    plan["expect"].append({"target": "not_hooked", "event": "call", "has": ["x"]})
    report = grade(plan, ROOT)
    finding = next(f for f in report.findings if f.rule == "expect-target")
    assert finding.severity == "major"
    assert report.submittable


def test_missing_module_blocks() -> None:
    plan = load_plan(PLAN)
    plan["module"] = "examples/absent.py"
    report = grade(plan, ROOT)
    assert "module-exists" in {f.rule for f in report.blocking}


def test_hook_without_reason_is_major() -> None:
    plan = load_plan(PLAN)
    plan["hooks"][0]["why"] = ""
    report = grade(plan, ROOT)
    finding = next(f for f in report.findings if f.rule == "hook-why")
    assert finding.severity == "major"


def test_scaffold_needs_scope_and_hooks() -> None:
    report = grade(scaffold("A scaffolded hook plan", "demo"))
    rules = {f.rule for f in report.findings}
    assert "scope-ref" in rules
    assert "exercise" in rules
    assert report.submittable is False


def test_report_renders_hooks_and_grade() -> None:
    plan = load_plan(PLAN)
    text = render_report(plan, grade(plan, ROOT))
    assert "check_password" in text
    assert "## Plan grade" in text
    assert "**A**" in text


def test_plan_errors(tmp_path: Path) -> None:
    with pytest.raises(PlanError):
        load_plan(tmp_path / "nope.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{oops", encoding="utf-8")
    with pytest.raises(PlanError):
        load_plan(bad)


# ------------------------------------------------------------------------ cli


def test_cli_validate_check_run_and_emit(tmp_path: Path) -> None:
    result = run_cli("validate", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] == 50 and payload["passed"] is True

    checked = run_cli("check", str(PLAN))
    assert checked.returncode == 0, checked.stdout
    assert "grade A" in checked.stdout

    ran = run_cli("run", str(PLAN))
    assert ran.returncode == 0, ran.stdout
    assert "hunter2" in ran.stdout
    assert "PASS" in ran.stdout

    out = tmp_path / "agent.js"
    emitted = run_cli("emit", str(PLAN), "--format", "frida", "--out", str(out))
    assert emitted.returncode == 0, emitted.stderr
    assert "strcmp" in out.read_text(encoding="utf-8")
