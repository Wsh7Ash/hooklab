---
name: process-attach-timing
description: "Attach before the code path runs, which for short-lived processes means spawning suspended rather than attaching to something already moving. Use when the target is a CLI that exits in milliseconds or a service that validates input at startup"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, timing]
---

# Process Attach Timing

> Attach before the code path runs, which for short-lived processes means spawning suspended rather than attaching to something already moving

**Use when:** the target is a CLI that exits in milliseconds or a service that validates input at startup

**Avoid when:** the process is long-lived and the interesting call happens on demand

## Procedure

1. Identify when the interesting function runs relative to process start.
2. If it runs during startup, spawn the process suspended and attach first.
3. If it runs on demand, attach any time before triggering the request.
4. Record the attach point in the plan so the trace is reproducible.
5. Confirm the hook is installed before the first call, for example by a counter.
6. Re-check timing if the target is restarted by a supervisor.

## Signals

- The process exits before the hook installs.
- The first call happens during dynamic linking, before your script loads.
- A supervisor restarts the process and the hook is lost.
- The capture starts mid-path, missing the first argument.

## Patterns

**1. Spawn suspended**

```text
frida -f ./target --pause  -> attach, then resume
```

**2. Counter proof**

```text
hooks_fired == 1 before the request  -> installed in time
```

**3. Startup path**

```text
hook at load time when validation happens during init
```

## Pitfalls

- Attaching to a process that already performed the validation you wanted to see.
- Assuming a supervisor keeps your instrumented process alive.
- Starting the trace after the first request and reporting incomplete captures.

## Done when

- The attach point is recorded and precedes the first relevant call.
- A counter or log line shows the hook was active before the trigger.

## References

- [Frida - spawning and resuming](https://frida.re/docs/javascript-api/#frida)
- [GDB - attaching to a process](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html)
