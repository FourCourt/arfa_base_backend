# Migration & Seeder 系統使用指南

## 🎯 概述

本項目實現了完整的 **Migration** 和 **Seeder** 系統，用於數據庫結構管理和初始數據填充。

## 🗄️ Migration 系統

### 什麼是 Migration？
Migration 是用於管理數據庫結構變更的版本控制系統，類似於 Git 但針對數據庫。

### Migration 文件位置
```
app/database/migrations/
├── __init__.py
├── base.py                    # 基礎 Migration 類
├── 001_create_migrations_table.py
└── 002_create_all_tables.py
```

### Migration 特性
- **版本控制**: 每個 migration 都有唯一版本號
- **可回滾**: 支持向下回滾
- **執行記錄**: 記錄已執行的 migrations
- **依賴管理**: 自動處理外鍵約束

## 🌱 Seeder 系統

### 什麼是 Seeder？
Seeder 是用於填充初始數據的系統，通常在數據庫表創建後執行。

### Seeder 文件位置
```
app/database/seeders/
├── __init__.py
├── base.py                           # 基礎 Seeder 類
├── 001_create_admin_role.py         # 創建管理員角色
├── 002_create_permissions.py        # 創建權限數據
├── 003_create_admin_user.py         # 創建管理員用戶
└── 004_assign_admin_permissions.py  # 分配管理員權限
```

### Seeder 特性
- **數據填充**: 自動填充初始數據
- **重複檢查**: 避免重複插入數據
- **可回滾**: 支持數據回滾
- **依賴管理**: 按順序執行

## 🚀 使用方法

### 1. 完整設置數據庫

```bash
# 執行所有 migrations 和 seeders
python migrate_and_seed.py
```

這會執行以下步驟：
1. 創建 migrations 表
2. 創建所有業務表
3. 創建管理員角色
4. 創建權限數據
5. 創建管理員用戶
6. 為管理員角色分配權限
7. 為管理員用戶分配角色

### 2. 創建新的 Migration

```python
# 在 app/database/migrations/ 目錄下創建新文件
# 例如: 003_add_new_table.py

from app.database.migrations.base import BaseMigration

class AddNewTable(BaseMigration):
    def __init__(self):
        super().__init__()
        self.version = "003"
        self.description = "Add new table"
    
    def up(self, db):
        """執行 migration"""
        sql = """
        CREATE TABLE new_table (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_sql(db, sql)
    
    def down(self, db):
        """回滾 migration"""
        sql = "DROP TABLE IF EXISTS new_table"
        self.execute_sql(db, sql)
```

### 3. 創建新的 Seeder

```python
# 在 app/database/seeders/ 目錄下創建新文件
# 例如: 005_create_sample_data.py

from app.database.seeders.base import BaseSeeder

class CreateSampleDataSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        self.name = "CreateSampleDataSeeder"
        self.description = "Create sample data"
    
    def run(self, db):
        """執行 seeder"""
        # 檢查數據是否已存在
        if self.record_exists(db, "items", {"title": "Sample Item"}):
            print("示例數據已存在，跳過創建")
            return
        
        # 創建示例數據
        sql = """
        INSERT INTO items (title, description, price, owner_id, created_at, updated_at)
        VALUES ('Sample Item', 'This is a sample item', 99.99, 1, NOW(), NOW())
        """
        self.execute_sql(db, sql)
        print("✅ 示例數據創建成功")
    
    def rollback(self, db):
        """回滾 seeder"""
        sql = "DELETE FROM items WHERE title = 'Sample Item'"
        self.execute_sql(db, sql)
        print("✅ 示例數據已刪除")
```

## 📊 數據庫結構

### 核心表結構

