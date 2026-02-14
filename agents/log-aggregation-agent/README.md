# log-aggregation-agent

## 概要
ログ集約エージェント。ログの収集・集約・分析。

## カテゴリ
オブザーバビリティ・モニタリング

## トリガーワード
ログ集約, ログ分析, ログ管理

## 主な機能

### データ管理
- log-aggregation-agent 関連データのSQLiteデータベース管理
- CRUD操作の実装
- 検索・フィルタリング機能

### チャットボット機能
- Discord連携によるインタラクティブ応答
- 自然言語によるクエリ処理
- コマンドパターンマッチング

## 使用方法

### インストール
```bash
cd agents/log-aggregation-agent
pip install -r requirements.txt
```

### 実行
```bash
python agent.py
```

## ライセンス
MIT License

## バージョン
1.0.0
