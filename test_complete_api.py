"""
完整的資料庫配置API測試
"""
import requests
import json

# API 基礎 URL
BASE_URL = "http://localhost:8001/api/v1"

def test_all_apis():
    """測試所有API功能"""
    
    print("=== 完整API測試 ===")
    
    # 1. 登入獲取token
    print("1. 管理員登入...")
    login_data = {
        "username": "admin",
        "password": "Admin123!@#"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("OK 登入成功")
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"ERROR 登入失敗: {response.text}")
        return
    
    # 2. 創建測試使用者
    print("2. 創建測試使用者...")
    import time
    timestamp = int(time.time())
    test_user = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "Test123!@#"
    }
    response = requests.post(f"{BASE_URL}/users/", json=test_user)
    if response.status_code == 200:
        print("OK 測試使用者創建成功")
        user_data = response.json()
    else:
        print(f"ERROR 測試使用者創建失敗: {response.text}")
        return
    
    # 3. 測試使用者登入
    print("3. 測試使用者登入...")
    test_login = {
        "username": "testuser",
        "password": "Test123!@#"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=test_login)
    if response.status_code == 200:
        print("OK 測試使用者登入成功")
        test_token = response.json()["access_token"]
        test_headers = {"Authorization": f"Bearer {test_token}"}
    else:
        print(f"ERROR 測試使用者登入失敗: {response.text}")
        return
    
    # 4. 創建伺服器
    print("4. 創建測試伺服器...")
    test_server = {
        "server_name": "測試伺服器",
        "server_ip": "192.168.1.100",
        "server_port": 8080,
        "description": "測試用伺服器"
    }
    response = requests.post(f"{BASE_URL}/servers/", json=test_server, headers=test_headers)
    if response.status_code == 200:
        print("OK 伺服器創建成功")
        server_data = response.json()
        server_id = server_data["id"]
    else:
        print(f"ERROR 伺服器創建失敗: {response.text}")
        return
    
    # 5. 獲取伺服器列表
    print("5. 獲取伺服器列表...")
    response = requests.get(f"{BASE_URL}/servers/", headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取伺服器列表成功")
        servers = response.json()
        print(f"  伺服器數量: {len(servers)}")
    else:
        print(f"ERROR 獲取伺服器列表失敗: {response.text}")
    
    # 6. 創建資料庫配置
    print("6. 創建資料庫配置...")
    test_db_config = {
        "server_id": server_id,
        "config_name": "測試資料庫",
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "mysql",
        "is_default": True
    }
    
    response = requests.post(f"{BASE_URL}/database-configs/servers/{server_id}/configs/", 
                           json=test_db_config, headers=test_headers)
    if response.status_code == 200:
        print("OK 資料庫配置創建成功")
        config_data = response.json()
        config_id = config_data["id"]
    else:
        print(f"ERROR 資料庫配置創建失敗: {response.text}")
        return
    
    # 7. 獲取伺服器的資料庫配置列表
    print("7. 獲取伺服器資料庫配置列表...")
    response = requests.get(f"{BASE_URL}/database-configs/servers/{server_id}/configs/", 
                         headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取配置列表成功")
        configs = response.json()
        print(f"  配置數量: {configs['total']}")
    else:
        print(f"ERROR 獲取配置列表失敗: {response.text}")
    
    # 8. 獲取所有資料庫配置
    print("8. 獲取所有資料庫配置...")
    response = requests.get(f"{BASE_URL}/database-configs/", headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取所有配置成功")
        all_configs = response.json()
        print(f"  總配置數量: {all_configs['total']}")
    else:
        print(f"ERROR 獲取所有配置失敗: {response.text}")
    
    # 9. 獲取特定配置
    print("9. 獲取特定配置...")
    response = requests.get(f"{BASE_URL}/database-configs/{config_id}", headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取特定配置成功")
        specific_config = response.json()
        print(f"  配置名稱: {specific_config['config_name']}")
    else:
        print(f"ERROR 獲取特定配置失敗: {response.text}")
    
    # 10. 測試資料庫連接
    print("10. 測試資料庫連接...")
    response = requests.post(f"{BASE_URL}/database-configs/{config_id}/test", 
                           headers=test_headers)
    if response.status_code == 200:
        test_result = response.json()
        print(f"OK 連接測試完成: {test_result['message']}")
        if test_result['success']:
            print(f"  響應時間: {test_result['response_time_ms']}ms")
        else:
            print(f"  錯誤: {test_result['error_message']}")
    else:
        print(f"ERROR 連接測試失敗: {response.text}")
    
    # 11. 測試不儲存的連接
    print("11. 測試不儲存的連接...")
    test_connection_data = {
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "root",
        "password": "password",
        "db_type": "mysql"
    }
    response = requests.post(f"{BASE_URL}/database-configs/test", 
                          json=test_connection_data, headers=test_headers)
    if response.status_code == 200:
        test_result = response.json()
        print(f"OK 不儲存連接測試完成: {test_result['message']}")
    else:
        print(f"ERROR 不儲存連接測試失敗: {response.text}")
    
    # 12. 更新資料庫配置
    print("12. 更新資料庫配置...")
    update_data = {
        "config_name": "更新後的測試資料庫",
        "is_default": False
    }
    response = requests.put(f"{BASE_URL}/database-configs/{config_id}", 
                          json=update_data, headers=test_headers)
    if response.status_code == 200:
        print("OK 資料庫配置更新成功")
    else:
        print(f"ERROR 資料庫配置更新失敗: {response.text}")
    
    # 13. 獲取預設配置
    print("13. 獲取預設配置...")
    response = requests.get(f"{BASE_URL}/database-configs/servers/{server_id}/configs/default", 
                         headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取預設配置成功")
    else:
        print(f"ERROR 獲取預設配置失敗: {response.text}")
    
    # 14. 更新伺服器
    print("14. 更新伺服器...")
    server_update = {
        "server_name": "更新後的測試伺服器",
        "description": "更新後的描述"
    }
    response = requests.put(f"{BASE_URL}/servers/{server_id}", 
                          json=server_update, headers=test_headers)
    if response.status_code == 200:
        print("OK 伺服器更新成功")
    else:
        print(f"ERROR 伺服器更新失敗: {response.text}")
    
    # 15. 獲取特定伺服器
    print("15. 獲取特定伺服器...")
    response = requests.get(f"{BASE_URL}/servers/{server_id}", headers=test_headers)
    if response.status_code == 200:
        print("OK 獲取特定伺服器成功")
        server_info = response.json()
        print(f"  伺服器名稱: {server_info['server_name']}")
    else:
        print(f"ERROR 獲取特定伺服器失敗: {response.text}")
    
    # 16. 刪除資料庫配置
    print("16. 刪除資料庫配置...")
    response = requests.delete(f"{BASE_URL}/database-configs/{config_id}", 
                            headers=test_headers)
    if response.status_code == 200:
        print("OK 資料庫配置刪除成功")
    else:
        print(f"ERROR 資料庫配置刪除失敗: {response.text}")
    
    # 17. 刪除伺服器
    print("17. 刪除測試伺服器...")
    response = requests.delete(f"{BASE_URL}/servers/{server_id}", 
                            headers=test_headers)
    if response.status_code == 200:
        print("OK 伺服器刪除成功")
    else:
        print(f"ERROR 伺服器刪除失敗: {response.text}")
    
    # 18. 刪除測試使用者
    print("18. 刪除測試使用者...")
    response = requests.delete(f"{BASE_URL}/users/{user_data['id']}", 
                            headers=headers)
    if response.status_code == 200:
        print("OK 測試使用者刪除成功")
    else:
        print(f"ERROR 測試使用者刪除失敗: {response.text}")
    
    print("\n=== 測試完成 ===")
    print("所有API功能測試完成！")

if __name__ == "__main__":
    try:
        test_all_apis()
    except requests.exceptions.ConnectionError:
        print("ERROR 無法連接到服務器，請確保服務正在運行")
    except Exception as e:
        print(f"ERROR 測試過程中發生錯誤: {str(e)}")
