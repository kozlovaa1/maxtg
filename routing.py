from typing import Any


def strip_tg_chat_map_comments(raw_value: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in raw_value.splitlines())


def parse_tg_chat_map(raw_value: str | None) -> tuple[dict[int, str], list[dict[str, Any]]]:
    route_map: dict[int, str] = {}
    warnings: list[dict[str, Any]] = []

    if not raw_value or raw_value.strip() == "":
        return route_map, warnings

    raw_value = strip_tg_chat_map_comments(raw_value)
    if raw_value.strip() == "":
        return route_map, warnings

    for position, raw_entry in enumerate(raw_value.split(","), start=1):
        entry = raw_entry.strip()
        if not entry:
            warnings.append({"position": position, "reason": "empty_entry"})
            continue

        if ":" not in entry:
            warnings.append({"position": position, "reason": "missing_separator"})
            continue

        max_chat_id_raw, tg_chat_id_raw = entry.split(":", 1)
        max_chat_id_raw = max_chat_id_raw.strip()
        tg_chat_id = tg_chat_id_raw.strip()

        if not max_chat_id_raw:
            warnings.append({"position": position, "reason": "missing_max_chat_id"})
            continue

        try:
            max_chat_id = int(max_chat_id_raw)
        except ValueError:
            warnings.append({"position": position, "reason": "invalid_max_chat_id"})
            continue

        if not tg_chat_id:
            warnings.append({"position": position, "reason": "missing_tg_chat_id"})
            continue

        if max_chat_id in route_map:
            warnings.append({"position": position, "reason": "duplicate_max_chat_id"})

        route_map[max_chat_id] = tg_chat_id

    return route_map, warnings


def telegram_target_for(
    max_chat_id: int,
    route_map: dict[int, str],
    fallback_chat_id: str | None,
) -> tuple[str | None, str]:
    if max_chat_id in route_map:
        return route_map[max_chat_id], "mapped"

    if fallback_chat_id and fallback_chat_id.strip():
        return fallback_chat_id.strip(), "fallback_TG_CHAT_ID"

    return None, "missing_target"
