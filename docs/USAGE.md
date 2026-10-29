# Usage

## 1. Write the plan

```bash
hooklab scaffold "Capture the plaintext password" --id password-capture --out plan.json
```

Then fill in the four parts that decide whether the plan is any good:

```json
"objective": "Show that the client's password reaches check_password unhashed.",
"hooks": [
  {"target": "check_password", "event": "call", "capture": ["username", "password"],
   "why": "the argument values prove whether the credential arrives hashed or in plaintext"}
],
"exercise": {"function": "login", "args": ["alice", "hunter2"]},
"expect": [{"target": "check_password", "event": "call", "has": ["password"]}]
```

`objective` is the question. `hooks[].why` is why this hook and not another. `exercise` is what makes the hook fire, without which the plan cannot be verified. `expect` is what a correct capture contains.

## 2. Grade before you run

```bash
hooklab check plan.json --verbose
```

Blocking findings are what would make the capture untrustworthy: no exercise, no expectations, a missing module, an intrusive plan with no cleanup. `--verbose` prints the hint, which usually names the missing artifact.

## 3. Run it

```bash
hooklab run plan.json
# returned: {'ok': True, 'user': 'alice'}
# call   check_password  username='alice' password='hunter2'
# return check_password  __return__=True
# 2 capture(s), PASS
```

For machine use:

```bash
hooklab run plan.json --json | jq '.captures'
```

Exit code is 0 only when every expectation is met. A hook that never fired shows as `FAIL ... no capture recorded` rather than an empty success.

## 4. Emit a native hook

```bash
hooklab emit plan.json --format frida   --out agent.js
hooklab emit plan.json --format gdb     --out hooklab-gdb.py
hooklab emit plan.json --format preload --out hooklab-preload.c
```

- **Frida**: `frida -p <pid> -l agent.js`. Resolves by symbol with a failure branch that logs instead of throwing.
- **GDB**: `gdb -q -x hooklab-gdb.py --args ./target`. The breakpoint returns `False`, so it logs and continues rather than stopping the target.
- **LD_PRELOAD**: `cc -shared -fPIC -o hook.so hooklab-preload.c -ldl`. Only for the prototypes the emitter knows.

An unknown symbol is refused with an explanation. That is the safe outcome: a guessed C prototype is worse than no hook.

## 5. Report

```bash
hooklab report plan.json --out plan-report.md
```

Sections: objective, hooks table (target, event, captures, why), verification expectations, cleanup, reproduction, plan grade.

## Grading model

| Finding | Effect |
|---|---|
| blocking | grade capped at D |
| major | −10 |
| minor | −3 |

A: ≥ 90, B: ≥ 75, C: ≥ 55, otherwise D.

## Reading the skills

```bash
hooklab list --phase hook
hooklab show interceptor-attach
hooklab search "got" "patch"
```

Each `SKILL.md` carries front matter, use/avoid conditions, a six-step procedure, signals, patterns, pitfalls, done-when criteria and references. `pack.json` records a SHA-256 per file.

A session, in order:

```bash
hooklab show dependency-map-first       # resolve
hooklab show read-only-hook-discipline  # instrument
hooklab show python-trace-hooks         # hook
hooklab show string-safety-bounds       # capture
hooklab show hook-fired-proof           # verify
hooklab show detach-and-restore         # teardown
```
