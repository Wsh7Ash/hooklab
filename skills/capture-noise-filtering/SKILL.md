---
name: capture-noise-filtering
description: "Drop captures that cannot answer the question, using a predicate you can state, rather than deleting lines by hand afterwards. Use when the hooked function fires on background traffic, health checks or unrelated callers"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, noise]
---

# Capture Noise Filtering

> Drop captures that cannot answer the question, using a predicate you can state, rather than deleting lines by hand afterwards

**Use when:** the hooked function fires on background traffic, health checks or unrelated callers

**Avoid when:** the capture is already small enough to read in full

## Procedure

1. Characterise the noise by caller, thread or argument shape.
2. Write the filter as an explicit predicate in the hook.
3. Log dropped counts separately, never silently.
4. Check that the filter does not drop the calls you need.
5. Record the predicate in the plan so the capture can be interpreted.
6. Re-run without the filter on a small sample to validate it.

## Signals

- Most captures come from a health-check thread.
- One caller produces ninety percent of the events.
- The value you need appears only in calls the filter would drop.
- Dropped count is unknown, so completeness cannot be judged.

## Patterns

**1. Predicate filter**

```text
if (threadId == healthThread) { dropped++; return; }  -> counted
```

**2. Arg-shape filter**

```text
skip calls where arg0.isNull()  -> counted, never silent
```

**3. Validation sample**

```text
run unfiltered on 20 calls  -> confirm nothing needed was dropped
```

## Pitfalls

- Filtering by a condition that also matches the call you need.
- Dropping events without counting them, so the capture looks complete.
- Removing noise in a text editor after the run and losing the audit trail.

## Done when

- The filter predicate and the dropped count are recorded.
- A sample run without the filter contains no additional needed calls.

## References

- [Frida - Thread.backtrace](https://frida.re/docs/javascript-api/#thread)
- [Python - traceback](https://docs.python.org/3/library/traceback.html)
