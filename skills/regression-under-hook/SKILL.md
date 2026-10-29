---
name: regression-under-hook
description: "Run the target's own normal path under the hook, so an instrumented run that breaks ordinary behaviour is caught before the evidence is published. Use when the hook will be attached for more than one code path"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, regression]
---

# Regression Under Hook

> Run the target's own normal path under the hook, so an instrumented run that breaks ordinary behaviour is caught before the evidence is published

**Use when:** the hook will be attached for more than one code path

**Avoid when:** the hook is attached for a single isolated call in a test harness

## Procedure

1. Pick the ordinary path that shares the hooked function.
2. Run it unhooked and record the outcome.
3. Run it with the hook attached and compare.
4. Check that the ordinary path still returns the same result.
5. If it regresses, narrow the hook or add a condition.
6. Record the regression check in the results.

## Signals

- The legitimate login fails only when the hook is attached.
- The hook's read of a buffer changes a length field.
- A shared function is hooked for one caller and breaks another.
- The ordinary path is slower enough to hit a timeout.

## Patterns

**1. Legit path first**

```text
valid credentials still succeed under the hook  -> no regression
```

**2. Narrow the hook**

```text
hook only calls where the caller matches  -> other paths untouched
```

**3. Record both**

```text
unhooked 200, hooked 200 with identical body
```

## Pitfalls

- Only testing the malicious input and declaring the hook safe.
- Hooking a shared helper and breaking a second caller.
- Skipping the regression check because the capture looked correct.

## Done when

- The ordinary path produces the same result with and without the hook.
- Any narrowing of the hook is recorded.

## References

- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
- [OWASP MASTG - resilience testing](https://mas.owasp.org/MASTG/)
