---
name: plt-got-patching
description: "Patch the GOT slot so only this binary's calls are redirected, which is narrower and more stable than patching the shared library body. Use when the hook should affect one binary's calls to an imported function"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, elf]
---

# PLT GOT Patching

> Patch the GOT slot so only this binary's calls are redirected, which is narrower and more stable than patching the shared library body

**Use when:** the hook should affect one binary's calls to an imported function

**Avoid when:** full RELRO makes the GOT read-only, or the call goes through a function pointer

## Procedure

1. Locate the relocation and its GOT slot for the symbol.
2. Confirm the page is writable, or plan for RELRO handling.
3. Save the original slot value before writing.
4. Write the address of your replacement function into the slot.
5. Call the original through the saved pointer from your replacement.
6. Restore the original slot value when the window closes.

## Signals

- The GOT page is mapped read-only after startup under full RELRO.
- Calls from inside the library still reach the original function.
- The replacement runs but the original is never called, breaking behaviour.
- The slot changes again after a lazy binding resolves.

## Patterns

**1. Save then swap**

```text
orig = ptr.readPointer(); ptr.writePointer(replacement);  -> restore later
```

**2. Call through**

```text
const original = new NativeFunction(orig, 'int', ['pointer','pointer']);
```

**3. Scope note**

```text
per-binary patch  -> library-internal callers are unaffected
```

## Pitfalls

- Writing to a RELRO-protected GOT and crashing on the first call.
- Losing the original pointer so behaviour cannot be restored or passed through.
- Assuming a GOT patch changes every caller in the process.

## Done when

- The original pointer is saved and used by the replacement.
- The slot is restored and the target still behaves normally afterwards.

## References

- [ELF - relocation types](https://refspecs.linuxfoundation.org/elf/elf.pdf)
- [Frida - Memory.patchCode](https://frida.re/docs/javascript-api/#memory)
