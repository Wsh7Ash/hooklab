---
name: capture-timestamping
description: "Timestamp captures with a monotonic clock, so timing claims survive a system clock adjustment during the run. Use when the capture supports a claim about ordering, latency or a race window"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, timing]
---

# Capture Timestamping

> Timestamp captures with a monotonic clock, so timing claims survive a system clock adjustment during the run

**Use when:** the capture supports a claim about ordering, latency or a race window

**Avoid when:** the capture is purely about values and timing plays no part

## Procedure

1. Use a monotonic clock for deltas, not wall-clock time.
2. Record the clock source in the plan.
3. Capture a timestamp at call and at return for latency.
4. Convert to wall-clock only for display, and label the conversion.
5. Check for clock adjustments during the run.
6. Report deltas with their resolution, not as exact measurements.

## Signals

- Deltas are negative, meaning the clock moved backwards.
- Two events share a timestamp at the clock's resolution.
- Latency measured under the hook exceeds the unhooked baseline.
- The timestamp granularity is coarser than the window being claimed.

## Patterns

**1. Monotonic deltas**

```text
t1 = perf_counter_ns()  -> unaffected by NTP steps
```

**2. Call to return**

```text
latency = return_ts - call_ts  -> labelled as observed under hook
```

**3. Resolution note**

```text
clock resolution 100 ns  -> do not claim a 10 ns window
```

## Pitfalls

- Using wall-clock time and reporting a negative duration after an adjustment.
- Claiming sub-millisecond ordering from a millisecond-resolution clock.
- Ignoring the hook's own overhead when reporting latency.

## Done when

- Timestamps use a named monotonic source and the resolution is stated.
- Latency claims are marked as measured under instrumentation.

## References

- [Python - time.perf_counter_ns](https://docs.python.org/3/library/time.html#time.perf_counter_ns)
- [Linux - clock_gettime](https://man7.org/linux/man-pages/man3/clock_gettime.3.html)
