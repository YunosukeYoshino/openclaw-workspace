# Network Agent

Network management Discord bot with NLP-based message processing.

## Features

- WiFi network management (SSIDs, passwords, security settings)
- Network device tracking (MAC addresses, IPs, device types)
- Port forwarding management
- VPN configuration storage
- DNS settings management
- Password vault for network credentials
- Natural language processing for easy interaction
- Bilingual support (Japanese/English)

## Installation

```bash
pip install discord.py
```

## Database Setup

The bot uses SQLite for data storage. Database tables are automatically created on first run.

### Tables

- `wifi_networks` - WiFi network configurations
- `devices` - Network device information
- `port_forwards` - Port forwarding rules
- `vpn_configs` - VPN connection settings
- `dns_settings` - DNS configuration profiles
- `password_vault` - Encrypted password storage
- `user_settings` - User preferences (language, timezone)

## Usage

### Natural Language

The bot understands natural language queries:

- "Show my WiFi networks" / "WiFi一覧を見て"
- "What devices are on my network?" / "デバイス一覧"
- "Show port forwards" / "ポート転送一覧"
- "My VPN configs" / "VPN設定"
- "Network status" / "ネットワーク状況"

### Commands

#### WiFi Management
```
!net wifi add <ssid> <password>           # Add WiFi network
!net wifi list                            # List all WiFi networks
```

#### Device Management
```
!net device add <name> [mac] [ip] [type]  # Add device
!net device list                          # List all devices
```

#### Port Forwarding
```
!net port add <name> <ext_port> <int_port> <ip> [proto]  # Add port forward
!net port list                                            # List port forwards
```

#### VPN Management
```
!net vpn add <name> <server> [user] [pass] [provider]    # Add VPN
!net vpn list                                            # List VPNs
```

#### DNS Settings
```
!net dns add <name> <primary> [secondary] [type]  # Add DNS
!net dns list                                        # List DNS settings
```

#### Password Vault
```
!net password add <service> <password> [user] [url] [category]  # Add password
!net password list                                              # List passwords
```

#### General
```
!net summary   # Show network management summary
!net help      # Show help message
```

## Examples

### Adding a WiFi network
```
!net wifi add MyHomeWifi mypassword123
```

### Adding a device
```
!net device add "My Laptop" AA:BB:CC:DD:EE:FF 192.168.1.100 laptop
```

### Adding port forward
```
!net port add "Web Server" 80 80 192.168.1.50 TCP
```

### Adding VPN
```
!net vpn add "Office VPN" vpn.company.com user pass123 MyCompany
```

### Adding password
```
!net password add "Router Admin" mypass123 admin 192.168.1.1 network
```

## Database API

```python
from db import NetworkDatabase, get_db

# Initialize database
db = get_db("network.db")

# WiFi operations
wifi_id = db.add_wifi(user_id, "MyWiFi", "password123")
networks = db.get_all_wifi(user_id)

# Device operations
device_id = db.add_device(user_id, "My PC", mac="AA:BB:CC:DD:EE:FF")
devices = db.get_all_devices(user_id)

# Port forwarding
pf_id = db.add_port_forward(user_id, "SSH", 22, 22, "192.168.1.100")
port_forwards = db.get_all_port_forwards(user_id)

# VPN
vpn_id = db.add_vpn(user_id, "Office VPN", "vpn.company.com")
vpns = db.get_all_vpns(user_id)

# DNS
dns_id = db.add_dns(user_id, "Google DNS", "8.8.8.8", "8.8.4.4")
dns_list = db.get_all_dns(user_id)

# Passwords
pwd_id = db.add_password(user_id, "Router", "admin123", "admin")
passwords = db.get_all_passwords(user_id)

# Summary
summary = db.get_summary(user_id)
```

## Running the Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Security Notes

- Passwords are stored in the database. Consider implementing encryption for production use.
- Ensure proper access controls on the database file.
- Use environment variables for sensitive configuration.

## Language Support

The bot automatically detects language from user messages and responds accordingly:
- Japanese: 日本語
- English: English

Switch language explicitly:
- "Speak Japanese" / "日本語で話して"
- "Speak English" / "英語で話して"
