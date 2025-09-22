# ARFA API 部署指南

## 環境配置

### 開發環境 (本地 - XAMPP MySQL)
```bash
# 設置環境變量
export ENVIRONMENT=development

# 或創建 .env 文件
echo "ENVIRONMENT=development" > .env
```

### 生產環境 (服務器 - PostgreSQL)
```bash
# 設置環境變量
export ENVIRONMENT=production

# 或創建 .env 文件
echo "ENVIRONMENT=production" > .env
```

## 開發環境設置

### 1. 本地開發 (XAMPP)
```bash
# 啟動 XAMPP
# 確保 MySQL 服務運行

# 創建數據庫
python create_database.py

# 創建數據表
python create_tables.py

# 啟動開發服務器
python run.py
```

### 2. 配置說明
- **數據庫**: XAMPP MySQL (localhost:3306)
- **數據庫名**: arfa_db
- **用戶名**: root
- **密碼**: (空)
- **驅動**: PyMySQL

## 生產環境部署

### 1. 服務器準備
```bash
# 安裝 Python 3.8+
sudo apt update
sudo apt install python3 python3-pip

# 安裝 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 創建數據庫和用戶
sudo -u postgres psql
```

### 2. PostgreSQL 設置
```sql
-- 創建數據庫
CREATE DATABASE arfa_db;

-- 創建用戶
CREATE USER arfa_user WITH PASSWORD 'your_secure_password';

-- 授予權限
GRANT ALL PRIVILEGES ON DATABASE arfa_db TO arfa_user;
ALTER USER arfa_user CREATEDB;
```

### 3. 環境變量設置
```bash
# 設置生產環境
export ENVIRONMENT=production

# 設置數據庫連接 (可選，會覆蓋默認配置)
export DATABASE_URL=postgresql://arfa_user:your_secure_password@localhost:5432/arfa_db

# 設置安全密鑰
export SECRET_KEY=your-super-secure-secret-key-here

# 設置 CORS 來源
export BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 安裝依賴
```bash
# 安裝所有依賴 (包括 PostgreSQL 驅動)
pip install -r requirements.txt
```

### 5. 數據庫遷移
```bash
# 創建數據表
python create_tables.py
```

### 6. 啟動服務
```bash
# 開發模式
python run.py

# 生產模式 (使用 gunicorn)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker 部署 (可選)

### 1. 創建 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2. 創建 docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://arfa_user:password@db:5432/arfa_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=arfa_db
      - POSTGRES_USER=arfa_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. 啟動 Docker 服務
```bash
docker-compose up -d
```

## 環境切換

### 快速切換腳本

#### 開發環境
```bash
# start_dev.sh
#!/bin/bash
export ENVIRONMENT=development
python run.py
```

#### 生產環境
```bash
# start_prod.sh
#!/bin/bash
export ENVIRONMENT=production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 監控和日誌

### 1. 日誌配置
```python
# 在 app/core/config.py 中添加
LOG_LEVEL: str = "INFO" if is_production() else "DEBUG"
```

### 2. 健康檢查
```bash
# 檢查服務狀態
curl http://localhost:8000/health

# 檢查數據庫連接
curl http://localhost:8000/api/v1/users/
```

## 常見問題

### 1. 數據庫連接失敗
- 檢查數據庫服務是否運行
- 確認連接字符串正確
- 檢查防火牆設置

### 2. 環境變量不生效
- 確認環境變量已設置
- 重啟應用程序
- 檢查 .env 文件位置

### 3. CORS 錯誤
- 檢查 BACKEND_CORS_ORIGINS 設置
- 確認前端域名正確

## 安全建議

1. **生產環境**:
   - 使用強密碼
   - 設置 HTTPS
   - 限制 CORS 來源
   - 定期更新依賴

2. **數據庫**:
   - 定期備份
   - 設置適當的權限
   - 監控連接數

3. **服務器**:
   - 設置防火牆
   - 使用 SSL 證書
   - 監控系統資源


