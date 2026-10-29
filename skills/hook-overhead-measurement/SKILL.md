---
name: hook-overhead-measurement
description: "Measure how much the hook slows the target, because a timing-sensitive claim measured under instrumentation may be an artefact of the hook. Use when the finding involves a race, a timeout or a latency threshold"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, performance]
---

# Hook Overhead Measurement

> Measure how much the hook slows the target, because a timing-sensitive claim measured under instrumentation may be an artefact of the hook

**Use when:** the finding involves a race, a timeout or a latency threshold

**Avoid when:** the finding is a static value capture with no timing dimension

## Procedure

1. Measure the operation without any hook, several times.
2. Measure it with the final hook set installed.
3. Report both medians and the ratio.
4. Reduce the hook's work if the ratio is large: fewer fields, no formatting.
5. Re-check any timing claim against the unhooked baseline.
6. State the overhead next to the timing claim.

## Signals

- The hooked run is an order of magnitude slower.
- A timeout appears only under instrumentation.
- The race window widens under the hook, making it easier to win.
- Overhead is negligible for the final narrow hook set.

## Patterns

**1. Baseline first**

```text
median 42 ms unhooked, 61 ms hooked  -> 1.45x
```

**2. Reduce work**

```text
capture one field instead of five  -> overhead drops
```

**3. Timing caveat**

```text
race won 6/10 unhooked, 10/10 hooked  -> the hook changed the odds
```

## Pitfalls

- Reporting a race success rate measured only under a heavy hook.
- Measuring overhead with a different input than the one in the finding.
- Assuming a single run is a measurement.

## Done when

- Hooked and unhooked timings are both recorded with medians.
- Timing claims state the overhead that was present.

## References

- [Frida - performance considerations](https://frida.re/docs/performance/)
- [Python - timeit](https://docs.python.org/3/library/timeit.html)
