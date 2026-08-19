#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inspect OZON 403 body + try mobile API hosts."""
import sys, re
from curl_cffi import requests as creq

def show_403(url):
    r = creq.get(url, impersonate="chrome", timeout=40)
    print("STATUS:", r.status_code)
    body = r.text
    # Find the interesting part (after <body>)
    print("LEN:", len(body))
    m = re.search(r'<body.*?>(.*)</body>', body, re.DOTALL)
    if m:
        frag = re.sub(r'<[^>]+>', ' ', m.group(1))
        frag = re.sub(r'\s+', ' ', frag).strip()
        print("BODY TEXT:", frag[:800])
    else:
        print(body[:1000])

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "https://ozon.ru/t/Wc01Y4b"
    print("### Direct page ###")
    show_403(target)

    print("\n### Mobile API entrypoint ###")
    try:
        r = creq.get("https://api.ozon.ru/composer-api.bx/page/json/v2?url=/product/chip-dlya-kartridzha-pantum-ctl-1100xk-dlya-modeley-cp1100-cm1100-3000-str-chernyy-1-sht-3175402320",
                     impersonate="chrome", timeout=40,
                     headers={'Accept': 'application/json'})
        print("STATUS:", r.status_code, "LEN:", len(r.text))
        print(r.text[:800])
    except Exception as e:
        print("ERR:", type(e).__name__, e)
