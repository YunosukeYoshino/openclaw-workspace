#!/usr/bin/env python3
"""
メモを記録
"""

import sys
sys.path.insert(0, 'agents/memo-agent')
from db import add_memo

# 記録
title = "上長からの連絡"
content = "休みの日なのに、一日中寝ててたら上長から連絡あってナイーブになった"
tags = ["仕事", "上長", "休み", "ナイーブ"]
category = "日常"

entry_id = add_memo(title, content, category, tags)
print(f"✅ メモ #{entry_id} 追加完了")
print(f"タイトル: {title}")
print(f"内容: {content}")
print(f"タグ: {', '.join(tags)}")
