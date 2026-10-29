---
name: disclosure-of-instrumentation
description: "State in the report that a hook was used and what it changed, because a finding that depends on instrumentation must say so. Use when the evidence comes from a running process you instrumented"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, reporting]
---

# Disclosure of Instrumentation

> State in the report that a hook was used and what it changed, because a finding that depends on instrumentation must say so

**Use when:** the evidence comes from a running process you instrumented

**Avoid when:** the finding is purely from static reading with no runtime observation

## Procedure

1. List each hook and whether it was read-only or intrusive.
2. State the tool and mechanism used, with versions.
3. Describe what behaviour, if any, the hook changed.
4. Explain how the claim would hold without the hook.
5. Disclose the instrumentation in the report body, not a footnote.
6. Note any residual change left in the target.

## Signals

- The report presents a hooked capture as if it were native behaviour.
- An intrusive patch is described as observation.
- The tool version is missing, so the capture cannot be reproduced.
- The finding depends entirely on a value only the hook could see.

## Patterns

**1. Mechanism line**

```text
observed via a read-only Frida interceptor on check_password (Frida 16.x)
```

**2. No-change claim**

```text
parity check shows identical output with and without the hook
```

**3. Instrumentation-free corollary**

```text
the same plaintext appears in the client's crash log
```

## Pitfalls

- Omitting that a hook produced the value and implying the target logged it.
- Describing an intrusive patch as passive observation.
- Leaving out versions so nobody can reproduce the capture.

## Done when

- The report names the mechanism, tool version and read-only status.
- Any behaviour change or residual state is disclosed.

## References

- [OWASP MASTG - reporting](https://mas.owasp.org/MASTG/)
- [HackerOne - report quality](https://docs.hackerone.com/en/articles/8475114-scope)
