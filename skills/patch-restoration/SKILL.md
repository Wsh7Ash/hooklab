---
name: patch-restoration
description: "Keep the original bytes of every patch and write them back, because a half-restored trampoline leaves the process subtly broken. Use when the hook overwrote code bytes rather than redirecting a pointer"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, patches]
---

# Patch Restoration

> Keep the original bytes of every patch and write them back, because a half-restored trampoline leaves the process subtly broken

**Use when:** the hook overwrote code bytes rather than redirecting a pointer

**Avoid when:** the hook only attached a listener and never wrote to memory

## Procedure

1. Capture the original bytes before writing any patch.
2. Record the address, length and hash of the original region.
3. Restore the bytes in the reverse order of patching.
4. Verify the restored bytes hash to the original value.
5. Check that the function executes normally after restoration.
6. Keep the byte capture with the session record.

## Signals

- The restored region hash differs from the recorded original.
- The function still jumps to the hook after restoration.
- A second patch overlapped the first and the restore order matters.
- Restoring crashes because the page protection was not reset.

## Patterns

**1. Save the bytes**

```text
original = ptr.readByteArray(len)  -> store with its hash
```

**2. Restore in reverse**

```text
undo patch B, then patch A  -> overlapping regions handled
```

**3. Verify by hash**

```text
sha256(restored) == sha256(original)  -> proven, not assumed
```

## Pitfalls

- Restoring patches in installation order when two overlapped.
- Writing bytes back without restoring page protection first.
- Assuming a restore worked because the call did not throw.

## Done when

- Every patched region is restored and verified by hash.
- The function behaves normally after restoration.

## References

- [Frida - Memory.protect](https://frida.re/docs/javascript-api/#memory)
- [Linux man-pages - mprotect](https://man7.org/linux/man-pages/man2/mprotect.2.html)
