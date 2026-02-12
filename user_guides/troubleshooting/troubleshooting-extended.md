# トラブルシューティング詳細 / Detailed Troubleshooting

## よくある問題と解決策 / Common Issues & Solutions

### 問題1: ImportError: No module named 'xxx'

**原因**: パッケージがインストールされていない

**解決策**:
```bash
pip install -r requirements.txt
pip install xxx
```

### 問題2: Permission denied: 'database.db'

**原因**: ファイルパーミッションの問題

**解決策**:
```bash
chmod 644 database.db
chown $USER:$USER database.db
```

### 問題3: Connection refused on port 8000

**原因**: APIが起動していないか、ポートが使用中

**解決策**:
```bash
# API起動
cd dashboard && python3 api.py

# ポート確認
lsof -i :8000
```

### 問題4: MemoryError

**原因**: メモリ不足

**解決策**:
```bash
# プロセスを再起動
pkill -f agent.py

# キャッシュをクリア
python3 -c "import gc; gc.collect()"
```

### 問題5: Timeout waiting for response

**原因**: 処理時間が長すぎる

**解決策**:
- タイムアウト値を増やす
- 非同期処理を使用する
- データを分割して処理
