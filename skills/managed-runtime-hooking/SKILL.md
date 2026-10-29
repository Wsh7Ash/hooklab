---
name: managed-runtime-hooking
description: "Hook at the runtime layer for JVM, CLR or V8 targets, where the method has a name and typed arguments instead of registers. Use when the target runs on a JVM, .NET or a JavaScript engine and the logic is in managed code"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, runtime]
---

# Managed Runtime Hooking

> Hook at the runtime layer for JVM, CLR or V8 targets, where the method has a name and typed arguments instead of registers

**Use when:** the target runs on a JVM, .NET or a JavaScript engine and the logic is in managed code

**Avoid when:** the value you need is produced by native code the runtime calls into

## Procedure

1. Identify the runtime version and its instrumentation support.
2. Resolve the class or module and the method by name and signature.
3. Hook the overload you actually want, since several may share a name.
4. Read typed arguments through the runtime API rather than raw memory.
5. Watch for JIT inlining that removes the method from the call path.
6. Record the runtime version, since hooking APIs change between them.

## Signals

- The class is loaded lazily and does not exist at attach time.
- The method has three overloads and only one carries the value.
- The JIT inlines the method so the hook never fires.
- The runtime needs a debugging flag to allow instrumentation.

## Patterns

**1. Resolve by signature**

```text
Java.use('com.example.Auth').check(java.lang.String)  -> exact overload
```

**2. Load early**

```text
hook the class loader or use a deferred hook  -> catch lazy classes
```

**3. JIT check**

```text
disable inlining or hook the caller if the hook never fires
```

## Pitfalls

- Hooking a method name that resolves to the wrong overload.
- Attaching before the class loads and concluding the hook is broken.
- Assuming a managed hook shows values that native code transforms later.

## Done when

- The overload is identified by full signature and the hook fires.
- The runtime version and any required flags are recorded.

## References

- [Frida - Java API](https://frida.re/docs/javascript-api/#java)
- [Frida - ObjC API](https://frida.re/docs/javascript-api/#objc)
