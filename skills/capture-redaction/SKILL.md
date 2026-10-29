---
name: capture-redaction
description: "Redact secrets in captured values before they leave the machine, because a hook on an auth function captures credentials by design. Use when the capture contains passwords, tokens, keys or another person's data"
pack: hooklab
version: 1.0.0
category: dynamic-instrumentation
tags: [hooking, teardown, privacy]
---

# Capture Redaction

> Redact secrets in captured values before they leave the machine, because a hook on an auth function captures credentials by design

**Use when:** the capture contains passwords, tokens, keys or another person's data

**Avoid when:** the capture is entirely synthetic test data

## Procedure

1. Classify every captured field as secret, personal or safe.
2. Replace secret values with a stable marker that keeps the field visible.
3. Keep the length class where length is part of the finding.
4. Verify the redacted capture still demonstrates the claim.
5. Check the raw capture never reached the repository or a paste site.
6. Record the redaction rule applied to each field.

## Signals

- A captured password appears in plaintext in the report.
- A token in the capture is still valid.
- Redaction removed the field that proves the claim.
- A screenshot of the capture shows unredacted values.

## Patterns

**1. Stable marker**

```text
password=<redacted:7 chars>  -> shape preserved, value gone
```

**2. Keep the proof**

```text
the field is visible and the value is not  -> claim intact
```

**3. History check**

```text
grep the repository history for the captured value  -> remove before publish
```

## Pitfalls

- Publishing a capture that contains a live bearer token.
- Redacting the field name instead of the value and losing the finding.
- Removing the value from the latest commit while it stays in history.

## Done when

- No secret or personal value appears in shipped artifacts.
- The redacted capture still demonstrates the claim.

## References

- [OWASP - sensitive data exposure](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure)
- [CWE-312 - cleartext storage of sensitive information](https://cwe.mitre.org/data/definitions/312.html)
