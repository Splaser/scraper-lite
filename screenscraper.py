import requests

from config import *


class ScreenScraper:
    def __init__(self):
        self.session = requests.Session()

    def _params(self):
        return {
            "devid": SS_DEV_ID,
            "devpassword": SS_DEV_PASSWORD,
            "ssid": SS_USER,
            "sspassword": SS_PASSWORD,
            "softname": SOFTNAME,
            "output": "json",
        }

    def systems(self):
        url = f"{BASE_URL}/systemesListe.php"

        r = self.session.get(
            url,
            params=self._params(),
            timeout=30,
        )

        r.raise_for_status()
        return r.json()

    def search(self, term, system_id=None):
        params = self._params()
        params["recherche"] = term

        if system_id:
            params["systemeid"] = system_id

        url = f"{BASE_URL}/jeuRecherche.php"

        r = self.session.get(
            url,
            params=params,
            timeout=30,
        )

        r.raise_for_status()
        return r.json()

    def game_info(self, game_id, system_id=None):
        params = self._params()

        params["gameid"] = game_id

        if system_id:
            params["systemeid"] = system_id

        url = f"{BASE_URL}/jeuInfos.php"

        r = self.session.get(
            url,
            params=params,
            timeout=30,
        )

        r.raise_for_status()
        return r.json()