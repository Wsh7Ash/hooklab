---
name: script-hook-vs-native-hook
description: "Choose an interpreter trace for a Python, Ruby or Node target and a native hook only when the value crosses into native code, because the layers see different things. Use when the target is an interpreted application with native dependencies"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, interpreters]
---

# Script Hook Versus Native Hook

> Choose an interpreter trace for a Python, Ruby or Node target and a native hook only when the value crosses into native code, because the layers see different things

**Use when:** the target is an interpreted application with native dependencies

**Avoid when:** the target is a single native binary with no scripting layer

## Procedure

1. Determine which layer holds the value you need in readable form.
2. Use the interpreter's own tracing facility when the value is a Python object.
3. Use a native hook when the value is a byte buffer crossing a library boundary.
4. Record which layer was used and what it could not see.
5. Check that a script-level hook does not perturb timing-sensitive paths.
6. Cross-check one capture between the two layers where both can see the value.

## Signals

- The interpreter hook sees a dict while the native call sees a serialized buffer.
- The native hook sees ciphertext where the script had plaintext.
- A script hook adds noticeable overhead to a hot loop.
- The script hook fires for a function that the native trace never shows.

## Patterns

**1. Script layer**

```text
sys.setprofile  -> sees Python locals by name
```

**2. Native layer**

```text
Interceptor.attach on the C function  -> sees raw buffers
```

**3. Cross-check**

```text
same value, two layers  -> confirms neither is transforming it
```

## Pitfalls

- Hooking native code to read a value that is still a Python object there.
- Ignoring that a script hook changes the timing of a race-sensitive path.
- Reporting a native buffer as if it were the application's string.

## Done when

- The layer is chosen because it holds the value in readable form.
- One value is cross-checked across layers where possible.

## References

- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
- [Node - inspector](https://nodejs.org/api/inspector.html)
