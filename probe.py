import json
from pathlib import Path

from config import SS_PASSWORD, SS_DEV_PASSWORD
from screenscraper import ScreenScraper
from media_picker import TARGETS, pick_best_media, pick_target_medias


CACHE = Path("cache")
CACHE.mkdir(exist_ok=True)


def sanitize(obj):
    text = json.dumps(obj, ensure_ascii=False)

    for secret in [
        SS_PASSWORD,
        SS_DEV_PASSWORD,
    ]:
        if secret:
            text = text.replace(secret, "***")

    return json.loads(text)


def dump_json(name: str, data: dict) -> None:
    data = sanitize(data)

    out = CACHE / name
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[SAVED]", out)


def dump_systems(ss: ScreenScraper) -> dict:
    data = ss.systems()
    dump_json("systems.json", data)
    return data


def dump_search(ss: ScreenScraper, term: str, system_id: int | None = None) -> dict:
    data = ss.search(term, system_id=system_id)
    dump_json("search.json", data)

    games = data.get("response", {}).get("jeux", [])

    print()
    print("[SEARCH RESULTS]")

    for i, game in enumerate(games[:10], 1):
        game_id = game.get("id")
        systeme = game.get("systeme", {})
        system_name = systeme.get("text", "")

        names = game.get("noms", [])
        display_name = names[0].get("text", "") if names else ""

        print(f"{i:02d}. id={game_id} system={system_name} name={display_name}")

    return data


def dump_gameinfo(
    ss: ScreenScraper,
    game_id: int,
    system_id: int | None = None,
) -> dict:
    data = ss.game_info(game_id=game_id, system_id=system_id)
    dump_json("gameinfo.json", data)

    game = data.get("response", {}).get("jeu", {})

    print()
    print("[GAME INFO]")
    print("id:", game.get("id"))

    print()
    print("[NAMES]")
    for name in game.get("noms", []):
        print(name.get("region"), "=", name.get("text"))

    print()
    print("[SYNOPSIS LANGS]")
    for item in game.get("synopsis", []):
        print(item.get("langue"))

    print()
    print("[MEDIAS]")
    for media in game.get("medias", []):
        print(
            "type=", media.get("type"),
            "parent=", media.get("parent"),
            "region=", media.get("region"),
            "format=", media.get("format"),
            "size=", media.get("size"),
        )

    return game


def print_picked_medias(game: dict) -> None:
    print()
    print("[PICKED MEDIA]")

    for output_name, wanted_types in TARGETS.items():
        media = pick_best_media(game, wanted_types)

        if not media:
            print(f"{output_name} -> MISS")
            continue

        print(
            f"{output_name} -> "
            f"{media.get('type')} "
            f"({media.get('region')}) "
            f"{media.get('url')}"
        )


if __name__ == "__main__":
    ss = ScreenScraper()

    # dump_systems(ss)
    # dump_search(ss, "Radiant Mythology 2", system_id=61)

    game = dump_gameinfo(ss, game_id=28321, system_id=61)
    print_picked_medias(game)