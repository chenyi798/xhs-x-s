import json
import re
import subprocess
import time
from pathlib import Path

import requests


COOKIE = (
    "a1=; " 
    "web_session=; "
)



PAYLOAD = {
    "cursor_score": "",
    "num": 18,
    "refresh_type": 1,
    "note_index": 10,
    "unread_begin_note_id": "",
    "unread_end_note_id": "",
    "unread_note_count": 0,
    "category": "homefeed.cosmetics_v3",
    "search_key": "",
    "need_num": 8,
    "image_formats": ["jpg", "webp", "avif"],
    "need_filter_image": False,
}

URL = "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed"

B1 = ""
B1B1 = "1"
CTR = 544
RANDOM32 = 0x7FFFFFFF


def now_ms_str() -> str:
    return str(int(time.time() * 1000))


def cookie_get(name: str, cookie: str) -> str:
    m = re.search(rf"(?:^|;\s*){re.escape(name)}=([^;]+)", cookie)
    return m.group(1) if m else ""


def build_headers():
    a1 = cookie_get("a1", COOKIE)
    loadts = cookie_get("loadts", COOKIE)
    dsllt = now_ms_str()
    dsl = now_ms_str()
    now_ms = now_ms_str()
    js = f"""
const {{ buildX3, buildXsCommon }} = require('./xhs_sign_bundle');
const payload = {json.dumps(PAYLOAD, ensure_ascii=False)};
const x = buildX3({{
  url: '/api/sns/web/v1/homefeed',
  payload,
  a1: {json.dumps(a1)},
  loadts: {json.dumps(loadts)},
  random32: {RANDOM32},
  nowMs: {json.dumps(now_ms)},
  ctr: {CTR},
}});
const c = buildXsCommon({{
  a1: {json.dumps(a1)},
  b1: {json.dumps(B1)},
  b1b1: {json.dumps(B1B1)},
  dsllt: {json.dumps(dsllt)},
  dsl: {json.dumps(dsl)},
  platform: 'Windows',
  signCount: 0,
}});
process.stdout.write(JSON.stringify({{ xs: x.xs, xsc: c.xSCommon }}));
"""
    result = subprocess.run(
        ["node", "-e", js],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "node signer failed "
            f"(exit {result.returncode})\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def main():
    built = build_headers()
    headers = {
        "accept": "*/*",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.xiaohongshu.com",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/147.0.0.0 Safari/537.36"
        ),
        "x-s": built["xs"],
        "x-s-common": built["xsc"],
        "cookie": COOKIE,
    }
    body = json.dumps(PAYLOAD, ensure_ascii=False, separators=(",", ":"))
    resp = requests.post(URL, headers=headers, data=body.encode("utf-8"), timeout=30)
    print("x-s =", built["xs"])
    print("x-s-common =", built["xsc"])
    print("status =", resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()
