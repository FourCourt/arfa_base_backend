#!/usr/bin/env python3
"""
檢查當前環境配置
"""
from app.core.config import settings
from app.core.environments import get_environment, is_development, is_production

def check_environment():
    """檢查當前環境配置"""
    print("🔍 環境配置檢查")
    print("=" * 50)
    
    # 基本信息
    print(f"環境: {get_environment()}")
    print(f"項目名稱: {settings.PROJECT_NAME}")
    print(f"版本: {settings.VERSION}")
    print(f"調試模式: {settings.DEBUG}")
    
    # 數據庫信息
    print(f"\n📊 數據庫配置:")
    print(f"連接字符串: {settings.DATABASE_URL}")
    
    if is_development():
        print("✅ 開發環境 - 使用 XAMPP MySQL")
        print("數據庫類型: MySQL/MariaDB")
        print("驅動: PyMySQL")
    elif is_production():
        print("🚀 生產環境 - 使用 PostgreSQL")
        print("數據庫類型: PostgreSQL")
        print("驅動: psycopg2")
    else:
        print("⚠️  未知環境")
    
    # CORS 配置
    print(f"\n🌐 CORS 配置:")
    for origin in settings.BACKEND_CORS_ORIGINS:
        print(f"  - {origin}")
    
    # 安全配置
    print(f"\n🔒 安全配置:")
    print(f"密鑰長度: {len(settings.SECRET_KEY)} 字符")
    print(f"算法: {settings.ALGORITHM}")
    print(f"令牌過期時間: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} 分鐘")
    
    print("\n" + "=" * 50)
    
    # 建議
    if is_development():
        print("💡 開發環境建議:")
        print("  - 確保 XAMPP MySQL 服務正在運行")
        print("  - 可以使用 http://localhost/phpmyadmin 管理數據庫")
        print("  - API 文檔: http://localhost:8000/docs")
    elif is_production():
        print("💡 生產環境建議:")
        print("  - 確保 PostgreSQL 服務正在運行")
        print("  - 使用強密碼和安全配置")
        print("  - 設置適當的 CORS 來源")
        print("  - 考慮使用 HTTPS")

if __name__ == "__main__":
    try:
        check_environment()
    except Exception as e:
        print(f"❌ 檢查環境配置時發生錯誤: {e}")
        print("請確保所有依賴已正確安裝")


