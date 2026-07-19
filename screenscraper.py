from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import *


class ScreenScraperError(RuntimeError):
    """ScreenScraper API 请求失败。"""


class ScreenScraperAuthenticationError(ScreenScraperError):
    """ScreenScraper 用户或开发者凭据无效。"""


class ScreenScraper:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _params(self):
        return {
            "devid": SS_DEV_ID,
            "devpassword": SS_DEV_PASSWORD,
            "ssid": SS_USER,
            "sspassword": SS_PASSWORD,
            "softname": SOFTNAME,
            "output": "json",
        }

    def _get_json(self, endpoint: str, **params: Any) -> dict[str, Any]:
        request_params = self._params()
        request_params.update(params)
        url = f"{BASE_URL}/{endpoint}"

        try:
            response = self.session.get(
                url,
                params=request_params,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            status = (
                f"，HTTP {exc.response.status_code}"
                if exc.response is not None
                else ""
            )
            raise ScreenScraperError(
                f"ScreenScraper 请求失败（{endpoint}{status}，"
                f"{type(exc).__name__}）。"
            ) from exc

        body = response.text.strip()
        if not body:
            raise ScreenScraperError(
                f"ScreenScraper 返回空响应（{endpoint}，HTTP {response.status_code}）。"
            )

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            preview = " ".join(body.split())[:300]
            lower_body = body.casefold()
            if "identifiants developpeur" in lower_body:
                raise ScreenScraperAuthenticationError(
                    "ScreenScraper 开发者凭据无效；请检查 config.json 中的 "
                    "SS_DEV_ID 和 SS_DEV_PASSWORD。"
                ) from exc
            if "erreur de login" in lower_body:
                raise ScreenScraperAuthenticationError(
                    "ScreenScraper 登录凭据无效；请检查 config.json 中的 "
                    "SS_USER、SS_PASSWORD、SS_DEV_ID 和 SS_DEV_PASSWORD。"
                ) from exc

            raise ScreenScraperError(
                f"ScreenScraper 返回了非 JSON 响应（{endpoint}，"
                f"HTTP {response.status_code}）：{preview}"
            ) from exc

        if not isinstance(data, dict):
            raise ScreenScraperError(
                f"ScreenScraper 返回了意外的 JSON 类型（{endpoint}）："
                f"{type(data).__name__}"
            )

        return data

    def systems(self):
        return self._get_json("systemesListe.php")

    def search(self, term, system_id=None):
        params = {"recherche": term}

        if system_id:
            params["systemeid"] = system_id

        return self._get_json("jeuRecherche.php", **params)

    def game_info(self, game_id, system_id=None):
        params = {"gameid": game_id}

        if system_id:
            params["systemeid"] = system_id

        return self._get_json("jeuInfos.php", **params)
