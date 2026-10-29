---
name: async-and-thread-capture
description: "Tag every capture with its thread, because a worker pool turns a single request into an interleaved stream that looks like corruption. Use when the target uses threads, asyncio, a worker pool or an event loop offloading work"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, concurrency]
---

# Async and Thread Capture

> Tag every capture with its thread, because a worker pool turns a single request into an interleaved stream that looks like corruption

**Use when:** the target uses threads, asyncio, a worker pool or an event loop offloading work

**Avoid when:** the target is strictly single-threaded and the capture order is already meaningful

## Procedure

1. Identify the threading model and the pool size.
2. Add the thread or task id to every capture record.
3. Group captures by request when a correlation id exists.
4. Check for captures that appear on a thread you did not expect.
5. Report per-thread sequences rather than one global order.
6. Note any data that was captured while another thread held a lock.

## Signals

- The same argument appears on three threads at once.
- A return event appears before its call in a global ordering.
- Values from two requests interleave in one capture file.
- A locked section produces no captures at all.

## Patterns

**1. Thread tag**

```text
threadId=<n> on every line  -> separate streams
```

**2. Correlation id**

```text
group by request id when the target provides one
```

**3. Per-thread order**

```text
sort within a thread, never across threads
```

## Pitfalls

- Presenting an interleaved multi-threaded capture as a single sequence.
- Assuming a lock makes the capture atomic; hooks can fire inside the critical section.
- Losing the thread id and then blaming the target for out-of-order events.

## Done when

- Every capture carries a thread or task identifier.
- Analysis groups by thread or correlation id rather than global order.

## References

- [Python - asyncio](https://docs.python.org/3/library/asyncio.html)
- [Frida - Thread API](https://frida.re/docs/javascript-api/#thread)
