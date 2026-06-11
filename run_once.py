from pathlib import Path

from screenscraper import ScreenScraper
from scraper_service import fetch_media_for_rom, get_system_id



if __name__ == "__main__":
    ss = ScreenScraper()

    psp_id = get_system_id(ss, ["PSP", "PlayStation Portable"])
    if psp_id is None:
        raise RuntimeError("PSP system ID not found")

    print("PSP system ID =", psp_id)