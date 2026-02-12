#!/usr/bin/env python3
"""
network-agent database module
SQLite-based network management
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class NetworkDatabase:
    """SQLite database for network records"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "network.db"
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()

        # WiFi networks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wifi_networks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                ssid TEXT NOT NULL,
                password TEXT,
                security_type TEXT DEFAULT 'WPA2',
                frequency_5ghz BOOLEAN DEFAULT 0,
                notes TEXT,
                location TEXT,
                last_connected TIMESTAMP,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Network devices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                mac_address TEXT,
                ip_address TEXT,
                device_type TEXT,
                manufacturer TEXT,
                os TEXT,
                notes TEXT,
                last_seen TIMESTAMP,
                is_static_ip BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Port forwards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS port_forwards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                service_name TEXT NOT NULL,
                external_port INTEGER NOT NULL,
                internal_port INTEGER NOT NULL,
                internal_ip TEXT NOT NULL,
                protocol TEXT DEFAULT 'TCP',
                enabled BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # VPN configs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vpn_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                provider TEXT,
                server_address TEXT,
                username TEXT,
                password TEXT,
                protocol TEXT DEFAULT 'OpenVPN',
                config_file TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # DNS settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dns_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                primary_dns TEXT,
                secondary_dns TEXT,
                network_type TEXT DEFAULT 'home',
                notes TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Password vault table (encrypted storage for network passwords)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                service_name TEXT NOT NULL,
                username TEXT,
                password TEXT,
                url TEXT,
                notes TEXT,
                category TEXT DEFAULT 'network',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                language TEXT DEFAULT 'ja',
                timezone TEXT DEFAULT 'UTC'
            )
        """)

        self.conn.commit()

    # User Settings
    def get_user_settings(self, user_id: str) -> Dict:
        """Get user settings"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            'user_id': user_id,
            'language': 'ja',
            'timezone': 'UTC'
        }

    def set_user_language(self, user_id: str, language: str):
        """Set user language preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (user_id, language)
            VALUES (?, COALESCE((SELECT language FROM user_settings WHERE user_id = ?), ?))
        """, (user_id, user_id, language))
        cursor.execute(
            "UPDATE user_settings SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        self.conn.commit()

    # WiFi Networks CRUD
    def add_wifi(self, user_id: str, ssid: str, password: str = None,
                 security_type: str = 'WPA2', frequency_5ghz: bool = False,
                 notes: str = None, location: str = None,
                 is_primary: bool = False) -> int:
        """Add a new WiFi network"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO wifi_networks
            (user_id, ssid, password, security_type, frequency_5ghz,
             notes, location, is_primary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, ssid, password, security_type, frequency_5ghz,
              notes, location, is_primary))
        self.conn.commit()
        return cursor.lastrowid

    def get_wifi(self, wifi_id: int) -> Optional[Dict]:
        """Get a single WiFi network by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM wifi_networks WHERE id = ?", (wifi_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_wifi(self, user_id: str) -> List[Dict]:
        """Get all WiFi networks for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM wifi_networks
            WHERE user_id = ?
            ORDER BY is_primary DESC, ssid ASC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_wifi(self, wifi_id: int, **kwargs) -> bool:
        """Update a WiFi network"""
        allowed_fields = ['ssid', 'password', 'security_type', 'frequency_5ghz',
                         'notes', 'location', 'last_connected', 'is_primary']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [wifi_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE wifi_networks SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_wifi(self, wifi_id: int, user_id: str = None) -> bool:
        """Delete a WiFi network"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM wifi_networks WHERE id = ? AND user_id = ?",
                (wifi_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM wifi_networks WHERE id = ?", (wifi_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Devices CRUD
    def add_device(self, user_id: str, name: str, mac_address: str = None,
                   ip_address: str = None, device_type: str = None,
                   manufacturer: str = None, os: str = None,
                   notes: str = None, is_static_ip: bool = False) -> int:
        """Add a new network device"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO devices
            (user_id, name, mac_address, ip_address, device_type,
             manufacturer, os, notes, is_static_ip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, mac_address, ip_address, device_type,
              manufacturer, os, notes, is_static_ip))
        self.conn.commit()
        return cursor.lastrowid

    def get_device(self, device_id: int) -> Optional[Dict]:
        """Get a single device by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_devices(self, user_id: str) -> List[Dict]:
        """Get all devices for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM devices
            WHERE user_id = ?
            ORDER BY name ASC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_device(self, device_id: int, **kwargs) -> bool:
        """Update a device"""
        allowed_fields = ['name', 'mac_address', 'ip_address', 'device_type',
                         'manufacturer', 'os', 'notes', 'last_seen', 'is_static_ip']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [device_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE devices SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_device(self, device_id: int, user_id: str = None) -> bool:
        """Delete a device"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM devices WHERE id = ? AND user_id = ?",
                (device_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Port Forwards CRUD
    def add_port_forward(self, user_id: str, service_name: str,
                        external_port: int, internal_port: int,
                        internal_ip: str, protocol: str = 'TCP',
                        notes: str = None) -> int:
        """Add a new port forward rule"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO port_forwards
            (user_id, service_name, external_port, internal_port,
             internal_ip, protocol, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, service_name, external_port, internal_port,
              internal_ip, protocol, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_port_forward(self, pf_id: int) -> Optional[Dict]:
        """Get a single port forward by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM port_forwards WHERE id = ?", (pf_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_port_forwards(self, user_id: str) -> List[Dict]:
        """Get all port forwards for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM port_forwards
            WHERE user_id = ?
            ORDER BY external_port ASC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_port_forward(self, pf_id: int, **kwargs) -> bool:
        """Update a port forward"""
        allowed_fields = ['service_name', 'external_port', 'internal_port',
                         'internal_ip', 'protocol', 'enabled', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [pf_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE port_forwards SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_port_forward(self, pf_id: int, user_id: str = None) -> bool:
        """Delete a port forward"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM port_forwards WHERE id = ? AND user_id = ?",
                (pf_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM port_forwards WHERE id = ?", (pf_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # VPN CRUD
    def add_vpn(self, user_id: str, name: str, provider: str = None,
                server_address: str = None, username: str = None,
                password: str = None, protocol: str = 'OpenVPN',
                config_file: str = None, notes: str = None) -> int:
        """Add a new VPN configuration"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO vpn_configs
            (user_id, name, provider, server_address, username, password,
             protocol, config_file, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, provider, server_address, username, password,
              protocol, config_file, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_vpn(self, vpn_id: int) -> Optional[Dict]:
        """Get a single VPN by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM vpn_configs WHERE id = ?", (vpn_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_vpns(self, user_id: str) -> List[Dict]:
        """Get all VPNs for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM vpn_configs
            WHERE user_id = ?
            ORDER BY is_active DESC, name ASC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_vpn(self, vpn_id: int, **kwargs) -> bool:
        """Update a VPN configuration"""
        allowed_fields = ['name', 'provider', 'server_address', 'username',
                         'password', 'protocol', 'config_file', 'notes', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [vpn_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE vpn_configs SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_vpn(self, vpn_id: int, user_id: str = None) -> bool:
        """Delete a VPN configuration"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM vpn_configs WHERE id = ? AND user_id = ?",
                (vpn_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM vpn_configs WHERE id = ?", (vpn_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # DNS Settings CRUD
    def add_dns(self, user_id: str, name: str, primary_dns: str,
                secondary_dns: str = None, network_type: str = 'home',
                notes: str = None, is_default: bool = False) -> int:
        """Add a new DNS configuration"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO dns_settings
            (user_id, name, primary_dns, secondary_dns, network_type, notes, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, primary_dns, secondary_dns, network_type, notes, is_default))
        self.conn.commit()
        return cursor.lastrowid

    def get_dns(self, dns_id: int) -> Optional[Dict]:
        """Get a single DNS configuration by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM dns_settings WHERE id = ?", (dns_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_dns(self, user_id: str) -> List[Dict]:
        """Get all DNS configurations for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM dns_settings
            WHERE user_id = ?
            ORDER BY is_default DESC, name ASC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_dns(self, dns_id: int, **kwargs) -> bool:
        """Update a DNS configuration"""
        allowed_fields = ['name', 'primary_dns', 'secondary_dns',
                         'network_type', 'notes', 'is_default']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [dns_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE dns_settings SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_dns(self, dns_id: int, user_id: str = None) -> bool:
        """Delete a DNS configuration"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM dns_settings WHERE id = ? AND user_id = ?",
                (dns_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM dns_settings WHERE id = ?", (dns_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Password Vault CRUD
    def add_password(self, user_id: str, service_name: str, password: str,
                     username: str = None, url: str = None, notes: str = None,
                     category: str = 'network') -> int:
        """Add a new password to the vault"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO password_vault
            (user_id, service_name, username, password, url, notes, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, service_name, username, password, url, notes, category))
        self.conn.commit()
        return cursor.lastrowid

    def get_password(self, pwd_id: int) -> Optional[Dict]:
        """Get a single password by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM password_vault WHERE id = ?", (pwd_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_passwords(self, user_id: str, category: str = None) -> List[Dict]:
        """Get all passwords for a user, optionally filtered by category"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM password_vault
                WHERE user_id = ? AND category = ?
                ORDER BY service_name ASC
            """, (user_id, category))
        else:
            cursor.execute("""
                SELECT * FROM password_vault
                WHERE user_id = ?
                ORDER BY category, service_name ASC
            """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_password(self, pwd_id: int, **kwargs) -> bool:
        """Update a password"""
        allowed_fields = ['service_name', 'username', 'password', 'url', 'notes', 'category']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        updates['last_updated'] = datetime.now().isoformat()
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [pwd_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE password_vault SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_password(self, pwd_id: int, user_id: str = None) -> bool:
        """Delete a password"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM password_vault WHERE id = ? AND user_id = ?",
                (pwd_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM password_vault WHERE id = ?", (pwd_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Summary
    def get_summary(self, user_id: str) -> Dict:
        """Get network management summary"""
        cursor = self.conn.cursor()

        summary = {}

        # Count WiFi networks
        cursor.execute("SELECT COUNT(*) as count FROM wifi_networks WHERE user_id = ?", (user_id,))
        summary['wifi_count'] = cursor.fetchone()['count'] or 0

        # Count devices
        cursor.execute("SELECT COUNT(*) as count FROM devices WHERE user_id = ?", (user_id,))
        summary['device_count'] = cursor.fetchone()['count'] or 0

        # Count port forwards
        cursor.execute("SELECT COUNT(*) as count FROM port_forwards WHERE user_id = ?", (user_id,))
        summary['port_forward_count'] = cursor.fetchone()['count'] or 0

        # Count VPNs
        cursor.execute("SELECT COUNT(*) as count FROM vpn_configs WHERE user_id = ?", (user_id,))
        summary['vpn_count'] = cursor.fetchone()['count'] or 0

        # Count passwords
        cursor.execute("SELECT COUNT(*) as count FROM password_vault WHERE user_id = ?", (user_id,))
        summary['password_count'] = cursor.fetchone()['count'] or 0

        # Count active VPNs
        cursor.execute("SELECT COUNT(*) as count FROM vpn_configs WHERE user_id = ? AND is_active = 1", (user_id,))
        summary['active_vpn_count'] = cursor.fetchone()['count'] or 0

        # Count enabled port forwards
        cursor.execute("SELECT COUNT(*) as count FROM port_forwards WHERE user_id = ? AND enabled = 1", (user_id,))
        summary['enabled_port_forward_count'] = cursor.fetchone()['count'] or 0

        return summary

    # Search
    def search_wifi(self, user_id: str, keyword: str) -> List[Dict]:
        """Search WiFi networks by keyword"""
        cursor = self.conn.cursor()
        pattern = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM wifi_networks
            WHERE user_id = ? AND (ssid LIKE ? OR notes LIKE ? OR location LIKE ?)
            ORDER BY ssid ASC
        """, (user_id, pattern, pattern, pattern))
        return [dict(row) for row in cursor.fetchall()]

    def search_devices(self, user_id: str, keyword: str) -> List[Dict]:
        """Search devices by keyword"""
        cursor = self.conn.cursor()
        pattern = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM devices
            WHERE user_id = ? AND (name LIKE ? OR mac_address LIKE ? OR ip_address LIKE ?
                                    OR manufacturer LIKE ? OR notes LIKE ?)
            ORDER BY name ASC
        """, (user_id, pattern, pattern, pattern, pattern, pattern))
        return [dict(row) for row in cursor.fetchall()]


# Convenience functions
def get_db(db_path: str = None) -> NetworkDatabase:
    """Get a database instance"""
    return NetworkDatabase(db_path)
