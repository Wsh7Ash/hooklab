---
name: argument-formatting
description: "Format captured arguments into a stable, comparable text form, because one inconsistent representation makes a capture set impossible to diff. Use when the capture will be compared across runs or reviewed by someone else"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, format]
---

# Argument Formatting

> Format captured arguments into a stable, comparable text form, because one inconsistent representation makes a capture set impossible to diff

**Use when:** the capture will be compared across runs or reviewed by someone else

**Avoid when:** the capture is a single value inspected once in a debugger

## Procedure

1. Choose one representation per type: hex for pointers, quoted text for strings, decimal for lengths.
2. Escape control characters instead of printing them raw.
3. Mark truncated values explicitly with their original length.
4. Keep field names consistent with the plan's capture list.
5. Never include an absolute address without the module base alongside it.
6. Check the same value twice and confirm the formatting is identical.

## Signals

- One capture shows a pointer where another shows a string for the same field.
- Terminal output contains control characters that reorder the line.
- Truncated strings look complete because the marker is missing.
- The same call formats differently between two runs.

## Patterns

**1. Typed formatting**

```text
password='hunter2' (str, 7 bytes)  len=7 ptr=0x7f..  -> explicit
```

**2. Escape control bytes**

```text
replace non-printable bytes with \xNN  -> log stays one line
```

**3. Truncation marker**

```text
'AAAA...' (120 of 4096 bytes)  -> the reader knows
```

## Pitfalls

- Printing a raw buffer that contains newlines and corrupting the capture format.
- Dropping the truncation marker so a prefix looks like the whole value.
- Mixing decimal and hex for the same field across runs.

## Done when

- Each captured field has one documented representation.
- Truncation and escaping are visible in the output.

## References

- [Python - repr and string escapes](https://docs.python.org/3/library/functions.html#repr)
- [Frida - NativePointer.toString](https://frida.re/docs/javascript-api/#nativepointer)
