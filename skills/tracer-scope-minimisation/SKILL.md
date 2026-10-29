---
name: tracer-scope-minimisation
description: "Restrict the tracer to the narrowest target set that answers the question, because a broad trace changes timing and buries the signal in noise. Use when the trace will run inside a live process or a performance-sensitive path"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, performance]
---

# Tracer Scope Minimisation

> Restrict the tracer to the narrowest target set that answers the question, because a broad trace changes timing and buries the signal in noise

**Use when:** the trace will run inside a live process or a performance-sensitive path

**Avoid when:** the question is exploratory and you genuinely do not know which function matters

## Procedure

1. Write the question the trace must answer in one sentence.
2. Name the smallest set of functions whose arguments answer it.
3. Trace only those, with an event cap as a safety net.
4. Measure the overhead with the narrow set before widening it.
5. Widen only when a specific value is still missing, and record why.
6. Remove every hook that did not contribute a captured value.

## Signals

- The trace produces thousands of events and none of the values you need.
- Runtime increases enough that a timeout fires.
- A single function produces repeated identical captures.
- The narrowed trace answers the question without the wide one.

## Patterns

**1. Question first**

```text
does the client send the password before hashing?  -> two functions, not the whole network stack
```

**2. Event cap**

```text
max_events = 2000  -> truncated flag instead of unbounded memory
```

**3. Prune by contribution**

```text
hook A captured the password; hook B captured nothing  -> drop B
```

## Pitfalls

- Tracing everything and then reading a million lines hoping to spot the value.
- Adding hooks 'in case they are useful' and changing the timing you wanted to observe.
- Leaving the cap out so a recursion fills memory.

## Done when

- Every installed hook maps to a value named in the objective.
- Overhead is measured with the final hook set.

## References

- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
- [Frida - performance considerations](https://frida.re/docs/performance/)
