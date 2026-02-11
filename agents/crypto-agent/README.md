# Crypto Agent / 仮想通貨管理エージェント

暗号資産の価格追跡、価格変動の通知、ポートフォリオ管理を行うエージェントです。
Tracks cryptocurrency prices, price alerts, and portfolio management.

## Features / 機能

- **保有資産管理 / Holdings Management**
  - 暗号資産の追加・管理
  - 購入価格の記録
  - 購入日時の記録

- **価格追跡 / Price Tracking**
  - 価格データの記録・更新
  - 最新価格の確認

- **価格通知 / Price Alerts**
  - 目標価格を超えた場合の通知
  - 目標価格を下回った場合の通知

- **ポートフォリオ管理 / Portfolio Management**
  - 保有資産の総価値計算
  - 各資産の現在価値表示

## Usage / 使い方

### 日本語

```
保有: BTC, 数量: 0.5, 購入価格: 50000
価格: BTC 55000
通知: BTC 60000 以上
保有
通知
価値
```

### English

```
holding: BTC, amount: 0.5, price: 50000
price: ETH 3500
add alert BTC 55000 above
holdings
alerts
portfolio
```

## Commands / コマンド

| Japanese | English | Description |
|----------|---------|-------------|
| 保有: {symbol}, 数量: {amount} | holding: {symbol}, amount: {amount} | Add holding |
| 価格: {symbol} {price} | price: {symbol} {price} | Update price |
| 通知: {symbol} {price} 以上/以下 | alert: {symbol} {price} above/below | Add alert |
| 保有 | holdings | List holdings |
| 通知 | alerts | List alerts |
| 価値 | portfolio / value | Portfolio value |

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Database / データベース

- SQLiteを使用
- 自動的に `crypto.db` が作成されます

## Notes / 注意事項

- 価格データは手動で更新する必要があります
- 実際のAPI連携には別途実装が必要です
- シンボルは大文字で入力してください
