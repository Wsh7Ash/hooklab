---
name: dependency-map-first
description: "Map the libraries and runtimes the target loads before choosing a hook, because the cheapest hook point is often a dependency rather than the target itself. Use when starting on an unfamiliar binary, an Electron app, a JVM service or a Go binary"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, recon]
---

# Dependency Map First

> Map the libraries and runtimes the target loads before choosing a hook, because the cheapest hook point is often a dependency rather than the target itself

**Use when:** starting on an unfamiliar binary, an Electron app, a JVM service or a Go binary

**Avoid when:** the target is a small statically linked binary you already understand

## Procedure

1. List the loaded modules with their paths, sizes and base addresses.
2. Identify the runtime: native, JVM, CLR, V8 or a language interpreter.
3. Note which dependencies parse the input you care about.
4. Choose the highest layer that still sees the raw value, not the lowest.
5. Record the module list with build ids in the plan's context.
6. Re-list after startup, since plugins and interpreters load late.

## Signals

- The target is a thin wrapper around a library that does the parsing.
- A JavaScript runtime loads after the window appears.
- The interesting logic lives in a plugin loaded on demand.
- The binary is mostly a launcher for a service in another language.

## Patterns

**1. Module table**

```text
libfoo.so 0x7f3c00000000 1.2 MiB build 9f2a...  -> the anchor list
```

**2. Runtime first**

```text
V8 present -> hook the JS layer, not the syscall layer
```

**3. Late loads**

```text
compare module list at launch and after 5s  -> plugins appear
```

## Pitfalls

- Hooking at the syscall layer when a library above it already has the plaintext.
- Missing a late-loaded plugin that performs the actual parsing.
- Treating a launcher binary as the application and hooking its stub functions.

## Done when

- The runtime and the module that performs the interesting work are both named.
- The hook layer is chosen and justified in the plan.

## References

- [Frida - Process.enumerateModules](https://frida.re/docs/javascript-api/#process)
- [OWASP MASTG - runtime instrumentation](https://mas.owasp.org/MASTG/)
