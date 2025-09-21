# PostgreSQL 設置指南

## 1. 安裝 PostgreSQL

### 下載和安裝
1. 前往 [PostgreSQL 官網](https://www.postgresql.org/download/windows/)
2. 下載 PostgreSQL 安裝程序
3. 運行安裝程序，記住設置的密碼

### 或者使用 XAMPP
如果你已經有 XAMPP，可以：
1. 打開 XAMPP 控制面板
2. 啟動 PostgreSQL 服務（如果有的話）

## 2. 創建數據庫

### 使用 pgAdmin（圖形界面）
1. 打開 pgAdmin
2. 連接到 PostgreSQL 服務器
3. 右鍵點擊 "Databases" → "Create" → "Database"
4. 數據庫名稱：`arfa_db`

### 使用命令行
```bash
# 連接到 PostgreSQL
psql -U postgres

# 創建數據庫
CREATE DATABASE arfa_db;

# 創建用戶（可選）
CREATE USER arfa_user WITH PASSWORD 'your_password';

# 授予權限
GRANT ALL PRIVILEGES ON DATABASE arfa_db TO arfa_user;

# 退出
\q
```

## 3. 配置連接字符串

在項目根目錄創建 `.env` 文件：

```env
# PostgreSQL 數據庫配置
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/arfa_db

# 或者使用自定義用戶
# DATABASE_URL=postgresql://arfa_user:your_password@localhost:5432/arfa_db
```

## 4. 安裝 Python 依賴

```bash
pip install asyncpg
```

## 5. 創建數據表

```bash
python create_tables.py
```

## 6. 啟動服務器

```bash
python run.py
```

## 常見問題

### 連接被拒絕
- 確保 PostgreSQL 服務正在運行
- 檢查防火牆設置
- 確認端口 5432 沒有被其他程序佔用

### 認證失敗
- 檢查用戶名和密碼
- 確認用戶有數據庫權限

### 數據庫不存在
- 確保已創建 `arfa_db` 數據庫
- 檢查數據庫名稱拼寫

