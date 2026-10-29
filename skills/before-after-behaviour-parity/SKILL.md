---
name: before-after-behaviour-parity
description: "Run the same input with and without the hook and compare outputs, because a read-only hook that changes behaviour is not read-only. Use when the plan claims to observe without modifying the target"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, verify, parity]
---

# Before After Behaviour Parity

> Run the same input with and without the hook and compare outputs, because a read-only hook that changes behaviour is not read-only

**Use when:** the plan claims to observe without modifying the target

**Avoid when:** the plan is explicitly intrusive and behaviour change is the point

## Procedure

1. Record the target's output for a fixed input without instrumentation.
2. Install the hook and repeat the identical input.
3. Compare outputs byte for byte, including exit code and timing class.
4. Compare a second input to catch a branch-specific difference.
5. If outputs differ, the hook is perturbing behaviour; fix it before trusting the capture.
6. Record both outputs in the evidence.

## Signals

- The exit code changes when the hook is attached.
- Output differs only in timing-sensitive fields.
- A race that disappears under the hook, which changes the observed outcome.
- The hook's exception handler swallows a real error.

## Patterns

**1. Byte compare**

```text
diff run-unhooked.txt run-hooked.txt  -> must be empty
```

**2. Exit code**

```text
both 0, or both 1  -> behaviour preserved
```

**3. Timing caveat**

```text
output identical but runtime +40%  -> state it
```

## Pitfalls

- Comparing outputs that were generated with different inputs.
- Accepting a different exit code as a harmless instrumentation artefact.
- Ignoring that timing changes can eliminate the race you were studying.

## Done when

- Hooked and unhooked outputs are identical for at least two inputs.
- Any timing or branch perturbation is stated.

## References

- [Frida - performance considerations](https://frida.re/docs/performance/)
- [OWASP MASTG - instrumentation effects](https://mas.owasp.org/MASTG/)
