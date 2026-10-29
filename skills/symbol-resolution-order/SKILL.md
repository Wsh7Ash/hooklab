---
name: symbol-resolution-order
description: "Determine which definition a symbol resolves to at run time, because two loaded libraries can export the same name and the hook then lands on the wrong one. Use when several libraries in a process export the same symbol, or the target links a vendored copy of a common library"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, symbols]
---

# Symbol Resolution Order

> Determine which definition a symbol resolves to at run time, because two loaded libraries can export the same name and the hook then lands on the wrong one

**Use when:** several libraries in a process export the same symbol, or the target links a vendored copy of a common library

**Avoid when:** the binary is statically linked and there is only one definition in the address space

## Procedure

1. List every loaded module in the process and the order the loader searched them.
2. Search each module's dynamic symbol table for the target name.
3. Record which module the loader will pick, honouring interposition rules.
4. Resolve by module and symbol pair rather than by bare name.
5. Confirm the resolved address falls inside the expected module's range.
6. Re-check after any library is loaded late, since it can change the winner.

## Signals

- Two modules export the symbol and only one is the target's own copy.
- The resolved address is outside the module you expected.
- A vendored library is loaded before the system one and wins interposition.
- A late dlopen adds a third definition after your hook was installed.

## Patterns

**1. Module-qualified resolve**

```text
Module.getExportByName('libc.so.6', 'strcmp')  -> not the bare name
```

**2. Address sanity**

```text
resolved 0x7f3c... inside libc range 0x7f3c...-0x7f3d...  -> correct module
```

**3. Late load check**

```text
print loaded modules again after startup  -> catch a vendored copy
```

## Pitfalls

- Hooking by bare name and landing on a compatibility shim instead of the real function.
- Assuming the first match in a symbol dump is the one the process uses.
- Ignoring a statically linked copy inside the target binary itself.

## Done when

- The plan names both the module and the symbol.
- The resolved address is confirmed to lie inside that module.

## References

- [Frida - Module API](https://frida.re/docs/javascript-api/#module)
- [Linux man-pages - dlsym](https://man7.org/linux/man-pages/man3/dlsym.3.html)
