---
name: artifact-cleanup
description: "Remove the scripts, logs and temporary files the session created, so the next run does not read stale captures as fresh evidence. Use when finishing a session that wrote capture files or agent scripts"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, hygiene]
---

# Artifact Cleanup

> Remove the scripts, logs and temporary files the session created, so the next run does not read stale captures as fresh evidence

**Use when:** finishing a session that wrote capture files or agent scripts

**Avoid when:** the artifacts are the evidence set, which should be archived rather than deleted

## Procedure

1. List every file the session created outside the evidence directory.
2. Distinguish evidence from working files before deleting anything.
3. Archive evidence with its manifest, then delete working files.
4. Remove injected scripts from the target's filesystem.
5. Check that no capture file is left where the next run will append to it.
6. Record what was deleted and what was kept.

## Signals

- A capture file grows across runs because it is appended to.
- An agent script remains on a remote host.
- A temporary file from run one is parsed as input in run two.
- Evidence and scratch files share one directory.

## Patterns

**1. Two directories**

```text
evidence/ kept and hashed; work/ deleted  -> no ambiguity
```

**2. Fresh run**

```text
truncate the capture file at start  -> run two cannot inherit run one
```

**3. Remote cleanup**

```text
remove the uploaded agent from the host after detaching
```

## Pitfalls

- Deleting the only copy of the capture because it was in the working directory.
- Appending to a capture file and reporting cumulative counts.
- Leaving an agent script on a customer host after the engagement.

## Done when

- Working files are removed and evidence is archived with a manifest.
- Each run starts with an empty capture destination.

## References

- [Frida - deploying agents](https://frida.re/docs/modes/)
- [NIST - media sanitization](https://csrc.nist.gov/pubs/sp/800/88/b/final)
