---
name: post-hook-retest
description: "Re-run the whole plan after a fix or a rebuild and compare captures, so the retest proves the change rather than assuming it. Use when the vendor ships a fix, or the target is rebuilt while the engagement continues"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, retest]
---

# Post Hook Retest

> Re-run the whole plan after a fix or a rebuild and compare captures, so the retest proves the change rather than assuming it

**Use when:** the vendor ships a fix, or the target is rebuilt while the engagement continues

**Avoid when:** the target has not changed since the last run

## Procedure

1. Record the build id and capture from the original run.
2. Confirm the target changed: build id, version or binary hash.
3. Re-run the identical plan against the new build.
4. Compare captures field by field and list the differences.
5. Check the ordinary path still works under the hook.
6. Report fixed, partially fixed or unchanged, with both captures.

## Signals

- The build id is unchanged, so the fix never reached the target.
- The value is no longer captured, indicating the code path changed.
- The path still captures the value but the decision changed.
- The ordinary path now fails, a regression from the fix.

## Patterns

**1. Same plan**

```text
run plan.json untouched  -> captures are comparable
```

**2. Three verdicts**

```text
fixed / partially fixed / unchanged  -> with both capture files
```

**3. Regression check**

```text
legitimate input still succeeds after the fix
```

## Pitfalls

- Editing the plan between runs and comparing incomparable captures.
- Assuming a new version number means the code path changed.
- Testing only the malicious path and missing a fix regression.

## Done when

- The new build is identified and the same plan produced a comparable capture.
- The verdict is stated with both captures attached.

## References

- [readelf - build id](https://man7.org/linux/man-pages/man1/readelf.1.html)
- [Frida - Interceptor](https://frida.re/docs/javascript-api/#interceptor)
