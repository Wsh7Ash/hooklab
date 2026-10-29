---
name: library-vs-symbol-name
description: "Separate the library from the symbol in a hook plan, because the same symbol exists in many libraries and a library rename silently breaks the hook. Use when writing a hook plan that another person or agent will execute on a different system"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, planning]
---

# Library Versus Symbol Name

> Separate the library from the symbol in a hook plan, because the same symbol exists in many libraries and a library rename silently breaks the hook

**Use when:** writing a hook plan that another person or agent will execute on a different system

**Avoid when:** the target is a single self-contained binary with no shared dependencies

## Procedure

1. Record the library name as it appears in the loader, including version suffix.
2. Record the symbol as exported, including any leading underscore convention.
3. Note the platform the pair was observed on.
4. Add an alternative library name where distributions differ, such as libc versus libSystem.
5. Order the alternatives so the plan tries the exact match first.
6. Keep symbol and library in separate fields rather than one dotted string.

## Signals

- The library has a versioned soname that changes between distributions.
- The symbol is exported with a leading underscore on one platform.
- The same function exists in libc and in a vendored static copy.
- The plan mixes library and symbol into one path-like string.

## Patterns

**1. Split the pair**

```text
{"library": "libc.so.6", "symbol": "memcmp"}  -> two fields, no parsing
```

**2. Distro alternatives**

```text
libc.so.6 on glibc, libSystem.B.dylib on macOS  -> list both, exact first
```

**3. Underscore convention**

```text
macOS exports _memcmp; the tool strips the platform prefix
```

## Pitfalls

- Encoding the library and symbol as one string that a tool then splits incorrectly.
- Omitting the version suffix and binding to a different soname on another host.
- Forgetting platform decoration and concluding the symbol does not exist.

## Done when

- Library and symbol are separate, explicit fields in the plan.
- Alternative names are listed for platforms the plan claims to support.

## References

- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
- [Oracle - dynamic linking and symbol resolution](https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter3-1.html)
