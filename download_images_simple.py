#!/usr/bin/env python3
"""
シンプル版: requests + BeautifulSoupで画像をダウンロード
"""

import hashlib
import os
import time
from pathlib import Path
from typing import Set

import requests
from bs4 import BeautifulSoup

# 設定
SEARCH_QUERY = "田中美久"
OUTPUT_DIR = "images/miku_tanaka"
MAX_IMAGES = 50


def get_image_hash(image_data: bytes) -> str:
    """画像データのハッシュを計算"""
    return hashlib.md5(image_data).hexdigest()


def download_images():
    """画像をダウンロード"""
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    existing_hashes: Set[str] = set()
    hash_file = Path(OUTPUT_DIR) / ".hashes"
    if hash_file.exists():
        with open(hash_file, "r") as f:
            existing_hashes = set(line.strip() for line in f)

    downloaded = 0
    skipped = 0

    # Bing Image Searchを使う
    url = "https://www.bing.com/images/search"
    params = {
        "q": SEARCH_QUERY,
        "form": "HDRSC2",
        "first": "1",
        "tsc": "ImageBasicHover"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"検索中: {SEARCH_QUERY}")
    response = requests.get(url, params=params, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")

    # 画像URLを抽出
    img_tags = soup.find_all("img")
    print(f"{len(img_tags)}個の画像タグが見つかりました")

    for i, img in enumerate(img_tags[:MAX_IMAGES * 2]):
        try:
            src = img.get("src")
            murl = img.get("data-murl")

            # data-murl（高画質）を優先
            img_url = murl or src

            if not img_url:
                continue

            print(f"[{i+1}] 画像を取得中: {img_url[:60]}...")

            img_response = requests.get(img_url, headers=headers, timeout=15)
            if img_response.status_code != 200:
                print(f"  スキップ: ステータス {img_response.status_code}")
                skipped += 1
                continue

            image_data = img_response.content

            if len(image_data) < 5000:
                print(f"  スキップ: サイズ {len(image_data)} bytes")
                skipped += 1
                continue

            img_hash = get_image_hash(image_data)
            if img_hash in existing_hashes:
                print(f"  スキップ: ダブり検出")
                skipped += 1
                continue

            filename = f"{int(time.time())}_{img_hash[:8]}.jpg"
            filepath = Path(OUTPUT_DIR) / filename

            with open(filepath, "wb") as f:
                f.write(image_data)

            existing_hashes.add(img_hash)
            downloaded += 1

            print(f"  保存: {filename} ({len(image_data)} bytes)")

            if downloaded >= MAX_IMAGES:
                print(f"目標数 {MAX_IMAGES} 枚に達しました")
                break

        except Exception as e:
            print(f"  エラー: {e}")
            skipped += 1
            continue

    with open(hash_file, "w") as f:
        for h in existing_hashes:
            f.write(f"{h}\n")

    print(f"\n完了！")
    print(f"  ダウンロード: {downloaded} 枚")
    print(f"  スキップ: {skipped} 枚")
    print(f"  保存先: {OUTPUT_DIR}/")


if __name__ == "__main__":
    download_images()
