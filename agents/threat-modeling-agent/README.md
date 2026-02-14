# threat-modeling-agent

## 概要
脅威モデリングエージェント。脅威モデルの作成・分析。

## カテゴリ
セキュリティ・脅威ハンティング

## トリガーワード
脅威モデリング, 脅威モデル, 脅威分析

## 主な機能

### データ管理
- threat-modeling-agent 関連データのSQLiteデータベース管理
- CRUD操作の実装
- 検索・フィルタリング機能

### チャットボット機能
- Discord連携によるインタラクティブ応答
- 自然言語によるクエリ処理
- コマンドパターンマッチング

## 使用方法

### インストール
```bash
cd agents/threat-modeling-agent
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
