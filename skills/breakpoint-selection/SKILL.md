---
name: breakpoint-selection
description: "Choose between a breakpoint, a tracepoint and an interceptor by asking whether the process may stop, because a breakpoint in production is an outage. Use when deciding how to observe a native function on a live or shared system"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, method]
---

# Breakpoint Selection

> Choose between a breakpoint, a tracepoint and an interceptor by asking whether the process may stop, because a breakpoint in production is an outage

**Use when:** deciding how to observe a native function on a live or shared system

**Avoid when:** the process is a local disposable test instance you fully control

## Procedure

1. Decide whether the process may pause even briefly.
2. If it may not, choose an interceptor or a tracepoint, never a stopping breakpoint.
3. If it may, choose a breakpoint and configure it to auto-continue after logging.
4. Check whether the debugger attach itself is blocked by the platform.
5. Record the chosen mechanism and the reason in the plan.
6. Test the mechanism on a disposable instance before the shared one.

## Signals

- The target has a watchdog that kills it when paused.
- Attaching a debugger is blocked by ptrace restrictions.
- The service is shared and a pause affects other users.
- A breakpoint that auto-continues still adds enough latency to trip a timeout.

## Patterns

**1. Non-stopping first**

```text
gdb: return False from stop()  -> log and continue
```

**2. Interceptor instead**

```text
frida Interceptor.attach  -> no stop at all
```

**3. Check ptrace**

```text
cat /proc/sys/kernel/yama/ptrace_scope  -> 1 means restricted attach
```

## Pitfalls

- Attaching a stopping breakpoint to a shared service and causing a stall.
- Assuming ptrace is allowed on a hardened host.
- Auto-continuing a breakpoint that still costs milliseconds per call in a hot loop.

## Done when

- The mechanism is chosen against an explicit statement about pausing.
- The plan records why a stopping breakpoint was or was not acceptable.

## References

- [GDB - breakpoint commands](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Break-Commands.html)
- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
