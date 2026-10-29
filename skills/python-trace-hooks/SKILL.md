---
name: python-trace-hooks
description: "Use sys.setprofile for call and return values rather than sys.settrace, because profile events carry the return value and cost far less. Use when the target is Python and the value of interest is a local variable or a return value"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, python]
---

# Python Trace Hooks

> Use sys.setprofile for call and return values rather than sys.settrace, because profile events carry the return value and cost far less

**Use when:** the target is Python and the value of interest is a local variable or a return value

**Avoid when:** you need line-level execution inside a function, which only settrace provides

## Procedure

1. Choose the target function and the names of the locals you need.
2. Install sys.setprofile, not sys.settrace, for call and return events.
3. Record frame locals by name at the call event.
4. Record the return value from the return event's argument.
5. Restore the previous profiler when the window closes.
6. Confirm the hook fired with a counter before trusting the capture.

## Signals

- The function is a C extension and never produces a Python frame.
- Locals are optimised away or renamed by the compiler.
- The profiler is already installed by another tool and gets replaced.
- Return events fire for every function, so the filter must be exact.

## Patterns

**1. Profile not trace**

```text
sys.setprofile(fn)  -> call and return only, cheaper than settrace
```

**2. Name the local**

```text
frame.f_locals.get('password')  -> captured by name
```

**3. Restore the profiler**

```text
previous = sys.getprofile(); try: ... finally: sys.setprofile(previous)
```

## Pitfalls

- Using settrace and paying line-level cost for a call-level question.
- Reading frame.f_locals for a variable that the compiler removed.
- Leaving the profiler installed and slowing every later call in the process.

## Done when

- The hook records named locals at call and the return value at return.
- The previous profiler is restored after the window.

## References

- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
- [Python - frame objects](https://docs.python.org/3/reference/datamodel.html#frame-objects)
