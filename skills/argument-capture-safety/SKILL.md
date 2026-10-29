---
name: argument-capture-safety
description: "Capture arguments without dereferencing anything you have not validated, because reading a bad pointer inside a hook crashes the process you are observing. Use when the hook reads strings, buffers or structs from raw pointers"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, safety]
---

# Argument Capture Safety

> Capture arguments without dereferencing anything you have not validated, because reading a bad pointer inside a hook crashes the process you are observing

**Use when:** the hook reads strings, buffers or structs from raw pointers

**Avoid when:** the hook runs in a managed runtime where arguments are typed objects

## Procedure

1. Treat every pointer argument as untrusted until proven readable.
2. Check the pointer is non-null and within a mapped range before reading.
3. Bound the read to a fixed maximum length.
4. Catch any read fault and log a marker instead of propagating it.
5. Record the maximum length used, so a truncated value is recognised.
6. Test the hook against a call with a deliberately invalid pointer.

## Signals

- The captured string is empty because the pointer was null.
- The process crashes only when the hook is attached.
- A captured value is longer than the buffer the caller allocated.
- The hook works on one call and crashes on a different code path.

## Patterns

**1. Validate then read**

```text
if (ptr.isNull()) return;  then readUtf8String(200)
```

**2. Bound the read**

```text
Memory.readUtf8String(ptr, 120)  -> never unbounded
```

**3. Fault marker**

```text
catch the exception and log '<unreadable>' instead of crashing
```

## Pitfalls

- Reading an unbounded string from a pointer that is not null-terminated.
- Assuming an argument is always non-null because the first call had one.
- Letting an exception in the hook propagate into the target's call path.

## Done when

- Every pointer read is null-checked and length-bounded.
- A hook run with an invalid pointer logs a marker instead of crashing.

## References

- [Frida - Memory API](https://frida.re/docs/javascript-api/#memory)
- [Frida - NativePointer](https://frida.re/docs/javascript-api/#nativepointer)
