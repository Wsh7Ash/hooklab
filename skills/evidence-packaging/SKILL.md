---
name: evidence-packaging
description: "Package the plan, the capture, the parity check and the detach record together, because a capture without its installation record is unverifiable. Use when handing instrumentation results to a triager, a teammate or a report"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, evidence]
---

# Evidence Packaging

> Package the plan, the capture, the parity check and the detach record together, because a capture without its installation record is unverifiable

**Use when:** handing instrumentation results to a triager, a teammate or a report

**Avoid when:** the capture is an informal note to yourself

## Procedure

1. Collect the plan, the capture file, the parity check and the detach record.
2. Hash the set into a manifest.
3. Label each file with the claim it supports.
4. Include the target's build id and the hook mechanism used.
5. Reference files by path inside the writeup.
6. Re-verify the manifest before sending.

## Signals

- The capture is attached without the plan that produced it.
- No build id, so the target version is unknown.
- The parity check is missing, so read-only status is unproven.
- The manifest lists a file that was not attached.

## Patterns

**1. Five files**

```text
plan.json, capture.txt, parity.diff, detach.log, manifest.json  -> one set
```

**2. Build id**

```text
recorded per file  -> captures cannot be mixed across builds
```

**3. Claim mapping**

```text
capture.txt supports 'plaintext reaches check_password'
```

## Pitfalls

- Sending a capture with no record of how it was installed.
- Mixing captures from two builds in one evidence set.
- Attaching a manifest that no longer matches the files.

## Done when

- The set includes the plan, capture, parity check and detach record.
- The manifest verifies against the attached files.

## References

- [RFC 6234 - secure hash algorithms](https://www.rfc-editor.org/rfc/rfc6234)
- [OWASP MASTG - evidence collection](https://mas.owasp.org/MASTG/)
