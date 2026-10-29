---
name: string-safety-bounds
description: "Bound every string read and say so in the output, because an unbounded read either crashes the target or silently swallows the value you wanted. Use when the captured value is a C string whose length the target controls"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, safety]
---

# String Safety Bounds

> Bound every string read and say so in the output, because an unbounded read either crashes the target or silently swallows the value you wanted

**Use when:** the captured value is a C string whose length the target controls

**Avoid when:** the value is a managed string with a known length

## Procedure

1. Choose a maximum length that comfortably exceeds the expected value.
2. Read at most that many bytes, stopping at a null terminator.
3. Record whether the read hit the bound, which means the value is truncated.
4. Escape non-printable bytes rather than printing them raw.
5. Verify with a value longer than the bound that truncation is visible.
6. Keep the bound in the plan so a reader can judge completeness.

## Signals

- The captured string ends exactly at the bound with no terminator.
- The value contains embedded nulls and stops early.
- A longer input produces a longer capture, meaning the read was unbounded.
- The target crashes only when the hook reads the string.

## Patterns

**1. Bounded read**

```text
readUtf8String(ptr, 256)  -> never unbounded, always terminated
```

**2. Truncation flag**

```text
truncated = bytes == bound  -> recorded in the capture line
```

**3. Embedded nulls**

```text
log the byte length as well as the text  -> length exposes the tail
```

## Pitfalls

- Reading until a null that never arrives and walking into unmapped memory.
- Reporting a truncated value as if it were the complete string.
- Assuming text stops at the first null when the field is actually length-prefixed.

## Done when

- Every string read has an explicit bound recorded in the plan.
- Truncation is visible in the captured output.

## References

- [Frida - Memory.readUtf8String](https://frida.re/docs/javascript-api/#memory)
- [CWE-170 - improper null termination](https://cwe.mitre.org/data/definitions/170.html)
