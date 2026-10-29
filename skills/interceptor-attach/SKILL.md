---
name: interceptor-attach
description: "Attach an interceptor that logs and returns the original result, which is the least invasive way to observe a native function. Use when the target is a live process and you need every call with its arguments"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, native]
---

# Interceptor Attach

> Attach an interceptor that logs and returns the original result, which is the least invasive way to observe a native function

**Use when:** the target is a live process and you need every call with its arguments

**Avoid when:** the function is inlined or called through a pointer the interceptor cannot see

## Procedure

1. Resolve the module and symbol pair rather than a bare name.
2. Attach with an onEnter that only reads and logs.
3. Leave onLeave empty unless you need the return value.
4. Confirm the hook fires with a counter before running the real test.
5. Detach when the observation window closes.
6. Record the module, symbol and address in the results.

## Signals

- The counter stays at zero, meaning the resolution was wrong.
- The function fires far more often than the protocol suggests.
- onLeave reports a value the target never returns.
- Attaching throws because the function is already hooked by another tool.

## Patterns

**1. Minimal agent**

```text
Interceptor.attach(addr, { onEnter(args) { console.log(args[0].toInt32()); } });
```

**2. Counter proof**

```text
let hits = 0; onEnter() { hits++; }  -> assert hits > 0
```

**3. Clean detach**

```text
const listener = Interceptor.attach(...);  then listener.detach();
```

## Pitfalls

- Attaching by bare name and hitting a compatibility shim.
- Modifying an argument inside onEnter and changing the behaviour under test.
- Forgetting that a second attach on the same address stacks a second listener.

## Done when

- The hook fires, proven by a counter, before the real observation.
- The listener is detached at the end of the window.

## References

- [Frida - Interceptor.attach](https://frida.re/docs/javascript-api/#interceptor)
- [Frida - NativeFunction](https://frida.re/docs/javascript-api/#nativefunction)
