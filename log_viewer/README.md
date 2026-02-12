# Log Viewer / ログビューア

システムログの検索・表示

## 機能

- ログファイル一覧
- ログ検索
- タイムスタンプ抽出
- 最近のログフィルタリング

## 使い方

```bash
python3 implementation.py
```

## API

### ログ検索

```python
viewer.search_logs(query="error", hours=24)
```

### ログファイル一覧

```python
viewer.get_log_files()
```

---

# Log Viewer

System log search and viewer.

## Features

- Log file listing
- Log search
- Timestamp extraction
- Recent logs filtering

## Usage

```bash
python3 implementation.py
```

## API

### Search Logs

```python
viewer.search_logs(query="error", hours=24)
```

### List Log Files

```python
viewer.get_log_files()
```
