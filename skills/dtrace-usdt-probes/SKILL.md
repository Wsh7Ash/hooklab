---
name: dtrace-usdt-probes
description: "Use the probes the application already publishes, which are cheaper and more stable than patching a function that may be optimised or inlined. Use when the target ships USDT or DTrace probes, or the platform supports them"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, hook, tracing]
---

# DTrace USDT Probes

> Use the probes the application already publishes, which are cheaper and more stable than patching a function that may be optimised or inlined

**Use when:** the target ships USDT or DTrace probes, or the platform supports them

**Avoid when:** the application publishes no probes and adding them requires a rebuild

## Procedure

1. List the probes the binary publishes and their argument signatures.
2. Identify which probe fires on the path you need.
3. Attach a one-liner that prints the probe arguments.
4. Confirm the probe fires without changing application behaviour.
5. Record the probe name and arguments, which are stable across builds.
6. Fall back to a function hook only if no probe covers the path.

## Signals

- The binary contains a note section describing probes.
- A probe fires at the point where the value is still plaintext.
- The platform requires elevated privileges to attach.
- The probe's arguments are truncated to a fixed width.

## Patterns

**1. List probes**

```text
readelf -n ./target | grep -i provider  -> probe names and args
```

**2. One-liner**

```text
dtrace -n 'app*:::request-start { printf("%s", copyinstr(arg0)); }'
```

**3. Stability note**

```text
probes are a public interface  -> survives optimisation changes
```

## Pitfalls

- Rebuilding the target to add probes and then reporting behaviour of the rebuilt binary.
- Assuming probe arguments are full strings when they are fixed-width chunks.
- Ignoring privilege requirements and concluding the target is uninstrumentable.

## Done when

- A published probe is used, with its name and arguments recorded.
- The probe is shown to fire without a rebuild.

## References

- [DTrace - guide](https://illumos.org/books/dtrace/chp-intro.html)
- [systemtap - probe documentation](https://sourceware.org/systemtap/documentation.html)
