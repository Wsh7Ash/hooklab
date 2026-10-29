"""In-process tracing, module loading and hook-script emission.

The point of this module is that a hook plan can be *executed* rather than
believed: ``Tracer`` installs a profile hook, records the arguments a function
received and the value it returned, and ``run_exercise`` calls a function with
plain JSON arguments so no ``eval`` is ever involved.

Emission covers the three places researchers actually put a hook: Frida (a JS
agent for a running process), GDB (a Python breakpoint script) and LD_PRELOAD
(a C interposer). Only well-known libc prototypes are emitted as C, because
guessing an unknown function's signature produces code that corrupts the target.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

RETURN_KEY = "__return__"
MAX_EVENTS = 2000
MAX_REPR = 240


class HookError(RuntimeError):
    """Raised when a hook plan cannot be run or emitted."""


class EmitError(RuntimeError):
    """Raised when a native hook cannot be emitted safely."""


@dataclass(frozen=True)
class Capture:
    target: str
    event: str
    values: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {"target": self.target, "event": self.event, "values": dict(self.values)}


def _safe_repr(value: Any) -> str:
    try:
        text = repr(value)
    except Exception as exc:  # a __repr__ that raises must not kill the trace
        return f"<unrepresentable: {type(exc).__name__}>"
    if len(text) > MAX_REPR:
        text = text[: MAX_REPR - 3] + "..."
    return text


@dataclass
class Tracer:
    """Records calls and returns for the targets named in a hook plan."""

    hooks: list[dict[str, Any]]
    max_events: int = MAX_EVENTS
    captures: list[Capture] = field(default_factory=list)
    truncated: bool = False
    _previous: Callable[..., Any] | None = None

    def _index(self) -> dict[str, list[dict[str, Any]]]:
        index: dict[str, list[dict[str, Any]]] = {}
        for hook in self.hooks:
            target = str(hook.get("target", "")).strip()
            if target:
                index.setdefault(target, []).append(hook)
        return index

    def _matches(self, code: Any, index: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        names = {code.co_name, getattr(code, "co_qualname", code.co_name)}
        hits: list[dict[str, Any]] = []
        for name in names:
            hits.extend(index.get(name, []))
        return hits

    def _profile(self, frame: Any, event: str, arg: Any) -> None:
        if event not in ("call", "return"):
            return
        if self.truncated:
            return
        try:
            hooks = self._matches(frame.f_code, self._index())
            if not hooks:
                return
            for hook in hooks:
                if str(hook.get("event", "call")) != event:
                    continue
                wanted = [str(name) for name in hook.get("capture", [])]
                if event == "return":
                    if RETURN_KEY not in wanted:
                        wanted = [*wanted, RETURN_KEY]
                    values = {RETURN_KEY: _safe_repr(arg)}
                else:
                    values = {
                        name: _safe_repr(frame.f_locals.get(name))
                        for name in wanted
                        if name in frame.f_locals
                    }
                if self.captures and len(self.captures) >= self.max_events:
                    self.truncated = True
                    return
                self.captures.append(
                    Capture(str(hook.get("target")), event, values)
                )
        except Exception:
            # A tracer must never take the target down with it.
            return

    def __enter__(self) -> "Tracer":
        self._previous = sys.getprofile()
        sys.setprofile(self._profile)
        return self

    def __exit__(self, *exc: Any) -> None:
        sys.setprofile(self._previous)


def load_module(path: Path) -> Any:
    """Import a Python file by path, without requiring it on sys.path."""
    if not path.is_file():
        raise HookError(f"module not found: {path}")
    name = f"hooklab_target_{abs(hash(path.resolve()))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise HookError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    parent = str(path.resolve().parent)
    added = parent not in sys.path
    if added:
        sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(module)
    finally:
        if added:
            sys.path.remove(parent)
    return module


@dataclass
class RunResult:
    captures: list[Capture]
    returned: str
    truncated: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "captures": [capture.as_dict() for capture in self.captures],
            "returned": self.returned,
            "truncated": self.truncated,
        }


def run_exercise(
    module: Any,
    hooks: Iterable[dict[str, Any]],
    exercise: dict[str, Any],
) -> RunResult:
    """Call ``exercise['function']`` under the tracer and report what was seen."""
    function_name = str(exercise.get("function", "")).strip()
    if not function_name:
        raise HookError("exercise has no function")
    function = getattr(module, function_name, None)
    if not callable(function):
        raise HookError(f"module has no callable {function_name!r}")

    args = exercise.get("args") or []
    kwargs = exercise.get("kwargs") or {}
    if not isinstance(args, list) or not isinstance(kwargs, dict):
        raise HookError("exercise args must be a list and kwargs an object")

    tracer = Tracer(list(hooks))
    with tracer:
        try:
            result = function(*args, **kwargs)
        except Exception as exc:  # the target's own failure is data, not a crash
            result = f"<raised {type(exc).__name__}: {exc}>"

    return RunResult(tracer.captures, _safe_repr(result), tracer.truncated)


def check_expectations(
    captures: Iterable[Capture], expect: Iterable[dict[str, Any]]
) -> list[str]:
    """Return one problem string per unmet expectation."""
    records = list(captures)
    problems: list[str] = []
    for rule in expect:
        target = str(rule.get("target", ""))
        event = str(rule.get("event", "call"))
        wanted = [str(name) for name in rule.get("has", [])]
        matching = [c for c in records if c.target == target and c.event == event]
        if not matching:
            problems.append(f"{target}/{event}: no capture recorded")
            continue
        for name in wanted:
            if not any(name in capture.values for capture in matching):
                problems.append(f"{target}/{event}: missing captured value {name!r}")
        for name in [str(item) for item in rule.get("absent", [])]:
            if any(name in capture.values for capture in matching):
                problems.append(f"{target}/{event}: value {name!r} should not have been captured")
    return problems


# ------------------------------------------------------------------ emission

LIBRARY_FUNCTION_FALLBACK = "Module.findGlobalExportByName"


def emit_frida(plan: dict[str, Any]) -> str:
    """A Frida agent that logs the plan's native hooks."""
    native = [item for item in plan.get("native") or [] if isinstance(item, dict)]
    if not native:
        raise EmitError("plan has no native hooks to emit")

    lines = [
        "'use strict';",
        "",
        "// Generated by hooklab. Attach with: frida -p <pid> -l hooklab-agent.js",
        "// Every hook is read-only: it logs and returns, it does not modify arguments.",
        "",
        "function resolve(symbol) {",
        f"  try {{ return {LIBRARY_FUNCTION_FALLBACK}(symbol); }}",
        "  catch (e) { console.error('[hooklab] cannot resolve ' + symbol); return null; }",
        "}",
        "",
    ]
    for item in native:
        symbol = str(item.get("symbol", ""))
        args = [str(name) for name in item.get("print", [])]
        lines += [
            f"// {item.get('library', 'any')}!{symbol} on {item.get('on', 'enter')}",
            "(function () {",
            f"  const address = resolve({json.dumps(symbol)});",
            "  if (address === null) { return; }",
            "  Interceptor.attach(address, {",
            "    onEnter(args) {",
        ]
        for index, name in enumerate(args):
            slot = name if name.startswith("arg") else f"arg{index}"
            lines.append(
                f"      console.log('[hooklab] {symbol} {name}=' + "
                f"{slot}.readUtf8String().slice(0, 200));"
            )
        lines += [
            "    },",
            "  });",
            "})();",
            "",
        ]
    lines.append("console.log('[hooklab] ' + " + str(len(native)) + " + ' hook(s) installed');")
    return "\n".join(lines) + "\n"


