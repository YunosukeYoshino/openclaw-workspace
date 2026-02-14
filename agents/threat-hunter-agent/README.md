# threat-hunter-agent

## 概要
脅威ハンターエージェント。能動的な脅威ハンティング・調査。

## カテゴリ
セキュリティ・脅威ハンティング

## トリガーワード
脅威ハンティング, ハンティング, 脅威調査

## 主な機能

### データ管理
- threat-hunter-agent 関連データのSQLiteデータベース管理
- CRUD操作の実装
- 検索・フィルタリング機能

### チャットボット機能
- Discord連携によるインタラクティブ応答
- 自然言語によるクエリ処理
- コマンドパターンマッチング

## 使用方法

### インストール
```bash
cd agents/threat-hunter-agent
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
