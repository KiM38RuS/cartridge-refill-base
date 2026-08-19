#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetch OZON product pages via curl_cffi (Chrome impersonation), extract prices."""
import sys, re, json
from curl_cffi import requests as creq

def fetch_ozon(url, timeout=45):
    r = creq.get(url, impersonate="chrome", timeout=timeout, headers={
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9',
    })
    return r.status_code, r.text, r.url

def extract_prices(text):
    out = []
    # OZON embeds prices in JSON state; search known keys
    keys = ['cardPrice', 'originalPrice', 'priceWithCard', 'price', 'oldPrice', 'priceValue', 'salePrice', 'basePrice', 'extraDiscount']
    for k in keys:
        for m in re.finditer(r'"%s"\s*:\s*"?(\d+)"?' % re.escape(k), text):
            out.append((k, int(m.group(1))))
    return out

def extract_price_block(text):
    """Find JSON blobs around 'price' keys with context."""
    blocks = []
    for m in re.finditer(r'"price"\s*:\s*\{', text):
        start = m.start()
        # crude: take 800 chars
        blocks.append(text[start:start+800])
        if len(blocks) > 5:
            break
    return blocks

if __name__ == '__main__':
    urls = sys.argv[1:]
    for url in urls:
        try:
            st, text, final = fetch_ozon(url)
            print("=" * 100)
            print("URL:", url)
            print("STATUS:", st, "FINAL:", final, "LEN:", len(text))
            if st != 200:
                print(text[:500])
                continue
            prices = extract_prices(text)
            print("PRICE KEYS:", prices[:50])
            # Deduplicate consecutive
            uniq = []
            seen = set()
            for k, v in prices:
                if (k, v) not in seen:
                    seen.add((k, v))
                    uniq.append((k, v))
            print("UNIQ:", uniq[:40])
            # find title
            t = re.search(r'<title>([^<]*)</title>', text)
            if t:
                print("TITLE:", t.group(1)[:150])
            # dump price blocks to a sidecar for deep inspection
            blobs = extract_price_block(text)
            for i, b in enumerate(blobs[:3]):
                print(f"--- price block {i} ---")
                print(b[:700])
            # Save full page to inspect offline
            import hashlib
            h = hashlib.md5(url.encode()).hexdigest()[:8]
            with open(f"_ozon_{h}.html", "w", encoding="utf-8") as f:
                f.write(text)
            print("SAVED _ozon_%s.html" % h)
        except Exception as e:
            print(url, "ERROR:", type(e).__name__, e)
