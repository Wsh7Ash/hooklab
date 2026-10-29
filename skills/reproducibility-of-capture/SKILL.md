---
name: reproducibility-of-capture
description: "Run the plan twice and show the same captures, because a hook that depends on timing or load produces evidence nobody can re-derive. Use when the capture will be cited in a report or handed to another researcher"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, reproducibility]
---

# Reproducibility of Capture

> Run the plan twice and show the same captures, because a hook that depends on timing or load produces evidence nobody can re-derive

**Use when:** the capture will be cited in a report or handed to another researcher

**Avoid when:** the target is genuinely nondeterministic and the plan states a distribution instead

## Procedure

1. Run the plan twice from a clean process state.
2. Compare the capture fields, ignoring addresses and timestamps.
3. Record any difference and its cause.
4. Pin nondeterministic inputs, such as thread scheduling or a random seed.
5. Report a distribution when the value genuinely varies.
6. State the number of runs behind every quoted capture.

## Signals

- The value appears in one run and not the other.
- Event counts differ between identical runs.
- Only addresses and timestamps differ, which is expected.
- The capture depends on a cache that is warm on the second run.

## Patterns

**1. Field-wise compare**

```text
ignore ptr= and ts= fields  -> everything else must match
```

**2. Seed pinning**

```text
set a fixed seed or disable the pool  -> deterministic path
```

**3. Distribution**

```text
3 of 5 runs captured the plaintext  -> state the rate
```

## Pitfalls

- Quoting one run as typical when a third of runs produce nothing.
- Comparing raw lines including addresses and concluding a mismatch.
- Ignoring a warm cache that makes the second run take a different path.

## Done when

- Two clean runs are compared field by field with differences explained.
- The number of runs behind each quoted capture is stated.

## References

- [Frida - reproducibility notes](https://frida.re/docs/performance/)
- [Python - random seeding](https://docs.python.org/3/library/random.html#random.seed)
