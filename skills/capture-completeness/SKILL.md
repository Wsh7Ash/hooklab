---
name: capture-completeness
description: "Show that the capture covers every call in the window, by reconciling the target's own counters with the hook's event count. Use when the claim depends on how many times something happened or on a missing event"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, completeness]
---

# Capture Completeness

> Show that the capture covers every call in the window, by reconciling the target's own counters with the hook's event count

**Use when:** the claim depends on how many times something happened or on a missing event

**Avoid when:** the claim is about a single observed value and counts are irrelevant

## Procedure

1. Find an independent count: target logs, a counter endpoint or a database row count.
2. Compare it with the hook's event count for the same window.
3. Investigate any shortfall, which usually means dropped events or an early detach.
4. Check whether the event cap truncated the capture.
5. State the reconciliation in the results.
6. If the counts cannot be reconciled, do not claim completeness.

## Signals

- The target logged 400 requests and the hook recorded 391.
- The truncated flag is set, so later events are missing.
- Counts match before the detach and diverge afterwards.
- A filtered subset is being compared with an unfiltered total.

## Patterns

**1. Reconcile**

```text
server counter 400, hook events 400  -> complete
```

**2. Explain the gap**

```text
9 missing -> events occurred after detach  -> stale claim
```

**3. Truncation**

```text
truncated=true means the count is a lower bound, not a total
```

## Pitfalls

- Claiming a request never happened when the capture was truncated.
- Comparing a filtered capture with an unfiltered server counter.
- Ignoring a small shortfall that actually indicates dropped events.

## Done when

- The hook count is reconciled against an independent count, or the gap is explained.
- Truncation status is stated wherever counts are quoted.

## References

- [Frida - performance and event loss](https://frida.re/docs/performance/)
- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
