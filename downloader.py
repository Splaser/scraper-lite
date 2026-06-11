from pathlib import Path
import shutil
import subprocess

import requests


def has_aria2c() -> bool:
    return shutil.which("aria2c") is not None


def download_file_requests(
    url: str,
    out_file: Path,
    *,
    timeout: int = 120,
    skip_existing: bool = True,
) -> bool:
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if skip_existing and out_file.exists() and out_file.stat().st_size > 0:
        print("[SKIP]", out_file)
        return True

    print("[GET ]", out_file.name, "(requests)")

    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as e:
        print("[ERR ]", out_file.name, e)
        return False

    if not r.content:
        print("[ERR ]", out_file.name, "empty response")
        return False

    out_file.write_bytes(r.content)
    print("[OK  ]", out_file, f"({len(r.content)} bytes)")
    return True


def download_file_aria2(
    url: str,
    out_file: Path,
    *,
    skip_existing: bool = True,
) -> bool:
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if skip_existing and out_file.exists() and out_file.stat().st_size > 0:
        print("[SKIP]", out_file)
        return True

    if not has_aria2c():
        print("[MISS] aria2c not found")
        return False

    print("[GET ]", out_file.name, "(aria2c)")

    cmd = [
        "aria2c",
        "--allow-overwrite=true",
        "--auto-file-renaming=false",
        "--continue=true",
        "--max-connection-per-server=4",
        "--split=4",
        "--min-split-size=1M",
        "--retry-wait=2",
        "--max-tries=3",
        "--summary-interval=0",
        "--console-log-level=warn",
        "--download-result=hide",
        "--dir",
        str(out_file.parent),
        "--out",
        out_file.name,
        url,
    ]

    try:
        p = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except OSError as e:
        print("[ERR ]", out_file.name, e)
        return False

    if p.returncode != 0:
        print("[ERR ]", out_file.name, "aria2c failed")
        if p.stdout:
            print(p.stdout.strip())
        return False

    if not out_file.exists() or out_file.stat().st_size <= 0:
        print("[ERR ]", out_file.name, "not created or empty")
        return False

    print("[OK  ]", out_file, f"({out_file.stat().st_size} bytes)")
    return True


def download_file(
    url: str,
    out_file: Path,
    *,
    skip_existing: bool = True,
    prefer_aria2: bool = True,
) -> bool:
    if prefer_aria2:
        ok = download_file_aria2(
            url,
            out_file,
            skip_existing=skip_existing,
        )

        if ok:
            return True

        print("[FALLBACK]", out_file.name, "aria2c -> requests")

    return download_file_requests(
        url,
        out_file,
        skip_existing=skip_existing,
    )


def download_picked_medias(
    picked: dict[str, dict],
    out_dir: Path,
    *,
    skip_existing: bool = True,
    prefer_aria2: bool = True,
) -> dict[str, bool]:
    results: dict[str, bool] = {}

    for output_name, media in picked.items():
        url = media.get("url")

        if not url:
            print("[MISS]", output_name, "no url")
            results[output_name] = False
            continue

        out_file = out_dir / output_name

        ok = download_file(
            url,
            out_file,
            skip_existing=skip_existing,
            prefer_aria2=prefer_aria2,
        )

        results[output_name] = ok

        if ok:
            print(
                "[DONE]",
                output_name,
                "<-",
                media.get("type"),
                f"({media.get('region')})",
                media.get("format"),
            )

    return results