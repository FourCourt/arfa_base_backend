# 數據庫模塊
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

# 創建數據庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    # MySQL 配置
    pool_pre_ping=True,  # 檢查連接是否有效
    echo=True,  # 顯示 SQL 語句（開發時有用）
    pool_recycle=300,  # 連接回收時間
    pool_size=10,  # 連接池大小
    max_overflow=20  # 最大溢出連接數
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 數據庫依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




