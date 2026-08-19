#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetch Yandex search snippets for OZON products — collect prices."""
import sys, re, html as html_mod
from curl_cffi import requests as creq

def yandex_search(query, n=10):
    url = "https://yandex.ru/search/"
    r = creq.get(url, impersonate="chrome", timeout=40, params={'text': query},
                 headers={'Accept-Language': 'ru-RU,ru;q=0.9'})
    print("STATUS:", r.status_code, "LEN:", len(r.text))
    if r.status_code != 200:
        print(r.text[:500])
        return []
    text = r.text
    # Yandex snippets: look for ozon links with price context
    results = []
    # find all blocks "https://www.ozon.ru/product/..." with nearby text
    for m in re.finditer(r'href="(https://www\.ozon\.ru/product/[^"]+)"[^>]*>(.*?)</a>', text, re.DOTALL):
        url2 = html_mod.unescape(m.group(1))
        label = re.sub(r'<[^>]+>', ' ', m.group(2))
        label = re.sub(r'\s+', ' ', html_mod.unescape(label)).strip()
        results.append((url2, label))
    # also generic price pattern
    prices = re.findall(r'(\d[\d\s]*)\s*₽', text)
    return results, prices[:30]

if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else 'ozon чип clt-1100XK'
    res, prices = yandex_search(q)
    print("OZON LINKS FOUND:", len(res))
    for u, l in res[:15]:
        print("*", u)
        print("  ", l[:200])
    print("PRICES:", prices)
