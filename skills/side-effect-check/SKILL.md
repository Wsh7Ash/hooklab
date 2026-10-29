---
name: side-effect-check
description: "Check the target's own logs, files and network state after the hook, so an instrumentation side effect is not mistaken for target behaviour. Use when the capture is used to claim that the target did or did not do something"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, side-effects]
---

# Side Effect Check

> Check the target's own logs, files and network state after the hook, so an instrumentation side effect is not mistaken for target behaviour

**Use when:** the capture is used to claim that the target did or did not do something

**Avoid when:** the target is a pure function with no external effects

## Procedure

1. List the external effects the target can produce: logs, files, sockets.
2. Record the state of each before the run.
3. Run with the hook attached and capture new effects.
4. Attribute each effect to the target or to the instrumentation.
5. Remove or explain any effect caused by the hook itself.
6. Store the effect list with the evidence.

## Signals

- A log line appears that mentions the debugger or the hook library.
- A temporary file exists only on hooked runs.
- The target retries a network call because the hook slowed it down.
- The hook's log output lands in the target's own log stream.

## Patterns

**1. Attribute each effect**

```text
target wrote audit.log
tool wrote /tmp/hooklab-*.log  -> separated
```

**2. Quiet hooks**

```text
log to a private file descriptor, not the target's stdout
```

**3. Retry detection**

```text
hooked run produces 2 requests where unhooked produced 1  -> perturbation
```

## Pitfalls

- Counting the hook's own log lines as target activity.
- Missing that a slower hook triggered a retry and duplicated a request.
- Leaving temporary artefacts that the next run reads as input.

## Done when

- Every observed effect is attributed to the target or the instrumentation.
- Instrumentation artefacts are removed or clearly labelled.

## References

- [Frida - Script output](https://frida.re/docs/javascript-api/#console)
- [Linux - strace and file effects](https://man7.org/linux/man-pages/man1/strace.1.html)
