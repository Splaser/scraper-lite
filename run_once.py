from pathlib import Path

from screenscraper import ScreenScraper, ScreenScraperError
from scraper_service import fetch_media_for_rom, get_system_id


SYSTEM_KEYWORDS = ["GBA", "Gameboy Advance"]

ROM_FILE = "Tetris Worlds (USA).zip"
SEARCH_TERM = "Tetris Worlds"

MEDIA_ROOT = Path("media")


if __name__ == "__main__":
    try:
        ss = ScreenScraper()

        system_id = get_system_id(ss, SYSTEM_KEYWORDS)

        if system_id is None:
            raise RuntimeError(f"system not found: {SYSTEM_KEYWORDS}")

        print("[SYSTEM]", SYSTEM_KEYWORDS, "=>", system_id)

        fetch_media_for_rom(
            ss,
            rom_file=ROM_FILE,
            search_term=SEARCH_TERM,
            system_id=system_id,
            media_root=MEDIA_ROOT,
            skip_existing=False,
        )
    except ScreenScraperError as exc:
        raise SystemExit(f"[ERROR] {exc}") from None
