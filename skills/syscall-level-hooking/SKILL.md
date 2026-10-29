---
name: syscall-level-hooking
description: "Hook the syscall boundary when every higher layer encrypts or batches the data, accepting that arguments are raw buffers rather than typed values. Use when the library-level hook sees only ciphertext and the plaintext exists briefly at a syscall"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, syscall]
---

# Syscall Level Hooking

> Hook the syscall boundary when every higher layer encrypts or batches the data, accepting that arguments are raw buffers rather than typed values

**Use when:** the library-level hook sees only ciphertext and the plaintext exists briefly at a syscall

**Avoid when:** a higher-level hook already exposes the value in a readable form

## Procedure

1. Identify the syscall number and arguments for the operation of interest.
2. Attach at the syscall entry in the current process, not globally.
3. Read the buffer argument with a length bound before the call executes.
4. Log the syscall result separately from the input.
5. Account for the platform's syscall convention, which differs from the C ABI.
6. Record the syscall numbers used, since they are architecture specific.

## Signals

- The buffer holds plaintext only before the write, never after.
- Arguments arrive in registers that differ from the function ABI.
- The same data appears in several syscalls due to partial writes.
- A seccomp filter blocks syscall-level instrumentation.

## Patterns

**1. Read pre-call**

```text
onEnter: read the buffer;  onLeave: log the returned byte count
```

**2. Syscall numbering**

```text
x86_64 write = 1, read = 0  -> numbers differ on arm64
```

**3. Partial writes**

```text
loop over returned lengths  -> do not assume one call
```

## Pitfalls

- Reading the buffer after the syscall, when the kernel has already consumed it.
- Assuming function-ABI registers at the syscall boundary.
- Reporting one partial write as the whole message.

## Done when

- The buffer is captured before the syscall executes, with a documented length bound.
- The syscall numbers and convention are recorded in the plan.

## References

- [Linux man-pages - syscall](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [Frida - Syscall tracing](https://frida.re/docs/javascript-api/#interceptor)
