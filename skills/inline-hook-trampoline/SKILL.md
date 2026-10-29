---
name: inline-hook-trampoline
description: "Overwrite the function prologue with a jump and keep the displaced instructions in a trampoline, so the original still runs correctly. Use when the function cannot be intercepted at the boundary and the body must be patched"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, native]
---

# Inline Hook Trampoline

> Overwrite the function prologue with a jump and keep the displaced instructions in a trampoline, so the original still runs correctly

**Use when:** the function cannot be intercepted at the boundary and the body must be patched

**Avoid when:** an interceptor or GOT patch achieves the same result with less risk

## Procedure

1. Disassemble enough prologue instructions to cover the jump size.
2. Copy those instructions into an executable trampoline buffer.
3. Fix up any relative branch in the copied bytes.
4. Write a jump to the hook at the function entry.
5. Jump back to the instruction after the displaced block from the trampoline.
6. Restore the original bytes when the window closes.

## Signals

- The displaced instruction is a relative jump that breaks when moved.
- Another tool has already placed a breakpoint byte at the entry.
- The trampoline page is not executable and the call faults.
- The hook works until a signal handler lands mid-patch.

## Patterns

**1. Copy and fix**

```text
relocate the prologue, rebase rip-relative operands  -> trampoline runs
```

**2. Atomic patch**

```text
suspend threads, patch, resume  -> avoids executing half a jump
```

**3. Restore bytes**

```text
keep the original prologue bytes  -> required for teardown
```

## Pitfalls

- Copying a PC-relative instruction into a trampoline without rebasing it.
- Patching while other threads execute the prologue.
- Forgetting that some functions are too short to hold a jump safely.

## Done when

- The trampoline executes the displaced instructions and returns correctly.
- Original bytes are saved and restored at teardown.

## References

- [Frida - Interceptor.replace](https://frida.re/docs/javascript-api/#interceptor)
- [Intel - instruction set reference](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
