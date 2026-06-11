TARGETS = {
    # ES-DE / Daijisho 常用命名
    "boxfront.png": ["box-2D", "box-3D", "box-scan", "box-texture"],

    # wheel 才是真 logo，sstitle 只能当兜底
    "logo.png": ["wheel", "wheel-carbon", "wheel-steel", "sstitle"],

    # 普通截图优先，标题画面兜底，screenmarquee 比较偏混合图
    "screenshot.png": ["ss", "sstitle", "screenmarquee"],

    # 预览视频优先 normalized，体积小
    "video.mp4": ["video-normalized", "video"],
}

REGION_PRIORITY = ["jp", "wor", "us", "eu", "ss", "kr", None]


def pick_best_media(game: dict, wanted_types: list[str]) -> dict | None:
    medias = [
        m for m in game.get("medias", [])
        if m.get("parent") == "jeu"
        and m.get("type") in wanted_types
        and m.get("url")
    ]

    if not medias:
        return None

    def score(m: dict) -> tuple[int, int, int]:
        media_type = m.get("type", "")
        region = m.get("region")

        try:
            type_score = len(wanted_types) - wanted_types.index(media_type)
        except ValueError:
            type_score = 0

        try:
            region_score = len(REGION_PRIORITY) - REGION_PRIORITY.index(region)
        except ValueError:
            region_score = 0

        try:
            size_score = int(m.get("size") or 0)
        except ValueError:
            size_score = 0

        return type_score, region_score, size_score

    return sorted(medias, key=score, reverse=True)[0]


def pick_target_medias(game: dict) -> dict[str, dict]:
    picked = {}

    for output_name, wanted_types in TARGETS.items():
        media = pick_best_media(game, wanted_types)
        if media:
            picked[output_name] = media

    return picked