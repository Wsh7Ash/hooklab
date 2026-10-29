# Architecture

`hooklab` has three parts: a plan model with rules, an in-process tracer that can execute a plan, and three emitters that translate the same plan into native hook scripts.

## Modules

| Module | Responsibility |
|---|---|
| `hooks.py` | `Tracer`, module loading, `run_exercise`, expectation checking, emitters |
| `plan.py` | Plan rules, grading, scaffold and report rendering |
| `model.py` / `validate.py` / `render.py` | The shared corpus harness |
| `cli.py` | `check`, `run`, `emit`, `report`, `scaffold` plus corpus commands |
| `corpus/part1..3.py` | The 50 skills as plain dicts |

## Data flow

```text
plan.json -> plan.grade -> Report(grade, score, findings)
    |
    +-> cli.run  -> hooks.load_module -> hooks.run_exercise -> captures -> check_expectations
    +-> cli.emit -> emit_frida | emit_gdb | emit_preload -> script text
```

Grading and running are independent: a plan can be graded without being executed, and a plan can be executed without passing the grade. That separation is deliberate — you want to see the findings before you attach anything.

## The tracer

`Tracer` installs `sys.setprofile`, which fires `call` and `return` events only. `sys.settrace` would add line events, which is an order of magnitude more overhead for information this tool does not use.

Design decisions that matter:

- **Match by name, filter by event.** A hook entry names a target and an event; only that pair records.
- **Locals by name at call, argument at return.** A return event's `arg` is the return value, so `__return__` is captured without instrumenting the callee.
- **Bounded capture.** `max_events` stops runaway recursion; `truncated` is reported so a short capture is never mistaken for a complete one.
- **Never propagate.** The recorder wraps its work in `try/except` and returns; an exception inside a profiler disables tracing for the rest of the process and can corrupt the result.
- **Restore, do not clear.** `__exit__` reinstalls the previous profiler, so hooklab does not silently remove another tool's instrumentation.

## Emission

Each emitter reads only `native` entries — `{library, symbol, on, print}` — and each refuses instead of guessing:

| Format | Refusal condition |
|---|---|
| Frida | no `native` entries |
| GDB | no `native` entries |
| LD_PRELOAD | no entries, or any symbol outside the known-prototype table |

The C table exists because an interposer must declare the exact prototype: a wrong signature reads the wrong registers and returns a wrong value, which is a corrupted target rather than an observation. Four libc functions are certain enough to generate; everything else is better served by a Frida hook, which does not need the signature.

## Deliberate non-goals

- No ptrace or process injection. `run` executes in its own process.
- No network attach. `emit` writes a file; loading it into a live process is a separate, deliberate act.
- No behaviour modification. Plans are graded as `read-only` or `intrusive`, and intrusive plans must declare cleanup.
