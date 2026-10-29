---
name: negative-control-hook
description: "Hook a function that must not be called on the tested path, so a hook that fires everywhere is exposed as unfiltered rather than informative. Use when the claim depends on a function being reached only under a specific condition"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, control]
---

# Negative Control Hook

> Hook a function that must not be called on the tested path, so a hook that fires everywhere is exposed as unfiltered rather than informative

**Use when:** the claim depends on a function being reached only under a specific condition

**Avoid when:** the plan observes the whole process deliberately and says so

## Procedure

1. Pick a function that should not run on the control path.
2. Install a counting hook on it with no logging.
3. Run the control input and confirm the count is zero.
4. Run the triggering input and confirm the count is greater than zero.
5. Record both counts in the results.
6. If the control count is non-zero, the path is broader than claimed.

## Signals

- The control function fires for both inputs, so the branch is not conditional.
- The control count exceeds the trigger count, indicating a shared path.
- Both counts are zero, meaning the hooks are not installed.
- The control fires only on the second run, suggesting state carry-over.

## Patterns

**1. Two counts**

```text
control input -> admin_check: 0
weak input    -> admin_check: 1  -> conditional path proven
```

**2. Silent counter**

```text
count only, no logging  -> negligible overhead
```

**3. Broad path finding**

```text
control also fires  -> the 'bypass' is not a bypass
```

## Pitfalls

- Choosing a control function that cannot run in either case, proving nothing.
- Logging the control hook and perturbing the timing of the real path.
- Skipping the control and assuming the branch was conditional.

## Done when

- The control count is zero and the trigger count is non-zero.
- Both counts appear in the results.

## References

- [OWASP MASTG - dynamic analysis](https://mas.owasp.org/MASTG/)
- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
