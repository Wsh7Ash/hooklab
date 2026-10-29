---
name: inline-and-static-functions
description: "Recognise when the function you want does not exist separately in the binary, so the hook targets the caller or the library boundary instead. Use when the source shows a small helper and the symbol table does not, or the optimizer inlined it"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, optimisation]
---

# Inline and Static Functions

> Recognise when the function you want does not exist separately in the binary, so the hook targets the caller or the library boundary instead

**Use when:** the source shows a small helper and the symbol table does not, or the optimizer inlined it

**Avoid when:** the function is exported and clearly present in the symbol table

## Procedure

1. Check the symbol table for the function name at the expected optimisation level.
2. Inspect call sites to see whether the logic appears inline instead of as a call.
3. Choose the enclosing exported function as the hook point.
4. Or hook the boundary the data crosses, such as a read or a comparison in a library.
5. Confirm the alternative hook still reveals the value you need.
6. Record that the original function was inlined and why the substitute is equivalent.

## Signals

- The helper exists in the source but not in nm output.
- The call site contains the comparison directly instead of a call.
- The function is marked static and used once.
- Disabling optimisation makes the symbol appear again.

## Patterns

**1. Empirical check**

```text
nm -C ./target | grep parse_header  -> nothing, so it was inlined
```

**2. Hook the caller**

```text
hook handle_request and capture the same buffer it passed to the inlined helper
```

**3. Boundary hook**

```text
hook memcmp in the process to observe the comparison the inline code performs
```

## Pitfalls

- Concluding the code path does not exist because the symbol is missing.
- Hooking a rebuild with -O0 and reporting behaviour that the shipped build does not have.
- Choosing a boundary hook that misses the value because it is transformed first.

## Done when

- The substitute hook point is named and shown to reveal the same value.
- The plan states that the original function was inlined.

## References

- [GCC - optimisation options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