def emit_gdb(plan: dict[str, Any]) -> str:
    """A GDB Python script that breaks on each symbol and logs, without stopping."""
    native = [item for item in plan.get("native") or [] if isinstance(item, dict)]
    if not native:
        raise EmitError("plan has no native hooks to emit")

    lines = [
        '"""Generated by hooklab. Run with: gdb -q -x hooklab-gdb.py --args ./target"""',
        "",
        "import gdb",
        "",
        "",
        "class HooklabBreakpoint(gdb.Breakpoint):",
        "    def __init__(self, symbol, slot_names):",
        "        super().__init__(symbol, gdb.BP_BREAKPOINT, internal=False)",
        "        self.symbol = symbol",
        "        self.slot_names = slot_names",
        "",
        "    def stop(self):",
        "        frame = gdb.newest_frame()",
        "        out = ['[hooklab] ' + self.symbol]",
        "        for index, name in enumerate(self.slot_names):",
        "            try:",
        "                value = frame.read_register('rdi') if index == 0 else frame.read_register('rsi')",
        "                out.append('%s=%s' % (name, value))",
        "            except Exception:",
        "                out.append('%s=<unreadable>' % name)",
        "        print(' '.join(out))",
        "        return False  # log and continue",
        "",
        "",
    ]
    for item in native:
        symbol = str(item.get("symbol", ""))
        args = [str(name) for name in item.get("print", [])]
        lines.append(f"HooklabBreakpoint({json.dumps(symbol)}, {args!r})")
    lines.append("")
    return "\n".join(lines)


# Only prototypes that are certain; guessing an unknown signature corrupts state.
C_SIGNATURES = {
    "strcmp": ("int", "const char *", "const char *", "int"),
    "strncmp": ("int", "const char *", "const char *", "size_t"),
    "memcmp": ("int", "const void *", "const void *", "size_t"),
    "puts": ("int", "const char *", "int"),
}


def emit_preload(plan: dict[str, Any]) -> str:
    """A C interposer for the libc functions hooklab knows how to wrap."""
    native = [item for item in plan.get("native") or [] if isinstance(item, dict)]
    if not native:
        raise EmitError("plan has no native hooks to emit")

    unknown = [str(item.get("symbol")) for item in native if str(item.get("symbol")) not in C_SIGNATURES]
    if unknown:
        raise EmitError(
            "no safe prototype for "
            + ", ".join(sorted(unknown))
            + "; supply a Frida hook instead of guessing a C signature"
        )

    lines = [
        "/* Generated by hooklab. Build: cc -shared -fPIC -o hook.so hooklab-preload.c -ldl */",
        "#define _GNU_SOURCE",
        "#include <dlfcn.h>",
        "#include <stdio.h>",
        "#include <string.h>",
        "",
    ]
    for item in native:
        symbol = str(item.get("symbol"))
        ret, *params, _ = C_SIGNATURES[symbol]
        names = [f"a{index}" for index in range(len(params))]
        signature = ", ".join(f"{type_name} {name}" for type_name, name in zip(params, names)) or "void"
        lines += [
            f"/* {symbol}: logged on entry, results unchanged */",
            f"static {ret} (*real_{symbol})({signature}) = NULL;",
            f"{ret} {symbol}({signature}) {{",
            f"    if (real_{symbol} == NULL) {{ real_{symbol} = dlsym(RTLD_NEXT, \"{symbol}\"); }}",
            f"    fprintf(stderr, \"[hooklab] {symbol} called\\n\");",
        ]
        if symbol == "strcmp":
            lines.append("    if (a0 != NULL && a1 != NULL) {")
            lines.append("        fprintf(stderr, \"[hooklab] a0=%.120s a1=%.120s\\n\", a0, a1);")
            lines.append("    }")
        lines.append(f"    return real_{symbol}({', '.join(names)});")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)
