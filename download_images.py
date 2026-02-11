#!/usr/bin/env python3
"""
田中美久の画像をGoogle Imagesから取得するスクリプト
- 新しい順でソート
- ダブりチェック（ハッシュベース）
"""

import hashlib
import os
import time
from pathlib import Path
from typing import Set
from urllib.parse import urlencode, quote

# Playwrightをimport
from playwright.sync_api import sync_playwright

# 設定
SEARCH_QUERY = "田中美久"
OUTPUT_DIR = "images/miku_tanaka"
MAX_IMAGES = 50  # 取得する最大画像数
SCROLL_PAUSE = 1.5  # スクロールごとの待機時間（秒）


def get_image_hash(image_data: bytes) -> str:
    """画像データのハッシュを計算"""
    return hashlib.md5(image_data).hexdigest()


def download_images():
    """画像をダウンロード"""
    # 出力ディレクトリを作成
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 既存のハッシュをロード
    existing_hashes: Set[str] = set()
    hash_file = Path(OUTPUT_DIR) / ".hashes"
    if hash_file.exists():
        with open(hash_file, "r") as f:
            existing_hashes = set(line.strip() for line in f)

    downloaded = 0
    skipped = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 新しい順の検索URL（tbs=ssbr:1,ssbr:1m,ssbr:1y）
        query = quote(SEARCH_QUERY)
        url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=ssbr:1,ssbr:1m,ssbr:1y&udm=2"

        print(f"URLを開いています: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)

        # 画像をスクロールして読み込み
        last_height = page.evaluate("document.body.scrollHeight")
        for i in range(5):  # 5回スクロール
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(SCROLL_PAUSE)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"スクロール {i+1}/5...")

        # すべての画像要素を取得
        print("画像を探しています...")
        images = page.query_selector_all("img[src]")

        print(f"{len(images)}枚の画像要素が見つかりました")

        for i, img in enumerate(images[:MAX_IMAGES * 2]):  # 多めに取得してフィルタ
            try:
                src = img.get_attribute("src")
                if not src or src.startswith("data:"):
                    continue

                # サムネイルスキップ（小さい画像）
                if len(src) < 50 or "encrypted-tbn" not in src:
                    continue

                print(f"[{i+1}] 画像を取得中: {src[:50]}...")

                # 画像データを取得
                response = context.request.get(src)
                if response.status != 200:
                    print(f"  スキップ: ステータス {response.status}")
                    skipped += 1
                    continue

                image_data = response.body()

                # サイズチェック（小さい画像はスキップ）
                if len(image_data) < 5000:
                    print(f"  スキップ: サイズ {len(image_data)} bytes")
                    skipped += 1
                    continue

                # ハッシュチェック（ダブり排除）
                img_hash = get_image_hash(image_data)
                if img_hash in existing_hashes:
                    print(f"  スキップ: ダブり検出")
                    skipped += 1
                    continue

                # 保存
                filename = f"{int(time.time())}_{img_hash[:8]}.jpg"
                filepath = Path(OUTPUT_DIR) / filename

                with open(filepath, "wb") as f:
                    f.write(image_data)

                existing_hashes.add(img_hash)
                downloaded += 1

                print(f"  保存: {filename}")

                if downloaded >= MAX_IMAGES:
                    print(f"目標数 {MAX_IMAGES} 枚に達しました")
                    break

            except Exception as e:
                print(f"  エラー: {e}")
                skipped += 1
                continue

        # ハッシュを保存
        with open(hash_file, "w") as f:
            for h in existing_hashes:
                f.write(f"{h}\n")

        browser.close()

    print(f"\n完了！")
    print(f"  ダウンロード: {downloaded} 枚")
    print(f"  スキップ: {skipped} 枚")
    print(f"  保存先: {OUTPUT_DIR}/")


if __name__ == "__main__":
    download_images()
