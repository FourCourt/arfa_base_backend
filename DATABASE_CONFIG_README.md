# 資料庫配置管理功能

## 📋 功能概述

這個資料庫配置管理功能允許使用者為他們的伺服器配置多個資料庫連接，並提供連線測試功能。特別適用於金流平台，讓使用者可以將交易資料寫入到指定的資料庫中。

## 🏗️ 系統架構

### 資料表結構

#### 1. `servers` 表
- 儲存使用者的伺服器資訊
- 每個使用者可以有多個伺服器
- 支援伺服器名稱、IP、端口等基本資訊

#### 2. `database_configs` 表
- 儲存資料庫連接配置
- 每個伺服器可以有多個資料庫配置
- 支援 MySQL、PostgreSQL、SQLite 等資料庫類型
- 密碼加密儲存，支援預設配置設定

#### 3. `connection_test_logs` 表
- 記錄資料庫連接測試日誌
- 包含測試結果、響應時間、錯誤訊息等

## 🔧 API 端點

### 伺服器管理

```
POST   /api/v1/servers/                    # 創建伺服器
GET    /api/v1/servers/                    # 獲取伺服器列表
GET    /api/v1/servers/{server_id}         # 獲取特定伺服器
PUT    /api/v1/servers/{server_id}         # 更新伺服器
DELETE /api/v1/servers/{server_id}         # 刪除伺服器
```

### 資料庫配置管理

```
POST   /api/v1/database-configs/servers/{server_id}/configs/     # 創建資料庫配置
GET    /api/v1/database-configs/servers/{server_id}/configs/    # 獲取伺服器配置列表
GET    /api/v1/database-configs/                                # 獲取所有配置
GET    /api/v1/database-configs/{config_id}                     # 獲取特定配置
PUT    /api/v1/database-configs/{config_id}                     # 更新配置
DELETE /api/v1/database-configs/{config_id}                     # 刪除配置
```

### 連線測試

```
POST   /api/v1/database-configs/{config_id}/test               # 測試已儲存的配置
POST   /api/v1/database-configs/test                           # 測試新配置（不儲存）
GET    /api/v1/database-configs/servers/{server_id}/configs/default  # 獲取預設配置
```

## 📝 使用範例

### 1. 創建伺服器

```bash
curl -X POST "http://localhost:8000/api/v1/servers/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "生產環境伺服器",
    "server_ip": "192.168.1.100",
    "server_port": 8080,
    "description": "主要生產環境伺服器"
  }'
```

### 2. 創建資料庫配置

```bash
curl -X POST "http://localhost:8000/api/v1/database-configs/servers/1/configs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "config_name": "生產環境MySQL",
    "host": "192.168.1.100",
    "port": 3306,
    "database_name": "payment_db",
    "username": "dbuser",
    "password": "password123",
    "db_type": "mysql",
    "is_default": true
  }'
```

### 3. 測試資料庫連接

```bash
curl -X POST "http://localhost:8000/api/v1/database-configs/1/test" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 測試新配置（不儲存）

```bash
curl -X POST "http://localhost:8000/api/v1/database-configs/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.100",
    "port": 3306,
    "database_name": "test_db",
    "username": "testuser",
    "password": "testpass",
    "db_type": "mysql"
  }'
```

## 🔐 安全性特性

### 1. 權限控制
- 使用者只能管理自己的伺服器和資料庫配置
- JWT Token 認證保護所有端點
- 伺服器與使用者綁定驗證

### 2. 資料安全
- 密碼使用現有安全模組加密儲存
- 敏感資訊不在日誌中記錄
- 連接字串安全傳輸

### 3. 連線安全
- 連接超時設定（10秒）
- 自動斷線重連機制
- 詳細的錯誤訊息和代碼

## 📊 支援的資料庫類型

- **MySQL**: 使用 `pymysql` 驅動
- **PostgreSQL**: 使用 `psycopg2` 驅動  
- **SQLite**: 使用內建 `sqlite3` 模組

## 🚀 部署說明

### 1. 資料庫遷移

```bash
# 執行遷移
python migrate_and_seed.py
```

### 2. 安裝依賴

```bash
pip install pymysql psycopg2-binary
```

### 3. 啟動服務

```bash
# 開發環境
python run.py

# 或使用批次檔
start_dev.bat
```

## 🧪 測試

### 運行測試腳本

```bash
python test_database_config.py
```

### 測試覆蓋範圍

- 伺服器 CRUD 操作
- 資料庫配置 CRUD 操作
- 連線測試功能
- 權限驗證
- 錯誤處理

## 📈 監控和日誌

### 1. 連線監控
- 連線成功率統計
- 平均響應時間
- 錯誤類型分析

### 2. 寫入監控
- 交易寫入成功率
- 寫入延遲統計
- 失敗原因分析

### 3. 日誌記錄
- 連線測試日誌
- 交易寫入日誌
- 錯誤處理日誌

## 🔄 業務流程

### 金流交易寫入流程

1. **接收交易** → 第三方金流API回調
2. **驗證授權** → 檢查使用者授權是否有效
3. **選擇資料庫** → 根據配置選擇目標資料庫
4. **寫入記錄** → 將交易資料寫入指定資料庫
5. **狀態回報** → 回報交易處理結果

## 🛠️ 開發說明

### 檔案結構

```
app/
├── models/
│   ├── server.py                    # 伺服器模型
│   └── database_config.py          # 資料庫配置模型
├── services/
│   ├── server_service.py           # 伺服器服務層
│   └── database_config_service.py  # 資料庫配置服務層
├── controllers/
│   ├── server_controller.py        # 伺服器控制器
│   └── database_config_controller.py # 資料庫配置控制器
└── api/endpoints/
    ├── servers.py                  # 伺服器API端點
    └── database_configs.py         # 資料庫配置API端點
```

### 擴展功能

- 支援更多資料庫類型
- 連接池管理
- 自動故障轉移
- 資料庫健康檢查
- 交易寫入API

## 📞 支援

如有問題或建議，請聯繫開發團隊。
