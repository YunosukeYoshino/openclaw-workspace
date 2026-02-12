# Device Agent / デバイス管理エージェント

A Discord bot for managing devices, warranties, maintenance, and assignments / デバイス、保証、メンテナンス、貸出を管理するDiscordボット

## Features / 機能

- **Device Registration** - Track all your devices / すべてのデバイスを登録・追跡
- **Warranty Tracking** - Monitor warranty expiration / 保証期限の管理
- **Maintenance Records** - Track repairs and maintenance / 修理・メンテナンス履歴
- **Issue Reporting** - Report and track device problems / 問題の報告・追跡
- **Device Assignments** - Track device lending/assignments / デバイスの貸出管理
- **Natural Language** - Japanese/English commands supported / 日本語・英語対応

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Configuration / 設定

Set your Discord bot token:

```bash
export DISCORD_TOKEN='your-bot-token-here'
```

## Usage / 使用方法

Start the bot:

```bash
python agent.py
```

## Commands / コマンド

### Device Registration / デバイス登録

```
add device MacBook Pro, laptop, M2, ABC123, Office, John Doe
登録 MacBook Pro, laptop, M2, ABC123, オフィス, 田中太郎
```

### List Devices / デバイス一覧

```
list devices
list devices active laptop
デバイス一覧
```

### Device Information / デバイス情報

```
device info 5
デバイス情報 5
```

### Search / 検索

```
search MacBook
検索 MacBook
```

### Warranty Check / 保確認

```
warranty check
保証確認
```

### Report Issue / 問題報告

```
issue 5, display, screen flickering
問題 5, ディスプレイ, 画面がちらつく
```

### Maintenance Record / メンテナンス記録

```
maintenance 5, screen replacement, display broken, 250.00
修理 5, 画面交換, 画面が壊れた, 25000
```

### Device Assignment / デバイス貸出

```
assign 5, Jane Smith, remote work
貸出 5, 佐藤花子, 在宅勤務
```

### Statistics / 統計

```
statistics
統計
```

## Database Schema / データベース構造

### devices
- id, name, type, model, serial_number, status, location
- ip_address, mac_address, owner, purchase_date, warranty_expiry
- specifications, notes, created_at, updated_at

### device_maintenance
- id, device_id, maintenance_type, description, cost
- performed_date, performed_by, notes, created_at

### device_issues
- id, device_id, issue_type, description, severity, status
- reported_date, resolved_date, resolution_notes, created_at

### device_assignments
- id, device_id, assigned_to, assigned_date, returned_date
- purpose, notes, created_at

## Device Types / デバイスタイプ

- laptop, desktop, phone, tablet, server
- printer, router, switch, camera, sensor, other

## License / ライセンス

MIT License
