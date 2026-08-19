#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Harvest OZON product URLs from Yandex search across many queries."""
import sys, re, html as html_mod, json
from curl_cffi import requests as creq

def yandex_ozon_links(query):
    url = "https://yandex.ru/search/"
    r = creq.get(url, impersonate="chrome", timeout=40, params={'text': query},
                 headers={'Accept-Language': 'ru-RU,ru;q=0.9'})
    if r.status_code != 200:
        return []
    text = r.text
    links = {}
    for m in re.finditer(r'href="(https://www\.ozon\.ru/product/[^"]+)"', text):
        u = html_mod.unescape(m.group(1)).split('?')[0].rstrip('/')
        if u not in links:
            links[u] = True
    return list(links)

queries = [
    'озон чип CLT-1100K pantum',
    'озон чип CLT-1100C cyan pantum',
    'озон чип CLT-1100M magenta',
    'озон чип CLT-1100Y yellow',
    'озон набор чипов CLT-1100 CMYK pantum',
    'озон тонер CLT-1100K черный заправка',
    'озон тонер CLT-1100C cyan 60г',
    'озон тонер CLT-1100M magenta',
    'озон тонер CLT-1100Y yellow',
    'озон набор тонеров CLT-1100 4 цвета',
    'озон комплект заправки CLT-1100 тонер чип',
    'озон заправочный комплект pantum CP1100 CM1100',
    'озон чип CTL-1100XK 3000',
    'озон чип CTL-1100XC 2300',
]

all_links = {}
for q in queries:
    try:
        links = yandex_ozon_links(q)
        for u in links:
            all_links[u] = all_links.get(u, 0) + 1
        print(f"[{len(links):2d}] {q}")
    except Exception as e:
        print(f"[ERR] {q}: {type(e).__name__} {e}")

print("\n=== ALL UNIQUE OZON PRODUCTS ===")
for u, cnt in sorted(all_links.items(), key=lambda x: -x[1]):
    print(f"{cnt}x {u}")

with open('_ozon_links.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_links.keys()), f, ensure_ascii=False, indent=1)
print(f"\nSaved {len(all_links)} links to _ozon_links.json")
