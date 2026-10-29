---
name: injection-window
description: "Define the window during which the hook is installed, so a temporary observation does not remain attached for the life of the process. Use when the hook is installed for one request, one transaction or one test case"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, scope]
---

# Injection Window

> Define the window during which the hook is installed, so a temporary observation does not remain attached for the life of the process

**Use when:** the hook is installed for one request, one transaction or one test case

**Avoid when:** the hook must run for the whole session and the plan says so

## Procedure

1. State the start and end condition of the observation window.
2. Install the hook only when the start condition is met.
3. Detach or disable it when the end condition is met.
4. Verify with a counter that no capture occurred outside the window.
5. Record the window boundaries in the results.
6. If the window is the whole session, say so explicitly rather than leaving it implicit.

## Signals

- Captures continue after the test case finished.
- The hook is still attached when the process is handed back to the user.
- Events from a warm-up request appear in the capture.
- The plan has no statement about when observation stops.

## Patterns

**1. Explicit window**

```text
enable at request start, disable in the finally block  -> nothing leaks
```

**2. Counter check**

```text
captures outside window == 0  -> asserted, not assumed
```

**3. Whole-session note**

```text
window: full process lifetime  -> stated, so the reader knows
```

## Pitfalls

- Leaving a hook installed after the test and changing later behaviour silently.
- Capturing warm-up traffic and reporting it as the test result.
- Assuming a finally block runs when the target exits abruptly.

## Done when

- The window is stated and enforced by enabling and disabling the hook.
- No capture is recorded outside the stated window.

## References

- [Frida - Script.unload](https://frida.re/docs/javascript-api/#script)
- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
