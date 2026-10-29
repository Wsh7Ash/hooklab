---
name: detach-and-restore
description: "Detach every listener and restore the previous state at the end of the window, so the target is left exactly as it was found. Use when finishing any instrumentation session on a process that keeps running"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, safety]
---

# Detach and Restore

> Detach every listener and restore the previous state at the end of the window, so the target is left exactly as it was found

**Use when:** finishing any instrumentation session on a process that keeps running

**Avoid when:** the process is a disposable instance that is killed immediately afterwards

## Procedure

1. Keep a handle for every hook you install.
2. Detach in reverse order of installation.
3. Restore any previous handler, such as a prior profiler or signal handler.
4. Confirm the target still behaves normally after detaching.
5. Record the detach time and the listener count before and after.
6. If a listener cannot be removed, say so and explain the residual change.

## Signals

- The hook still fires after the script claims to have unloaded.
- The previous profiler is gone and the target runs slower.
- A signal handler installed by the tool is still in place.
- Detach throws because the listener was already removed.

## Patterns

**1. Keep hook handles**

```text
listeners = [...]; for listener in reversed(listeners): listener.detach()
```

**2. Restore the profiler**

```text
sys.setprofile(previous)  -> not None unless it was None
```

**3. Count check**

```text
before 3, after 0 installed listeners
```

## Pitfalls

- Setting the profiler to None and destroying another tool's instrumentation.
- Detaching in installation order and leaving a nested hook installed.
- Assuming unload removed listeners that were attached outside it.

## Done when

- Zero listeners remain and the previous handler is restored.
- Post-detach behaviour is confirmed normal.

## References

- [Frida - Script.unload](https://frida.re/docs/javascript-api/#script)
- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
