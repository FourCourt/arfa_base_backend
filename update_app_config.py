#!/usr/bin/env python3
"""
更新應用程式配置使用 PostgreSQL
"""
import os
import shutil
from datetime import datetime

def update_app_config():
    """更新應用程式配置"""
    print("🔧 更新應用程式配置使用 PostgreSQL...")
    print("=" * 60)
    
    # 備份原始配置
    config_file = "app/core/config.py"
    backup_file = f"app/core/config.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if os.path.exists(config_file):
        shutil.copy2(config_file, backup_file)
        print(f"✅ 已備份原始配置到: {backup_file}")
    
    # 讀取原始配置
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新資料庫 URL
    old_sqlite_url = 'DATABASE_URL = "sqlite:///./app.db"'
    new_postgres_url = 'DATABASE_URL = "postgresql://lazyadmin:2djixxjl@localhost:5432/test"'
    
    if old_sqlite_url in content:
        content = content.replace(old_sqlite_url, new_postgres_url)
        print("✅ 已更新資料庫 URL 為 PostgreSQL")
    else:
        print("⚠️  未找到 SQLite URL，可能需要手動更新")
    
    # 寫入更新後的配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 應用程式配置已更新!")
    print("=" * 60)
    print("📋 PostgreSQL 連接資訊:")
    print("  - 主機: localhost")
    print("  - 端口: 5432")
    print("  - 資料庫: test")
    print("  - 用戶: lazyadmin")
    print("  - 密碼: 2djixxjl")
    print("=" * 60)
    print("🌐 pgAdmin 可視化介面:")
    print("  - URL: http://3.26.158.168")
    print("  - 郵箱: lazy@lazy.com")
    print("  - 密碼: 2djixxjl")
    print("=" * 60)

if __name__ == "__main__":
    update_app_config()
