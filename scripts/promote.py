#!/usr/bin/env python3
"""Notify Bing/IndexNow that KNBMF public URLs changed."""
from pathlib import Path
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://kashtnivaranbalajimandirfoundation.org"
KEY = "3c9043b9f3070dcac6834eea517feea8"
HOST = "kashtnivaranbalajimandirfoundation.org"


def urls() -> list[str]:
    from apply_seo import PAGES

    out = []
    for name, meta in PAGES.items():
        if name == "404.html":
            continue
        out.append(meta["url"])
    return out


def ping_indexnow(url_list: list[str], endpoint: str, label: str) -> None:
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{BASE}/{KEY}.txt",
        "urlList": url_list,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            print(label, res.status)
    except urllib.error.HTTPError as e:
        print(label, e.code, e.read()[:300])
    except Exception as e:
        print(label, "error", e)


def ping_bing_sitemap() -> None:
    sitemap = f"{BASE}/sitemap.xml"
    req = urllib.request.Request(
        "https://www.bing.com/ping?sitemap=" + urllib.parse.quote(sitemap, safe=""),
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            print("bing-sitemap", res.status)
    except urllib.error.HTTPError as e:
        print("bing-sitemap", e.code)
    except Exception as e:
        print("bing-sitemap error", e)


def main() -> None:
    url_list = urls()
    print("urls", len(url_list))
    ping_indexnow(url_list, "https://api.indexnow.org/indexnow", "indexnow")
    ping_indexnow(url_list, "https://www.bing.com/indexnow", "bing-indexnow")
    ping_indexnow(url_list, "https://yandex.com/indexnow", "yandex-indexnow")
    ping_bing_sitemap()


if __name__ == "__main__":
    main()