#### 1. 用戶表 (users)
```sql
- id: BIGINT (主鍵)
- username: VARCHAR(50) (唯一)
- email: VARCHAR(255)
- phone: VARCHAR(20)
- password_hash: VARBINARY(255)
- password_salt: VARBINARY(32)
- password_iters: SMALLINT
- status: TINYINT
- failed_login_count: TINYINT
- last_login_at: TIMESTAMP
- last_login_ip: VARBINARY(16)
- mfa_enabled: BOOLEAN
- password_reset_token: VARCHAR(255)
- password_reset_expires: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 2. 角色表 (roles)
```sql
- id: BIGINT (主鍵)
- code: VARCHAR(50) (唯一)
- name: VARCHAR(100)
- description: TEXT
- status: TINYINT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 3. 權限表 (permissions)
```sql
- id: BIGINT (主鍵)
- code: VARCHAR(50) (唯一)
- name: VARCHAR(100)
- description: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 4. 項目表 (items)
```sql
- id: BIGINT (主鍵)
- title: VARCHAR(255)
- description: TEXT
- price: DECIMAL(10,2)
- owner_id: BIGINT (外鍵 -> users.id)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 🔑 管理員帳號

### 預設管理員信息
- **用戶名**: `admin`
- **密碼**: `Admin123!@#`
- **郵箱**: `admin@arfa.com`
- **角色**: 系統管理員
- **權限**: 所有系統權限

### 權限列表
管理員擁有以下 23 個權限：

#### 用戶管理
- `user.create` - 創建用戶
- `user.read` - 查看用戶
- `user.update` - 更新用戶
- `user.delete` - 刪除用戶
- `user.manage` - 管理用戶

#### 項目管理
- `item.create` - 創建項目
- `item.read` - 查看項目
- `item.update` - 更新項目
- `item.delete` - 刪除項目
- `item.manage` - 管理項目

#### 角色管理
- `role.create` - 創建角色
- `role.read` - 查看角色
- `role.update` - 更新角色
- `role.delete` - 刪除角色
- `role.manage` - 管理角色

#### 權限管理
- `permission.create` - 創建權限
- `permission.read` - 查看權限
- `permission.update` - 更新權限
- `permission.delete` - 刪除權限
- `permission.manage` - 管理權限

#### 系統管理
- `system.admin` - 系統管理
- `system.logs` - 查看日誌
- `system.settings` - 系統設置

## 🛠️ 開發工作流

### 1. 添加新功能時
```bash
# 1. 創建新的 migration
# 2. 創建新的 seeder (如果需要初始數據)
# 3. 執行 migration 和 seeder
python migrate_and_seed.py
```

### 2. 團隊協作時
```bash
# 1. 拉取最新代碼
# 2. 執行 migrations
python migrate_and_seed.py
```

### 3. 生產環境部署時
```bash
# 1. 備份數據庫
# 2. 執行 migrations
python migrate_and_seed.py
# 3. 驗證數據完整性
```

## 🔍 故障排除

### 常見問題

#### 1. Migration 執行失敗
```bash
# 檢查數據庫連接
python test_mysql.py

# 檢查表結構
# 手動修復後重新執行
```

#### 2. Seeder 重複執行
- Seeder 系統會自動檢查數據是否存在
- 不會重複插入相同數據

#### 3. 外鍵約束錯誤
- 確保按正確順序創建表
- 檢查外鍵關係定義

### 重置數據庫
```bash
# 刪除所有表並重新創建
# 注意：這會丟失所有數據！
# 僅用於開發環境
```

## 📝 最佳實踐

### 1. Migration 命名
- 使用數字前綴：`001_`, `002_`, `003_`
- 描述性名稱：`create_users_table`, `add_email_index`

### 2. Seeder 順序
- 先創建基礎數據（角色、權限）
- 再創建依賴數據（用戶、項目）

### 3. 數據安全
- 生產環境使用強密碼
- 定期備份數據庫
- 測試環境與生產環境分離

### 4. 版本控制
- 將 migration 和 seeder 文件納入版本控制
- 團隊成員同步執行相同版本

## 🌐 API 測試

設置完成後，可以通過以下方式測試：

### 1. 健康檢查
```bash
curl http://localhost:8000/health
```

### 2. 管理員登入
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123!@#"
  }'
```

### 3. 查看 API 文檔
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

這個 Migration & Seeder 系統為你的 FastAPI 項目提供了完整的數據庫管理解決方案，確保數據庫結構的一致性和初始數據的完整性。


