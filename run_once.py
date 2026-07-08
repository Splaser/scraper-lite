from pathlib import Path

from screenscraper import ScreenScraper
from scraper_service import fetch_media_for_rom, get_system_id


SYSTEM_KEYWORDS = ["DC", "Dreamcast"]

ROM_FILE = "Sakura Taisen 3/Sakura Taisen 3 - Paris wa Moeteiru ka (CHSV3) (Disc 1).chd"
SEARCH_TERM = "Sakura Taisen 3"

MEDIA_ROOT = Path("media")


if __name__ == "__main__":
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
        skip_existing=True,
    )