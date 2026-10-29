---
name: function-address-verification
description: "Disassemble the resolved address before trusting it, because a symbol can resolve to a thunk, a resolver stub or a different overload than you meant. Use when the hook is installed by address or when the resolved bytes look different from the expected function"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, verification]
---

# Function Address Verification

> Disassemble the resolved address before trusting it, because a symbol can resolve to a thunk, a resolver stub or a different overload than you meant

**Use when:** the hook is installed by address or when the resolved bytes look different from the expected function

**Avoid when:** the hook is installed through a high-level API that validates the target

## Procedure

1. Read the first dozen instructions at the resolved address.
2. Check for a jump thunk that forwards to another address, and follow it.
3. Check for a lazy resolver stub in a PLT entry and resolve past it.
4. Compare the prologue with the same function exported by the library file on disk.
5. Record the resolved address and the bytes you saw.
6. Re-resolve after any library reload, since addresses move with ASLR.

## Signals

- The address contains a single unconditional jump.
- The bytes differ from the on-disk library at the same symbol.
- The address is inside a PLT section rather than a text section.
- A second call resolves to a different address than the first.

## Patterns

**1. Thunk detection**

```text
jmp qword ptr [rip + 0x2f1a]  -> follow the pointer, do not hook here
```

**2. On-disk compare**

```text
objdump -d --start-address=0x... ./libfoo.so  -> same prologue?
```

**3. ASLR awareness**

```text
record the module base with the address  -> offsets stay stable
```

## Pitfalls

- Hooking a lazy resolver stub and capturing the resolver instead of the function.
- Comparing addresses between runs when ASLR moved the module base.
- Assuming the exported symbol is the implementation rather than a versioned alias.

## Done when

- The resolved bytes are inspected and recorded, not just the address.
- Any thunk is followed and the final implementation is the hook target.

## References

- [Frida - Interceptor.attach](https://frida.re/docs/javascript-api/#interceptor)
- [objdump - disassembly options](https://man7.org/linux/man-pages/man1/objdump.1.html)
