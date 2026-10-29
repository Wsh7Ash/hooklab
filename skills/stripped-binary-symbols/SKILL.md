---
name: stripped-binary-symbols
description: "Recover a usable anchor when the binary is stripped, by resolving through the dynamic table, a library call or a byte pattern instead of a local symbol. Use when the target has no debug symbols and nm or readelf shows no matching local function"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, symbols]
---

# Stripped Binary Symbols

> Recover a usable anchor when the binary is stripped, by resolving through the dynamic table, a library call or a byte pattern instead of a local symbol

**Use when:** the target has no debug symbols and nm or readelf shows no matching local function

**Avoid when:** full debug symbols are available and the function resolves by name

## Procedure

1. Check the dynamic symbol table, which survives stripping for exported functions.
2. Check whether the function is reachable through a library the process already calls.
3. If neither works, locate the call site in the caller and hook the caller instead.
4. As a last resort, build a byte-pattern anchor from the function's prologue and verify it is unique.
5. Confirm the anchor resolves to exactly one address before attaching.
6. Record which method was used and why the simpler ones failed.

## Signals

- readelf shows an empty symbol table but exported functions still resolve.
- The function is inlined into the caller, so no separate symbol exists.
- The prologue pattern matches several addresses in the binary.
- The stripped binary still exports the function for its own plugins to use.

## Patterns

**1. Dynamic table first**

```text
readelf --dyn-syms ./target | grep -i parse  -> exported, still resolvable
```

**2. Hook the caller**

```text
hook the plugin entry that calls the static parser  -> same information, stable anchor
```

**3. Unique pattern**

```text
f3 0f 1e fa 55 48 89 e5  -> verify a single hit before attaching
```

## Pitfalls

- Assuming a stripped binary has no symbols at all and giving up before the dynamic table.
- Attaching to a byte pattern that matches three addresses and hooking the wrong one.
- Hooking an inlined function's supposed address when no call exists.

## Done when

- An anchor is resolved and shown to be unique in the address space.
- The plan records which resolution method was needed.

## References

- [readelf - ELF symbol tables](https://man7.org/linux/man-pages/man1/readelf.1.html)
- [Frida - Module.enumerateExports](https://frida.re/docs/javascript-api/#module)
