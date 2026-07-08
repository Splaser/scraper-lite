from pathlib import Path

from screenscraper import ScreenScraper
from media_picker import pick_target_medias
from downloader import download_picked_medias


def media_folder_from_file(file_name: str) -> str:
    p = Path(file_name)

    # 优先使用 ROM 所在目录作为媒体目录
    if p.parent != Path("."):
        return p.parent.name

    # 没有目录时 fallback 使用文件名去扩展名
    if p.suffix:
        return p.stem

    return file_name


def get_names(game: dict) -> list[str]:
    names = []

    for item in game.get("noms", []):
        text = item.get("text")
        if text and text not in names:
            names.append(text)

    return names


def get_display_name(game: dict) -> str:
    priority = ["jp", "us", "wor", "ss", "eu"]

    names = game.get("noms", [])

    for region in priority:
        for item in names:
            if item.get("region") == region and item.get("text"):
                return item["text"]

    if names and names[0].get("text"):
        return names[0]["text"]

    return str(game.get("id") or "unknown")


def print_search_results(games: list[dict], limit: int = 10) -> None:
    print()
    print("[SEARCH RESULTS]")

    for i, game in enumerate(games[:limit], 1):
        game_id = game.get("id")
        system = game.get("systeme", {})
        system_id = system.get("id")
        system_name = system.get("text")

        print(
            f"{i:02d}. "
            f"id={game_id} "
            f"system={system_name}({system_id}) "
            f"name={get_display_name(game)}"
        )


def search_games(
    ss: ScreenScraper,
    term: str,
    *,
    system_id: int | None = None,
) -> list[dict]:
    data = ss.search(term, system_id=system_id)
    games = data.get("response", {}).get("jeux", [])

    if len(games) == 1 and not games[0]:
        return []

    return games


def select_game_by_exact_name(games, target_name: str, system_id=None):
    target_lower = target_name.lower()

    for game in games:
        # 系统过滤
        system = game.get("systeme", {})
        if system_id is not None and str(system.get("id")) != str(system_id):
            continue

        # 名字匹配
        names = [n.get("text", "").lower() for n in game.get("noms", [])]
        if any(target_lower in n for n in names):
            return game

    # fallback: 返回第一个匹配系统的
    for game in games:
        system = game.get("systeme", {})
        if system_id is not None and str(system.get("id")) != str(system_id):
            continue
        return game

    return None


def select_first_game(
    games: list[dict],
    *,
    system_id: int | None = None,
) -> dict | None:
    if not games:
        return None

    if system_id is None:
        return games[0]

    for game in games:
        system = game.get("systeme", {})
        if str(system.get("id")) == str(system_id):
            return game

    return None


def get_game_info(
    ss: ScreenScraper,
    *,
    game_id: int | str,
    system_id: int | str | None = None,
) -> dict:
    data = ss.game_info(
        game_id=int(game_id),
        system_id=int(system_id) if system_id is not None else None,
    )

    return data.get("response", {}).get("jeu", {})


def fetch_media_by_game_id(
    ss: ScreenScraper,
    *,
    game_id: int | str,
    system_id: int | str,
    out_dir: Path,
    skip_existing: bool = True,
) -> dict[str, bool]:
    game = get_game_info(
        ss,
        game_id=game_id,
        system_id=system_id,
    )

    if not game:
        print("[FAIL] game info not found")
        return {}

    print()
    print("[GAME]", get_display_name(game))
    print("[ID  ]", game.get("id"))

    picked = pick_target_medias(game)

    print()
    print("[PICKED MEDIA]")

    for output_name, media in picked.items():
        print(
            output_name,
            "->",
            media.get("type"),
            f"({media.get('region')})",
            media.get("format"),
        )

    return download_picked_medias(
        picked,
        out_dir,
        skip_existing=skip_existing,
        prefer_aria2=True,
    )


def fetch_media_by_search(
    ss: ScreenScraper,
    *,
    term: str,
    system_id: int,
    out_dir: Path,
    skip_existing: bool = True,
) -> dict[str, bool]:
    games = search_games(
        ss,
        term,
        system_id=system_id,
    )

    print_search_results(games)

    game = select_game_by_exact_name(games, term, system_id=system_id)

    if not game:
        print("[FAIL] no game selected")
        return {}

    game_id = game.get("id")

    print()
    print("[SELECTED]", game_id, get_display_name(game))

    return fetch_media_by_game_id(
        ss,
        game_id=game_id,
        system_id=system_id,
        out_dir=out_dir,
        skip_existing=skip_existing,
    )


def fetch_media_for_rom(
    ss: ScreenScraper,
    *,
    rom_file: str,
    search_term: str,
    system_id: int,
    media_root: Path = Path("media"),
    skip_existing: bool = True,
) -> dict[str, bool]:
    folder_name = media_folder_from_file(rom_file)
    out_dir = media_root / folder_name

    print()
    print("[ROM ]", rom_file)
    print("[DIR ]", out_dir)

    return fetch_media_by_search(
        ss,
        term=search_term,
        system_id=system_id,
        out_dir=out_dir,
        skip_existing=skip_existing,
    )


def get_system_id(ss: ScreenScraper, name_keywords: list[str]) -> int | None:
    """
    根据关键词搜索系统名称，返回第一个匹配 system_id
    name_keywords: ['PSP', 'PlayStation Portable'] 等
    """
    systems_data = ss.systems()
    systems = systems_data.get("response", {}).get("systemes", [])

    for system in systems:
        noms = system.get("noms", {})
        system_names = list(noms.values())  # 包含 nom_us, nom_jp, nom_eu 等

        for kw in name_keywords:
            if any(kw.lower() in str(n).lower() for n in system_names):
                return system.get("id")

    return None