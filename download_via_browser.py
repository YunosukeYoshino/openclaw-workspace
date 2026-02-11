#!/usr/bin/env python3
"""
ブラウザツールを使って画像をダウンロード
CDP経由でブラウザに接続
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Set
from urllib.parse import quote

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 設定
SEARCH_QUERY = "田中美久"
OUTPUT_DIR = "images/miku_tanaka"
MAX_IMAGES = 50
SCROLL_PAUSE = 2

CDP_URL = "http://172.21.0.4:9222"  # OpenClaw sandbox browser CDP


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

    # CDPに接続してセッション情報を取得
    cdp_response = requests.get(f"{CDP_URL}/json")
    sessions = cdp_response.json()

    if not sessions:
        print("CDPセッションが見つかりません")
        return

    page_url = sessions[0].get("url", "")

    print(f"ブラウザに接続中... CDP: {CDP_URL}")

    # Seleniumで既存のブラウザにアタッチ
    chrome_options = ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "172.21.0.4:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Google Imagesに移動
        query = quote(SEARCH_QUERY)
        url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=ssbr:1,ssbr:1m,ssbr:1y&udm=2"

        print(f"URLを開いています: {url}")
        driver.get(url)

        # 画像をスクロールして読み込み
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(SCROLL_PAUSE)
            print(f"スクロール {i+1}/5...")

        # 画像要素を取得
        images = driver.find_elements(By.CSS_SELECTOR, "img[src]")
        print(f"{len(images)}個の画像要素が見つかりました")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for i, img in enumerate(images[:MAX_IMAGES * 2]):
            try:
                src = img.get_attribute("src")

                if not src or src.startswith("data:"):
                    continue

                if "encrypted-tbn" not in src:
                    continue

                print(f"[{i+1}] 画像を取得中: {src[:50]}...")

                img_response = requests.get(src, headers=headers, timeout=15)
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

        driver.quit()

    except Exception as e:
        print(f"エラー: {e}")
        return

    with open(hash_file, "w") as f:
        for h in existing_hashes:
            f.write(f"{h}\n")

    print(f"\n完了！")
    print(f"  ダウンロード: {downloaded} 枚")
    print(f"  スキップ: {skipped} 枚")
    print(f"  保存先: {OUTPUT_DIR}/")


if __name__ == "__main__":
    download_images()
