---
name: return-value-capture
description: "Capture the return value as its own event, because the arguments alone cannot show which branch the function took. Use when the function returns a decision, a length or a status that explains the behaviour"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, capture, returns]
---

# Return Value Capture

> Capture the return value as its own event, because the arguments alone cannot show which branch the function took

**Use when:** the function returns a decision, a length or a status that explains the behaviour

**Avoid when:** the function returns void and all the information is in its out-parameters

## Procedure

1. Identify the return type from the source or the ABI.
2. Hook the return event and read the value in the correct width.
3. Interpret the value with the type, not as a raw integer.
4. Pair each return with its matching call using a sequence number.
5. Capture out-parameter buffers separately at return time.
6. Record the interpretation rule in the plan.

## Signals

- The return value is a pointer to a struct rather than a scalar.
- An error code is returned as a negative errno value.
- The function returns early on one path, so no return event pairs with a call.
- The same numeric value means different things per call site.

## Patterns

**1. Pair by sequence**

```text
seq 4 call verify / seq 5 return verify value=False  -> matched
```

**2. Type the value**

```text
read as int32, not int64  -> avoids a sign-extension artefact
```

**3. Out-parameter read**

```text
read the buffer argument at return  -> the function filled it
```

## Pitfalls

- Reading a return value at call time, before the function has produced it.
- Interpreting an errno-style negative as a large unsigned integer.
- Missing that a function can return through an out-parameter and a status code.

## Done when

- Return values are captured as their own event and typed correctly.
- Calls and returns are paired by sequence number.

## References

- [Frida - Interceptor onLeave](https://frida.re/docs/javascript-api/#interceptor)
- [Python - sys.setprofile return events](https://docs.python.org/3/library/sys.html#sys.setprofile)
