---
name: read-only-hook-discipline
description: "Keep hooks read-only unless changing behaviour is the point, because an accidental write turns an observation into an exploit and voids the evidence. Use when the hook is meant to reveal values rather than to bypass a check"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, safety]
---

# Read Only Hook Discipline

> Keep hooks read-only unless changing behaviour is the point, because an accidental write turns an observation into an exploit and voids the evidence

**Use when:** the hook is meant to reveal values rather than to bypass a check

**Avoid when:** the objective is explicitly to test a bypass, which is a different, riskier plan

## Procedure

1. Classify the plan as read-only or intrusive before writing any code.
2. In a read-only plan, only call logging and read-only memory APIs.
3. Never replace a return value, patch a branch or modify an argument.
4. Verify the target's behaviour is identical with and without the hook.
5. If behaviour must change, split it into a separate intrusive plan with cleanup.
6. State the classification in the plan and in any published writeup.

## Signals

- The hook changes a return value to force a success path.
- The plan patches a conditional jump to skip a check.
- The target behaves differently with the hook attached.
- The plan has no cleanup but modifies memory.

## Patterns

**1. Read-only rule**

```text
log args and return, never assign  -> behaviour identical
```

**2. Parity check**

```text
run the same input with and without the hook  -> same output
```

**3. Split the plans**

```text
observe.json (read-only) and bypass.json (intrusive, with cleanup)
```

## Pitfalls

- Forcing a branch to prove exploitability and then presenting the result as observation.
- Modifying one byte to make a comparison pass and calling it a bug.
- Mixing observation and tampering in one plan so the evidence cannot be trusted.

## Done when

- The plan states read-only or intrusive explicitly.
- A parity check shows identical behaviour when the plan claims read-only.

## References

- [Frida - Interceptor.replace](https://frida.re/docs/javascript-api/#interceptor)
- [OWASP MASTG - instrumentation risks](https://mas.owasp.org/MASTG/)
