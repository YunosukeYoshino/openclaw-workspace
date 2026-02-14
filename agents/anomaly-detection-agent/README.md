# anomaly-detection-agent

## 概要
異常検知エージェント。異常行動・パターンの検知・分析。

## カテゴリ
セキュリティアナリティクス

## トリガーワード
異常検知, 異常行動, パターン検知

## 主な機能

### データ管理
- anomaly-detection-agent 関連データのSQLiteデータベース管理
- CRUD操作の実装
- 検索・フィルタリング機能

### チャットボット機能
- Discord連携によるインタラクティブ応答
- 自然言語によるクエリ処理
- コマンドパターンマッチング

## 使用方法

### インストール
```bash
cd agents/anomaly-detection-agent
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
