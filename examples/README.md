# Examples

A self-contained hooking demo. `target_app.py` is a toy login module; the plan observes the password reaching `check_password`.

| Path | What it is |
|---|---|
| `target_app.py` | The target: `login` calls `check_password(username, password)`, which compares against a known plaintext |
| `plan/password-capture.json` | The plan: two Python hooks, one exercise call, two expectations, one native hook, cleanup, grade 100 |
| `emitted/hooklab-agent.js` | Frida agent generated from the plan's native hook |
| `emitted/hooklab-gdb.py` | GDB Python script, logs and continues |
| `emitted/hooklab-preload.c` | LD_PRELOAD interposer for `strcmp` |

## Run it

```bash
hooklab check examples/plan/password-capture.json
# password-plaintext-capture: grade A (100/100) submittable

hooklab run examples/plan/password-capture.json
# returned: {'ok': True, 'user': 'alice'}
# call   check_password  username='alice' password='hunter2'
# return check_password  __return__=True
# 2 capture(s), PASS
```

## Break it on purpose

Point the hook at a function that never runs:

```bash
python - <<'PY'
import json
plan = json.load(open("examples/plan/password-capture.json"))
plan["hooks"][0]["target"] = "hash_password"
plan["expect"] = [{"target": "hash_password", "event": "call", "has": ["value"]}]
json.dump(plan, open("results/wrong-hook.json", "w"), indent=2)
PY
hooklab run results/wrong-hook.json
# FAIL hash_password/call: no capture recorded  -> exit 1
```

That failure mode is the point of the tool: the run did not silently succeed with an empty capture.

Drop the exercise and the grader blocks it:

```bash
python - <<'PY'
import json
plan = json.load(open("examples/plan/password-capture.json"))
plan["exercise"] = {}
json.dump(plan, open("results/no-exercise.json", "w"), indent=2)
PY
hooklab check results/no-exercise.json
# blocking exercise: no exercise call, so nothing proves the hook fires
```

## Regenerating the emitted scripts

```bash
hooklab emit examples/plan/password-capture.json --format frida   --out examples/emitted/hooklab-agent.js
hooklab emit examples/plan/password-capture.json --format gdb     --out examples/emitted/hooklab-gdb.py
hooklab emit examples/plan/password-capture.json --format preload --out examples/emitted/hooklab-preload.c
```

The C file was not compiled in this environment (no `dlfcn.h` in the local toolchain); build it on a glibc host with `cc -shared -fPIC -o hook.so hooklab-preload.c -ldl`.
