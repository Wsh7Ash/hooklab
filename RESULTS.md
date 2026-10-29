# Results

Evidence for the claims in `README.md`. Every command was run in this repository; output is verbatim.

## Environment

- OS: Windows (MSYS2 shell), CPython 3.14
- Runtime: standard library only, `pytest` for development
- Network: not required

## Corpus gate

```text
$ hooklab validate
hooklab: 50/50 skills valid
  ok  steps>=6 signals>=4 patterns>=3 pitfalls>=3 words>=180 refs canonical https
```

`results/validation.json` holds the machine-readable form (`checked 50, valid 50, passed true`). Phase distribution: `resolve` 9, `instrument` 9, `hook` 8, `capture` 8, `verify` 8, `teardown` 8.

## Test suite

```text
$ python -m pytest -q
..........................                                               [100%]
```

26 tests: corpus gate and committed-artifact drift, tracer behaviour, expectation checking, truncation, profiler restoration, all three emitters, every plan rule, and the CLI.

## End to end

`results/demo_transcript.txt` is a real session against `examples/target_app.py`:

| Command | Result |
|---|---|
| `check examples/plan/password-capture.json` | `grade A (100/100) submittable`, exit 0 |
| `run examples/plan/password-capture.json` | 2 captures, `PASS`; `password='hunter2'` and `__return__=True`, exit 0 |
| `run --json` | the same captures with `"truncated": false` and `"problems": []` |
| `emit --format preload` | a typed `strcmp` interposer using `dlsym(RTLD_NEXT, ...)` and a pass-through call |

## Defects found and fixed during this build

1. **Three corpus pattern labels were too short** (`Stream`, `Restore`, `Handles`) and the validator rejected them, which is the gate doing its job — the labels were lengthened rather than the floor lowered.
2. **Stray extra keys** (`user_when` in chainproof's sibling work, `when_note`/`when_extra` here) were written while drafting entries. They are ignored by the loader, but they were removed because a corpus that tolerates typos will accumulate them.

The tracer itself needed no fixes: it was written with the restore path and the exception guard from the start, and both are covered by tests (`test_tracer_restores_previous_profiler`, and the recorder's `except Exception: return`).

## What is not verified

- **The C emitter was not compiled here.** `gcc` is present but this MSYS2 toolchain has no `dlfcn.h`, so `gcc -fsyntax-only` failed on the include, not on the generated code. Compile it on a glibc host before relying on it.
- **No Frida, GDB or DTrace run was performed.** The emitters produce scripts and are tested for content; executing them needs those tools and a native target.
- **Only Python targets were executed.** `run` is defined for Python modules; native observation is out of scope by design and reported as such rather than silently skipped.
