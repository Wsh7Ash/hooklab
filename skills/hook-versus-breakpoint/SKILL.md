---
name: hook-versus-breakpoint
description: "Pick a persistent hook when you need every call, and a breakpoint when you need one call inspected in depth, because they answer different questions. Use when the objective involves either a stream of calls or a single deep inspection"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, method]
---

# Hook Versus Breakpoint

> Pick a persistent hook when you need every call, and a breakpoint when you need one call inspected in depth, because they answer different questions

**Use when:** the objective involves either a stream of calls or a single deep inspection

**Avoid when:** the target is a language runtime where a trace hook is the only supported option

## Procedure

1. Count how many calls the question needs: one, a sample or all of them.
2. For all calls, install a hook that logs and returns immediately.
3. For one call, use a breakpoint and inspect registers and memory interactively.
4. For a sample, use a hook with a rate limit and record what was dropped.
5. Note that a hook changes the function's own frame and can perturb stack inspection.
6. Record the choice and the sampling rule in the plan.

## Signals

- The question needs a distribution across many calls, not one example.
- The question needs the caller's stack, which a breakpoint shows more clearly.
- The hook's own frame confuses a stack walk at the target.
- Sampling without a rate limit produces a capture too large to read.

## Patterns

**1. Stream every call**

```text
hook every call, log one line, continue  -> distribution over 400 calls
```

**2. Single deep look**

```text
breakpoint, then bt and x/16gx $rsp  -> one call, full context
```

**3. Sampled hook**

```text
log every 50th call  -> note the sampling interval in the plan
```

## Pitfalls

- Using a breakpoint for a hot function and spending an hour stepping.
- Using a hook when you need the caller's stack and losing it to the injected frame.
- Sampling silently, so the capture looks like the full population.

## Done when

- The mechanism matches whether the question needs one call, a sample or all calls.
- Any sampling rate is stated in the plan and the results.

## References

- [GDB - stack frames](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Frames.html)
- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
