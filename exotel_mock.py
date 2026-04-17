from typing import Optional

NUMBER_POOL = [
    "+911140000001",
    "+911140000002",
    "+911140000003",
    "+911140000004",
    "+911140000005",
]

_available: list[str] = list(NUMBER_POOL)
_leased: dict[str, str] = {}  # proxy_number -> case_id


def lease_number(case_id: str) -> Optional[str]:
    if not _available:
        return None
    number = _available.pop(0)
    _leased[number] = case_id
    return number


def release_number(proxy_number: str) -> bool:
    if proxy_number in _leased:
        del _leased[proxy_number]
        _available.append(proxy_number)
        return True
    return False


def available_count() -> int:
    return len(_available)


def leased_numbers() -> dict[str, str]:
    return dict(_leased)
