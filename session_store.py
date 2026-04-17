import json
import os

SESSION_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")


def _normalize(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    return digits[-10:] if len(digits) >= 10 else digits


def _load() -> dict:
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE) as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_session(proxy: str, data: dict) -> None:
    sessions = _load()
    sessions[_normalize(proxy)] = data
    _save(sessions)


def get_session(proxy: str) -> dict | None:
    return _load().get(_normalize(proxy))


def delete_session(proxy: str) -> None:
    sessions = _load()
    sessions.pop(_normalize(proxy), None)
    _save(sessions)


def get_all() -> dict:
    return _load()
