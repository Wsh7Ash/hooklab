---
name: hook-idempotence
description: "Make installing the hook twice harmless, because scripts reload, sessions reconnect and a doubled hook produces doubled captures. Use when the hook script can be reloaded, or the same function is hooked by two parts of the plan"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, instrument, reliability]
---

# Hook Idempotence

> Make installing the hook twice harmless, because scripts reload, sessions reconnect and a doubled hook produces doubled captures

**Use when:** the hook script can be reloaded, or the same function is hooked by two parts of the plan

**Avoid when:** the hook is installed once in a process that runs to completion

## Procedure

1. Track which targets are already hooked in the script's state.
2. Skip installation when the target is already present.
3. Detect a previous installation that the current script did not create.
4. Ensure a reload replaces rather than stacks the hook.
5. Add a test that runs the plan twice and checks the capture count.
6. Record the installed count in the results.

## Signals

- Every call appears twice in the capture after a reload.
- The second install throws an error that the first did not.
- Capture count doubles without the target's call count changing.
- Unload leaves the hook installed, so the next attach stacks another.

## Patterns

**1. Guard the set**

```text
if (hooked.has(key)) return; hooked.add(key);  -> install once
```

**2. Reload replaces**

```text
detach the previous listener before attaching the new one
```

**3. Double-run test**

```text
run twice, expect N captures, not 2N  -> asserted
```

## Pitfalls

- Re-running a setup script and silently doubling every captured event.
- Assuming unload removes all listeners when one was installed manually.
- Detecting duplicates by value instead of by call, which hides real repeated calls.

## Done when

- Installing twice yields one hook and one capture per call.
- A repeated run is checked against the expected capture count.

## References

- [Frida - Interceptor.detachAll](https://frida.re/docs/javascript-api/#interceptor)
- [Frida - reloading scripts](https://frida.re/docs/modes/)
