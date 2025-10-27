"""
資料庫配置功能測試腳本
"""
import requests
import json

# API 基礎 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_database_config_api():
    """測試資料庫配置API"""
    
    # 測試資料
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    test_server = {
        "server_name": "測試伺服器",
        "server_ip": "192.168.1.100",
        "server_port": 8080,
        "description": "測試用伺服器"
    }
    
    test_db_config = {
        "server_id": 1,  # 需要先創建伺服器
        "config_name": "測試資料庫",
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "mysql",
        "is_default": True
    }
    
    print("=== 資料庫配置API測試 ===")
    
    # 1. 創建使用者
    print("1. 創建測試使用者...")
    response = requests.post(f"{BASE_URL}/users/", json=test_user)
    if response.status_code == 200:
        print("✓ 使用者創建成功")
        user_data = response.json()
    else:
        print(f"✗ 使用者創建失敗: {response.text}")
        return
    
    # 2. 登入獲取token
    print("2. 使用者登入...")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("✓ 登入成功")
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"✗ 登入失敗: {response.text}")
        return
    
    # 3. 創建伺服器
    print("3. 創建測試伺服器...")
    response = requests.post(f"{BASE_URL}/servers/", json=test_server, headers=headers)
    if response.status_code == 200:
        print("✓ 伺服器創建成功")
        server_data = response.json()
        test_db_config["server_id"] = server_data["id"]
    else:
        print(f"✗ 伺服器創建失敗: {response.text}")
        return
    
    # 4. 創建資料庫配置
    print("4. 創建資料庫配置...")
    response = requests.post(f"{BASE_URL}/database-configs/servers/{test_db_config['server_id']}/configs/", 
                           json=test_db_config, headers=headers)
    if response.status_code == 200:
        print("✓ 資料庫配置創建成功")
        config_data = response.json()
    else:
        print(f"✗ 資料庫配置創建失敗: {response.text}")
        return
    
    # 5. 獲取伺服器的資料庫配置列表
    print("5. 獲取伺服器資料庫配置列表...")
    response = requests.get(f"{BASE_URL}/database-configs/servers/{test_db_config['server_id']}/configs/", 
                         headers=headers)
    if response.status_code == 200:
        print("✓ 獲取配置列表成功")
        configs = response.json()
        print(f"  配置數量: {configs['total']}")
    else:
        print(f"✗ 獲取配置列表失敗: {response.text}")
    
    # 6. 測試資料庫連接
    print("6. 測試資料庫連接...")
    response = requests.post(f"{BASE_URL}/database-configs/{config_data['id']}/test", 
                           headers=headers)
    if response.status_code == 200:
        test_result = response.json()
        print(f"✓ 連接測試完成: {test_result['message']}")
        if test_result['success']:
            print(f"  響應時間: {test_result['response_time_ms']}ms")
        else:
            print(f"  錯誤: {test_result['error_message']}")
    else:
        print(f"✗ 連接測試失敗: {response.text}")
    
    # 7. 測試不儲存的連接
    print("7. 測試不儲存的連接...")
    test_connection_data = {
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "mysql"
    }
    response = requests.post(f"{BASE_URL}/database-configs/test", 
                          json=test_connection_data, headers=headers)
    if response.status_code == 200:
        test_result = response.json()
        print(f"✓ 不儲存連接測試完成: {test_result['message']}")
    else:
        print(f"✗ 不儲存連接測試失敗: {response.text}")
    
    # 8. 更新資料庫配置
    print("8. 更新資料庫配置...")
    update_data = {
        "config_name": "更新後的測試資料庫",
        "is_default": False
    }
    response = requests.put(f"{BASE_URL}/database-configs/{config_data['id']}", 
                          json=update_data, headers=headers)
    if response.status_code == 200:
        print("✓ 資料庫配置更新成功")
    else:
        print(f"✗ 資料庫配置更新失敗: {response.text}")
    
    # 9. 獲取預設配置
    print("9. 獲取預設配置...")
    response = requests.get(f"{BASE_URL}/database-configs/servers/{test_db_config['server_id']}/configs/default", 
                         headers=headers)
    if response.status_code == 200:
        print("✓ 獲取預設配置成功")
    else:
        print(f"✗ 獲取預設配置失敗: {response.text}")
    
    # 10. 刪除資料庫配置
    print("10. 刪除資料庫配置...")
    response = requests.delete(f"{BASE_URL}/database-configs/{config_data['id']}", 
                            headers=headers)
    if response.status_code == 200:
        print("✓ 資料庫配置刪除成功")
    else:
        print(f"✗ 資料庫配置刪除失敗: {response.text}")
    
    # 11. 刪除伺服器
    print("11. 刪除測試伺服器...")
    response = requests.delete(f"{BASE_URL}/servers/{test_db_config['server_id']}", 
                            headers=headers)
    if response.status_code == 200:
        print("✓ 伺服器刪除成功")
    else:
        print(f"✗ 伺服器刪除失敗: {response.text}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_database_config_api()
