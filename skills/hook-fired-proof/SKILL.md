---
name: hook-fired-proof
description: "Prove the hook actually fired before interpreting anything it captured, because an empty capture and a wrong hook look identical in a summary. Use when any plan that claims a value was observed at run time"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, evidence]
---

# Hook Fired Proof

> Prove the hook actually fired before interpreting anything it captured, because an empty capture and a wrong hook look identical in a summary

**Use when:** any plan that claims a value was observed at run time

**Avoid when:** never; this is the first check on every capture set

## Procedure

1. Count events per hook target during the run.
2. Assert the count is greater than zero for every hook the claim depends on.
3. Print the install time and the first event time.
4. If a hook never fired, check resolution before suspecting the target.
5. Record the counters with the capture so a reader can verify.
6. Treat a zero count as a failed run, not as evidence of absence.

## Signals

- The capture file is empty but the plan reports success.
- Install count is one and event count is zero.
- The hook fired before the trigger, meaning it observed the wrong call.
- A hook fires only after the window closes.

## Patterns

**1. Counters per hook**

```text
check_password: 1 call, 1 return
validate: 0 calls  -> the second hook is broken, not the target
```

**2. Timeline**

```text
installed 12:00:00.100, first event 12:00:00.180  -> after install
```

**3. Zero means failed**

```text
hits == 0 -> resolution bug, not 'the function was never called'
```

## Pitfalls

- Reading an empty capture as proof that the code path never ran.
- Counting events from a warm-up request and calling them the test run.
- Assuming a hook installed after the call could have observed it.

## Done when

- Every hook the claim depends on has a non-zero event count.
- Install and first-event times are recorded.

## References

- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
- [Python - sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile)
