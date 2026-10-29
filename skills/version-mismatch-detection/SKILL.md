---
name: version-mismatch-detection
description: "Confirm the hooked build is the build under review, because a hook on a patched or vendored version produces a capture that does not apply to the target. Use when the target ships its own copy of a dependency, or the report cites a version number from a package manifest"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, resolve, versions]
---

# Version Mismatch Detection

> Confirm the hooked build is the build under review, because a hook on a patched or vendored version produces a capture that does not apply to the target

**Use when:** the target ships its own copy of a dependency, or the report cites a version number from a package manifest

**Avoid when:** the hook targets the target's own code and the binary hash is already recorded

## Procedure

1. Record the binary's build id or hash before attaching.
2. Read the library version string the process actually has loaded.
3. Compare the loaded version with the one in the report and the manifest.
4. Check whether the binary bundles a vendored copy of the same library.
5. If versions differ, re-run against the reviewed build or restate the finding.
6. Store the build id with the capture so future runs can be compared.

## Signals

- The loaded library is newer than the version the report mentions.
- A vendored copy is loaded before the system library.
- The build id differs between two machines in the same test.
- The function's behaviour changed between the two versions you can see.

## Patterns

**1. Build id first**

```text
readelf -n ./target | grep 'Build ID'  -> pin the exact binary
```

**2. Loaded version**

```text
the process reports libfoo 2.31 while the report tested 2.28
```

**3. Vendored check**

```text
ldd ./target | grep foo  -> shows which copy is actually loaded
```

## Pitfalls

- Quoting a version from a package manifest while the process loaded a different one.
- Ignoring a vendored library because the system copy has the expected version.
- Re-running on an updated build and concluding the bug is gone.

## Done when

- The build id and loaded library version are recorded with the capture.
- Any mismatch between reviewed and tested builds is stated.

## References

- [readelf - note sections and build id](https://man7.org/linux/man-pages/man1/readelf.1.html)
- [Frida - Process.enumerateModules](https://frida.re/docs/javascript-api/#process)
