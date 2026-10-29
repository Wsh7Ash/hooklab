# hooklab

Plan a hook, run it, prove it fired.

`hooklab` is a CLI plus 50 skills for function-level instrumentation. A hook plan is JSON: what to hook, why, what to capture, how the observation is proven, and how the target is returned to normal. The CLI executes that plan in-process for Python targets and emits Frida, GDB or LD_PRELOAD scripts from the same plan for native ones.

```text
$ hooklab check examples/plan/password-capture.json
password-plaintext-capture: grade A (100/100) submittable
```

```text
$ hooklab run examples/plan/password-capture.json
returned: {'ok': True, 'user': 'alice'}
call   check_password           username='alice' password='hunter2'
return check_password           __return__=True
# 2 capture(s), PASS
```

No dependencies. Python 3.10+ standard library, `pytest` for development.

## Why a plan instead of a script

A hook is easy to write and hard to trust. The failures are always the same: it landed on the wrong symbol, it never fired, it changed the target's behaviour, or it was left installed. The plan format makes each of those checkable, and `hooklab` grades it before you collect evidence:

| Rule | Severity | What it catches |
|---|---|---|
| `schema` / `scope-ref` | blocking | no plan version, or no authorization reference for the target |
| `hooks` / `hook-target` | blocking | nothing to hook, or a hook with no target |
| `exercise` | blocking | no call that proves the hook fires |
| `expect` / `expect-values` | blocking / major | nothing asserted, or an assertion with no values |
| `cleanup` | blocking when `risk` is intrusive | a modifying hook with no restoration step |
| `module-exists` | blocking | the plan points at a file that is not there |
| `hook-why` | major | a hook that cannot say what value it reveals |
| `expect-target` | major | an expectation for something no hook records |

Any blocking finding caps the grade at D.

## What actually runs

For Python targets, `run` installs `sys.setprofile` (not `sys.settrace` — profile events carry the return value and cost far less), records the named locals at each call, records the return value at each return, then restores the previous profiler. Arguments come from the plan as plain JSON, so no `eval` is involved.

```python
with Tracer(hooks):
    result = function(*args, **kwargs)
# captures: call check_password username='alice' password='hunter2'
#           return check_password __return__=True
```

Captures are capped (`max_events`), truncation is reported rather than hidden, and an exception in the hook can never take the target down: the recorder swallows its own errors and keeps going.

## What it emits

One plan, three native targets. `hooklab emit --format frida|gdb|preload` writes the script, and every emitter refuses rather than guesses:

```text
$ hooklab emit examples/plan/password-capture.json --format preload
static int (*real_strcmp)(const char * a0, const char * a1) = NULL;
int strcmp(const char * a0, const char * a1) {
    if (real_strcmp == NULL) { real_strcmp = dlsym(RTLD_NEXT, "strcmp"); }
    fprintf(stderr, "[hooklab] strcmp called\n");
    ...
    return real_strcmp(a0, a1);
}
```

The C emitter only covers prototypes it knows (`strcmp`, `strncmp`, `memcmp`, `puts`). Ask it for an unknown symbol and it stops with an explanation, because a guessed signature corrupts the target's stack — the opposite of observation.

## Commands

```text
hooklab check PLAN [--json] [--verbose]        # grade the plan
hooklab run PLAN [--json]                      # execute the exercise under the tracer
hooklab emit PLAN --format frida|gdb|preload   # generate a native hook script
hooklab report PLAN [--out report.md]          # plan markdown with the grade
hooklab scaffold "Title" --id hook-id          # empty plan
hooklab validate                               # the 50/50 corpus gate
hooklab list / show / search / build           # corpus
```

## The skills

| Phase | Count | What it covers |
|---|---|---|
| `resolve` | 9 | symbol resolution order, library versus symbol, stripped binaries, PLT/GOT, version mismatch, address verification, inlining, calling conventions, dependency mapping |
| `instrument` | 9 | scope minimisation, breakpoint choice, hook versus breakpoint, argument safety, read-only discipline, attach timing, injection windows, multi-hook order, idempotence |
| `hook` | 8 | interceptor, GOT patch, inline trampoline, syscalls, managed runtimes, interpreter tracing, USDT probes, Python profile hooks |
| `capture` | 8 | formatting, return values, structs, string bounds, noise filtering, deduplication, threads, timestamps |
| `verify` | 8 | fired proof, negative control, behaviour parity, side effects, completeness, overhead, regression, reproducibility |
| `teardown` | 8 | detach and restore, patch restoration, process state, artifacts, redaction, evidence, disclosure, retest |

`hooklab validate` enforces six steps, four signals, three patterns, three pitfalls, 180 rendered words and canonical https references on every run.

## Install

```bash
python -m pip install -e ".[dev]"
hooklab validate
python -m pytest -q
```

## Proof

`RESULTS.md` records the commands run for this release with real output, and the two defects the tests caught. `results/demo_transcript.txt` is the raw session.

## Scope and intent

`run` executes a function in a Python module you point it at, on your machine, with arguments from the plan. `emit` writes files; it does not attach to anything. Nothing here contacts a remote host, and every skill assumes the target is authorized for testing — which is what the `scope-ref` rule demands before a plan can grade A.

MIT licensed.
