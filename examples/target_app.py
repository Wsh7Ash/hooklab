"""A small target used by the example hook plan.

The password reaches ``check_password`` in plaintext and the comparison happens
in Python, which is exactly the shape a hook plan is meant to observe.
"""

from __future__ import annotations

import hashlib

USERS = {"alice": "hunter2", "bob": "correct-horse-battery"}


def hash_password(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def check_password(username: str, password: str) -> bool:
    expected = USERS.get(username)
    if expected is None:
        return False
    return expected == password


def login(username: str, password: str) -> dict:
    ok = check_password(username, password)
    return {"ok": ok, "user": username if ok else None}
