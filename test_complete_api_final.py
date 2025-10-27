#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的API測試腳本
測試所有伺服器和資料庫配置相關的API功能
"""

import requests
import json
import time
from datetime import datetime

# API基礎URL
BASE_URL = "http://localhost:8001/api/v1"

def print_test_result(test_name, success, response=None, error=None):
    """打印測試結果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"[{test_name}] {status}")
    if response:
        print(f"  狀態碼: {response.status_code}")
        if response.status_code < 400:
            try:
                data = response.json()
                print(f"  響應: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            except:
                print(f"  響應: {response.text[:200]}...")
        else:
            print(f"  錯誤: {response.text}")
    if error:
        print(f"  錯誤: {error}")
    print()

def test_authentication():
    """測試認證功能"""
    print("=== 認證測試 ===")
    
    # 測試登入
    login_data = {
        "username": "admin",
        "password": "Admin123!@#"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    success = response.status_code == 200
    
    if success:
        data = response.json()
        token = data.get("access_token")
        print_test_result("管理員登入", True, response)
        return token
    else:
        print_test_result("管理員登入", False, response)
        return None

def test_server_apis(token):
    """測試伺服器API"""
    print("=== 伺服器管理測試 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 創建伺服器
    server_data = {
        "server_name": f"測試伺服器_{int(time.time())}",
        "server_ip": "192.168.1.100",
        "server_port": 8080,
        "description": "測試用的開發伺服器",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/servers/", json=server_data, headers=headers)
    success = response.status_code == 200
    print_test_result("創建伺服器", success, response)
    
    if not success:
        return None
    
    server_id = response.json().get("id")
    
    # 2. 獲取伺服器列表
    response = requests.get(f"{BASE_URL}/servers/", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取伺服器列表", success, response)
    
    # 3. 獲取特定伺服器
    response = requests.get(f"{BASE_URL}/servers/{server_id}", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取特定伺服器", success, response)
    
    # 4. 更新伺服器
    update_data = {
        "server_name": f"更新後的伺服器_{int(time.time())}",
        "description": "更新後的描述"
    }
    
    response = requests.put(f"{BASE_URL}/servers/{server_id}", json=update_data, headers=headers)
    success = response.status_code == 200
    print_test_result("更新伺服器", success, response)
    
    return server_id

def test_database_config_apis(token, server_id):
    """測試資料庫配置API"""
    print("=== 資料庫配置測試 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 創建資料庫配置
    config_data = {
        "server_id": server_id,
        "config_name": f"主資料庫_{int(time.time())}",
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "MYSQL",
        "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db",
        "is_active": True,
        "is_default": True
    }
    
    response = requests.post(f"{BASE_URL}/database-configs/servers/{server_id}/configs/", 
                           json=config_data, headers=headers)
    success = response.status_code == 200
    print_test_result("創建資料庫配置", success, response)
    
    if not success:
        return None
    
    config_id = response.json().get("id")
    
    # 2. 獲取使用者所有資料庫配置
    response = requests.get(f"{BASE_URL}/database-configs/", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取使用者資料庫配置列表", success, response)
    
    # 3. 獲取伺服器的資料庫配置
    response = requests.get(f"{BASE_URL}/database-configs/servers/{server_id}/configs/", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取伺服器資料庫配置列表", success, response)
    
    # 4. 獲取特定資料庫配置
    response = requests.get(f"{BASE_URL}/database-configs/{config_id}", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取特定資料庫配置", success, response)
    
    # 5. 更新資料庫配置
    update_data = {
        "config_name": f"更新後的資料庫_{int(time.time())}",
        "description": "更新後的描述"
    }
    
    response = requests.put(f"{BASE_URL}/database-configs/{config_id}", json=update_data, headers=headers)
    success = response.status_code == 200
    print_test_result("更新資料庫配置", success, response)
    
    # 6. 獲取預設資料庫配置
    response = requests.get(f"{BASE_URL}/database-configs/servers/{server_id}/default/", headers=headers)
    success = response.status_code == 200
    print_test_result("獲取預設資料庫配置", success, response)
    
    # 7. 測試資料庫連接（不保存）
    test_data = {
        "config_name": "測試連接",
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "MYSQL",
        "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db"
    }
    
    response = requests.post(f"{BASE_URL}/database-configs/test/", json=test_data, headers=headers)
    success = response.status_code == 200
    print_test_result("測試資料庫連接（不保存）", success, response)
    
    # 8. 測試資料庫連接（保存結果）
    response = requests.post(f"{BASE_URL}/database-configs/{config_id}/test/", headers=headers)
    success = response.status_code == 200
    print_test_result("測試資料庫連接（保存結果）", success, response)
    
    return config_id

def test_cleanup(token, server_id, config_id):
    """清理測試數據"""
    print("=== 清理測試數據 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 刪除資料庫配置
    if config_id:
        response = requests.delete(f"{BASE_URL}/database-configs/{config_id}", headers=headers)
        success = response.status_code == 200
        print_test_result("刪除資料庫配置", success, response)
    
    # 刪除伺服器
    if server_id:
        response = requests.delete(f"{BASE_URL}/servers/{server_id}", headers=headers)
        success = response.status_code == 200
        print_test_result("刪除伺服器", success, response)

def main():
    """主測試函數"""
    print("開始API完整測試")
    print("=" * 50)
    
    # 測試認證
    token = test_authentication()
    if not token:
        print("認證失敗，無法繼續測試")
        return
    
    # 測試伺服器API
    server_id = test_server_apis(token)
    if not server_id:
        print("伺服器測試失敗，無法繼續測試資料庫配置")
        return
    
    # 測試資料庫配置API
    config_id = test_database_config_apis(token, server_id)
    
    # 清理測試數據
    test_cleanup(token, server_id, config_id)
    
    print("=" * 50)
    print("API測試完成！")

if __name__ == "__main__":
    main()
