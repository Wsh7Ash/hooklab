---
name: multi-hook-ordering
description: "Fix the order in which several hooks report, so a capture stream can be read as a sequence instead of a bag of unrelated events. Use when two or more hooks observe the same request and the relationship between them matters"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, ordering]
---

# Multi Hook Ordering

> Fix the order in which several hooks report, so a capture stream can be read as a sequence instead of a bag of unrelated events

**Use when:** two or more hooks observe the same request and the relationship between them matters

**Avoid when:** the hooks observe unrelated paths that never interleave

## Procedure

1. List the hooks and the natural order the target calls them in.
2. Add a monotonic counter or timestamp to every capture record.
3. Record the nesting depth where hooks call each other.
4. Sort the capture stream by counter before analysis, never by arrival text.
5. Check that the observed order matches the order the source implies.
6. State the ordering guarantee the capture can and cannot provide.

## Signals

- The capture shows a return before its matching call.
- Two hooks report the same timestamp and the order is ambiguous.
- Nesting depth increases where no recursion is expected.
- A hook fires from a different thread than the one you expected.

## Patterns

**1. Monotonic counter**

```text
seq 1 call parse
seq 2 call validate
seq 3 return validate  -> readable order
```

**2. Depth tracking**

```text
indent by depth  -> shows which call is nested
```

**3. Thread tag**

```text
record thread id  -> separates interleaved streams
```

## Pitfalls

- Sorting captures by wall-clock text and losing sub-millisecond ordering.
- Assuming single-threaded execution when the target uses a worker pool.
- Presenting an interleaved multi-thread capture as a single sequence.

## Done when

- Every capture carries a sequence number or timestamp plus thread id.
- The analysis states the ordering guarantee and any interleaving.

## References

- [Frida - Thread API](https://frida.re/docs/javascript-api/#thread)
- [Python - threading](https://docs.python.org/3/library/threading.html)
