"""hooklab corpus: pack metadata plus 50 authored hooking skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once into
the validated :class:`~hooklab.model.Skill` shape. Phases follow a session:
resolve, instrument, hook, capture, verify, teardown.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "hooklab",
    "version": "1.0.0",
    "category": "dynamic-instrumentation",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for hooking and instrumentation, plus a CLI that "
        "runs a hook plan in-process, verifies the capture against expectations, "
        "and emits Frida, GDB or LD_PRELOAD scripts from the same plan."
    ),
    "expected_skills": 50,
    "meta_keys": ("phase",),
    "requires_verification": False,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
BY_SLUG: dict[str, Any] = {skill.slug: skill for skill in SKILLS}
