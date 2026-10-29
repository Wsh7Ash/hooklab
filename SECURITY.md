# Security and scope

## What this tool does

`hooklab run` executes one function from a Python module you name, with JSON arguments from the plan, inside the hooklab process. `hooklab emit` writes a script to disk. Neither attaches to another process or contacts a host.

## Authorized targets only

Every skill assumes a target you are permitted to instrument. The grader enforces the reporting side: a plan without a `scope_ref` cannot reach grade A.

Instrumenting a third-party application you do not own or have written permission to test is not made acceptable by a plan format.

## Read-only by default

A plan declares `risk` as `read-only` or `intrusive`. Read-only means the hook observes and returns; it must not patch a branch, change an argument or replace a return value. Intrusive plans need a `cleanup` section, and the grader blocks them without one.

The C emitter never changes results: it logs, then calls the real function through `dlsym(RTLD_NEXT, ...)`.

## Captured data

A hook on an authentication path captures credentials by design. Before anything leaves the machine:

- Redact values, keep field names and length class (`capture-redaction`).
- Check repository history, not just the working tree.
- Never commit a capture that contains a live token or another person's data.

## Teardown

The tracer restores the previous profiler on exit, including when the target raises. Plans that patch memory must record the original bytes and verify the restore by hash (`patch-restoration`).

## Reporting a problem in this tool

Open an issue with the plan and the observed capture. A tracer that changes target behaviour, or an emitter that generates a wrong C prototype, is a security-relevant bug here.
