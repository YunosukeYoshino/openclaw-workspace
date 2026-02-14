#!/usr/bin/env python3
"""ProductHunt HTMLの構造を解析"""

import urllib.request
import re
import json
import html

def analyze_html():
    """HTMLを解析"""
    url = "https://www.producthunt.com/posts"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        html_content = response.read().decode('utf-8')

    print(f"HTMLサイズ: {len(html_content)} 文字\n")

    # JSON-LDを取得
    jsonld_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
    matches = re.findall(jsonld_pattern, html_content, re.DOTALL)

    if matches:
        print(f"✅ JSON-LD: {len(matches)} 件\n")

        for i, match in enumerate(matches, 1):
            try:
                data = json.loads(match)
                print(f"--- JSON-LD #{i} ---")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                print("...\n")
            except:
                print("解析エラー\n")

    # その他の埋め込みデータを探す
    print("=" * 60)
    print("その他の埋め込み検索:")

    # __NUXT__ のような変数
    nuxt_match = re.search(r'window\.([A-Z_]+)\s*=\s*({.+?});', html_content, re.DOTALL)
    if nuxt_match:
        var_name = nuxt_match.group(1)
        print(f"✅ window.{var_name} を発見")

        # JSONの一部を表示
        json_str = nuxt_match.group(2)
        try:
            data = json.loads(json_str)
            print(f"  キー: {list(data.keys())[:10]}")
        except:
            print(f"  JSONパース失敗")

    # __buildManifest__ など
    build_manifest = re.search(r'__buildManifest\s*=\s*({.+?});', html_content, re.DOTALL)
    if build_manifest:
        print("✅ __buildManifest を発見")

    # __NEXT_DATA__ を別の方法で探す
    next_data_patterns = [
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        r'__NEXT_DATA__\s*=\s*({.+?})',
        r'"__NEXT_DATA__":\s*({.+?})',
    ]

    for pattern in next_data_patterns:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            print(f"✅ __NEXT_DATA__ パターンを発見")
            break

if __name__ == "__main__":
    analyze_html()
