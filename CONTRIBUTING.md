# Contributing

## Setup

```bash
python -m pip install -e ".[dev]"
hooklab validate
python -m pytest -q
```

Standard library only at runtime. The tracer and emitters must stay dependency-free: a hook tool that needs a package is a hook tool that cannot be dropped into an engagement.

## Welcome

- **A plan rule** that catches a real way a capture misleads, with a test that fails without it.
- **A new emitter** (LLDB, bpftrace) that refuses safely on unknown input, as the C emitter does.
- **A stronger skill.** Edit `corpus/part*.py`, then `hooklab build`.
- **A known-prototype entry** for the C emitter, with the exact signature from the platform headers and a test asserting the emitted declaration.

## Not welcome

- Emitting C for a symbol whose prototype is not certain.
- A hook path that can raise into the target: the recorder must never propagate.
- Clearing `sys.setprofile` instead of restoring the previous profiler.
- Weakening a validator floor to fit a skill.
- Any code that attaches to a remote host.

## Skill floors

Enforced by `hooklab validate` and in CI:

| Field | Floor |
|---|---|
| steps | 6, each at least 25 characters |
| signals | 4 |
| patterns | 3, labels 8+ characters, code 20+ |
| pitfalls | 3, each 30+ characters |
| done_when | 2 |
| tags | 2, lowercase kebab-case |
| refs | 1, `[label](https://...)` |
| rendered words | 180 |

Placeholder tokens, machine-local paths, duplicate slugs or titles and a missing `meta.phase` are rejected.

## After editing the corpus

```bash
hooklab build
hooklab validate
python -m pytest -q
```

Commit the regenerated `skills/`, `pack.json` and `results/` with the corpus change; CI fails on drift.
