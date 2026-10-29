---
name: plt-got-identification
description: "Locate the PLT stub and GOT entry for an imported function, which is the stable place to patch when the real function lives in a relocatable library. Use when the hook targets a call made by the binary rather than every caller in the process"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, elf]
---

# PLT GOT Identification

> Locate the PLT stub and GOT entry for an imported function, which is the stable place to patch when the real function lives in a relocatable library

**Use when:** the hook targets a call made by the binary rather than every caller in the process

**Avoid when:** the function is called through a vtable or a function pointer resolved at run time

## Procedure

1. Find the relocation entry for the symbol and read its GOT offset.
2. Find the PLT stub that jumps through that GOT slot.
3. Confirm that patching the GOT entry affects only this binary's calls.
4. Record the section and offset of both, with the file's build id.
5. Check RELRO: a full RELRO binary makes the GOT read-only after startup.
6. If the GOT is read-only, hook the function body instead and say why.

## Signals

- The GOT entry is in a read-only page after startup, indicating full RELRO.
- The symbol is imported but never called, so no PLT stub exists.
- The binary calls the function through a pointer stored in .data.rel.ro.
- Patching the GOT changes behaviour for this binary but not for libraries it loads.

## Patterns

**1. Relocation to GOT**

```text
readelf -r ./target | grep strcmp  -> 000000601018 R_X86_64_JUMP_SLOT strcmp
```

**2. Scope of a GOT patch**

```text
only calls from this binary go through this slot  -> per-binary hook
```

**3. RELRO check**

```text
readelf -l ./target | grep GNU_RELRO  -> full RELRO means the GOT is read-only
```

## Pitfalls

- Writing to a GOT entry protected by full RELRO and crashing the process.
- Assuming a GOT patch affects library-internal callers, which use their own PLT.
- Patching the PLT stub instead of the GOT slot and breaking the resolver path.

## Done when

- The relocation, GOT slot and PLT stub are recorded with their build id.
- RELRO state is checked and the patch method reflects it.

## References

- [ELF - System V ABI specification](https://refspecs.linuxfoundation.org/elf/elf.pdf)
- [Frida - Interceptor.replace](https://frida.re/docs/javascript-api/#interceptor)
