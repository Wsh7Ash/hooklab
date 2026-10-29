---
name: struct-and-buffer-reading
description: "Decode a struct by its declared layout rather than by guessing field offsets, so a padding difference does not shift every value you report. Use when the captured argument is a pointer to a struct or a packed binary record"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, memory]
---

# Struct and Buffer Reading

> Decode a struct by its declared layout rather than by guessing field offsets, so a padding difference does not shift every value you report

**Use when:** the captured argument is a pointer to a struct or a packed binary record

**Avoid when:** the argument is a scalar or a plain null-terminated string

## Procedure

1. Obtain the struct definition from the source or a header.
2. Record field offsets, widths and the platform's alignment rules.
3. Read each field with an explicit offset rather than sequential reads.
4. Verify the total struct size matches the expected layout.
5. Handle pointer fields by validating before dereferencing.
6. Record the layout version, since a rebuild can change it.

## Signals

- A field reads as garbage because padding shifted the offset.
- The struct contains a union whose active member depends on a tag field.
- The pointer fields point into a different module.
- The recorded size differs from the size the caller allocated.

## Patterns

**1. Explicit offsets**

```text
p.add(8).readU32()  -> field at its declared offset, not sequential
```

**2. Tag then read**

```text
switch (tag) { case 1: readInt(); ... }  -> union handled per tag
```

**3. Validate pointers**

```text
ptr.isNull() || !Process.findRangeByAddress(ptr)  -> skip
```

## Pitfalls

- Assuming no padding between a byte field and a pointer field.
- Reading a union member that the tag says is inactive.
- Dereferencing every pointer in a struct without a range check.

## Done when

- Field offsets come from the declared layout and the total size is verified.
- Union members are selected by their tag before reading.

## References

- [Frida - NativePointer arithmetic](https://frida.re/docs/javascript-api/#nativepointer)
- [C - structure alignment](https://en.cppreference.com/w/c/language/struct)
