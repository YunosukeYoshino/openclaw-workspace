# postmortem-manager-agent

## 概要
ポストモーテム管理エージェント。事後分析・レポート作成。

## カテゴリ
セキュリティパッチ・監査

## トリガーワード
ポストモーテム, 事後分析, 振り返り

## 主な機能

### データ管理
- postmortem-manager-agent 関連データのSQLiteデータベース管理
- CRUD操作の実装
- 検索・フィルタリング機能

### チャットボット機能
- Discord連携によるインタラクティブ応答
- 自然言語によるクエリ処理
- コマンドパターンマッチング

## 使用方法

### インストール
```bash
cd agents/postmortem-manager-agent
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
