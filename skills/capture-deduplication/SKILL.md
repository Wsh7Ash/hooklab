---
name: capture-deduplication
description: "Collapse identical consecutive captures while counting them, so a loop produces one readable line instead of a thousand. Use when the hooked function is called repeatedly with identical arguments"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, readability]
---

# Capture Deduplication

> Collapse identical consecutive captures while counting them, so a loop produces one readable line instead of a thousand

**Use when:** the hooked function is called repeatedly with identical arguments

**Avoid when:** each call is genuinely distinct and the sequence matters

## Procedure

1. Compare each capture with the previous one on the captured fields only.
2. When identical, increment a repeat counter instead of appending.
3. Emit the collapsed line when the value changes or the window closes.
4. Record the total count and the collapsed count.
5. Check that a change in any captured field starts a new line.
6. Keep the raw sequence numbers so the collapse is reversible.

## Signals

- The same arguments repeat hundreds of times in a polling loop.
- A capture line ends with a repeat count instead of a sequence.
- Two different calls collapse because a differing field was not captured.
- The collapsed count does not match the total event count.

## Patterns

**1. Collapse and count**

```text
password='x' x412  -> one line, count preserved
```

**2. Fields decide**

```text
compare only the fields in capture[]  -> document that choice
```

**3. Reversible**

```text
keep the first and last sequence numbers of the run
```

## Pitfalls

- Collapsing on a subset of fields and hiding a meaningful change.
- Losing the repeat count so the report understates how often the path runs.
- Deduplicating across threads and merging two independent streams.

## Done when

- Repeated captures collapse with a visible count.
- The collapsed count and total event count agree.

## References

- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
- [Python - itertools.groupby](https://docs.python.org/3/library/itertools.html#itertools.groupby)
