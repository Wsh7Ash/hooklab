---
name: call-convention-identification
description: "Identify how arguments reach the function before reading them, because a wrong convention yields plausible-looking values from the wrong registers. Use when the hook reads arguments at entry on a binary whose platform or build you did not produce"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, abi]
---

# Call Convention Identification

> Identify how arguments reach the function before reading them, because a wrong convention yields plausible-looking values from the wrong registers

**Use when:** the hook reads arguments at entry on a binary whose platform or build you did not produce

**Avoid when:** the hook runs in a managed runtime that exposes arguments by name

## Procedure

1. Identify the architecture and the platform's default calling convention.
2. Check for explicitly attributed conventions in the source or the disassembly.
3. Map each argument to its register or stack slot for that convention.
4. Confirm the mapping by observing a call whose arguments you control.
5. Record the convention in the plan next to the capture fields.
6. Re-check on a different platform build before reusing the plan.

## Signals

- The first argument appears in a different register than expected.
- A variadic call passes the count in a register the hook does not read.
- The platform uses a different convention for floating point arguments.
- Arguments appear on the stack because the function takes more than the register count.

## Patterns

**1. SysV order**

```text
rdi, rsi, rdx, rcx, r8, r9 then stack  -> arg0..arg5
```

**2. Windows x64**

```text
rcx, rdx, r8, r9 then shadow space  -> different from SysV
```

**3. Verify with a known call**

```text
call with ('AAAA','BBBB') and confirm which register holds which
```

## Pitfalls

- Assuming System V ordering on a Windows x64 build and reading the wrong argument.
- Reading argN without accounting for the shadow space on Windows.
- Ignoring floating point registers and reporting an integer reinterpretation.

## Done when

- The convention is named and each captured argument is mapped to a register or slot.
- A controlled call confirms the mapping before the real capture is used.

## References

- [System V - AMD64 ABI](https://refspecs.linuxfoundation.org/elf/x86_64-abi-0.99.pdf)
- [Microsoft - x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention)
