---
name: process-state-check
description: "Compare the process's state before and after instrumentation, so a leaked thread, file descriptor or open session is caught before you walk away. Use when the instrumented process continues running after the session, especially a shared service"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, state]
---

# Process State Check

> Compare the process's state before and after instrumentation, so a leaked thread, file descriptor or open session is caught before you walk away

**Use when:** the instrumented process continues running after the session, especially a shared service

**Avoid when:** the process is killed at the end of the test by design

## Procedure

1. Capture the process's thread count, open descriptors and connections before attaching.
2. Repeat the capture after detaching.
3. Compare and list any difference.
4. Explain or close each new descriptor or connection.
5. Check that no debugger or agent thread remains.
6. Record both snapshots in the session notes.

## Signals

- A new socket remains open after the tool exits.
- An extra thread persists, indicating a lingering agent.
- Open file descriptors grow across sessions.
- The process holds a file open that the tool created.

## Patterns

**1. Snapshot pair**

```text
threads 12 -> 13  -> one agent thread must be accounted for
```

**2. Descriptor diff**

```text
/proc/<pid>/fd compared before and after  -> new socket found
```

**3. Explain or close**

```text
new fd is the tool's log file  -> close it
```

## Pitfalls

- Leaving an agent thread running in a long-lived service.
- Ignoring a socket the tool opened to a remote endpoint.
- Comparing counts without identifying which descriptor is new.

## Done when

- Threads and descriptors are compared and every difference explained.
- No tool-owned descriptor or thread remains.

## References

- [Linux - proc filesystem](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Frida - detaching](https://frida.re/docs/javascript-api/#device)
