from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from app.models.database_config import DatabaseType, TestStatus, TestType, TestResult

def upgrade(op, Base):
    # 創建 servers 表
    op.create_table(
        'servers',
        Column('id', Integer, primary_key=True, index=True),
        Column('user_id', Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        Column('server_name', String(255), nullable=False, comment="伺服器名稱"),
        Column('server_ip', String(255), nullable=False, comment="伺服器IP地址"),
        Column('server_port', Integer, nullable=False, comment="伺服器端口"),
        Column('description', String(500), nullable=True, comment="伺服器描述"),
        Column('is_active', Boolean, default=True, comment="是否啟用"),
        Column('created_at', DateTime, default=func.now(), comment="創建時間"),
        Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), comment="更新時間")
    )
    
    # 創建 database_configs 表
    op.create_table(
        'database_configs',
        Column('id', Integer, primary_key=True, index=True),
        Column('user_id', Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        Column('server_id', Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True),
        Column('config_name', String(255), nullable=False, comment="配置名稱"),
        Column('host', String(255), nullable=False, comment="資料庫主機"),
        Column('port', Integer, nullable=False, comment="資料庫端口"),
        Column('database_name', String(255), nullable=False, comment="資料庫名稱"),
        Column('username', String(255), nullable=False, comment="使用者名稱"),
        Column('password_hash', String(255), nullable=False, comment="加密後的密碼"),
        Column('db_type', Enum(DatabaseType), nullable=False, comment="資料庫類型"),
        Column('connection_string', Text, nullable=True, comment="完整連接字串"),
        Column('is_active', Boolean, default=True, comment="是否啟用"),
        Column('is_default', Boolean, default=False, comment="是否為預設資料庫"),
        Column('last_tested_at', DateTime, nullable=True, comment="最後測試時間"),
        Column('test_status', Enum(TestStatus), default=TestStatus.NEVER_TESTED, comment="測試狀態"),
        Column('test_error_message', Text, nullable=True, comment="測試錯誤訊息"),
        Column('created_at', DateTime, default=func.now(), comment="創建時間"),
        Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), comment="更新時間")
    )
    op.create_index('idx_user_server', 'database_configs', ['user_id', 'server_id'])
    op.create_index('idx_server_active', 'database_configs', ['server_id', 'is_active'])
    op.create_index('idx_db_type', 'database_configs', ['db_type'])
    op.create_unique_constraint('unique_server_config_name', 'database_configs', ['server_id', 'config_name'])
    
    # 創建 connection_test_logs 表
    op.create_table(
        'connection_test_logs',
        Column('id', Integer, primary_key=True, index=True),
        Column('connection_id', Integer, ForeignKey("database_configs.id", ondelete="CASCADE"), nullable=False, index=True),
        Column('user_id', Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        Column('test_type', Enum(TestType), nullable=False, comment="測試類型"),
        Column('status', Enum(TestResult), nullable=False, comment="測試結果"),
        Column('response_time_ms', Integer, nullable=True, comment="響應時間(毫秒)"),
        Column('error_message', Text, nullable=True, comment="錯誤訊息"),
        Column('error_code', String(50), nullable=True, comment="錯誤代碼"),
        Column('tested_at', DateTime, default=func.now(), comment="測試時間")
    )
    op.create_index('idx_connection_id', 'connection_test_logs', ['connection_id'])
    op.create_index('idx_user_id', 'connection_test_logs', ['user_id'])
    op.create_index('idx_tested_at', 'connection_test_logs', ['tested_at'])
    op.create_index('idx_status', 'connection_test_logs', ['status'])

def downgrade(op, Base):
    # 刪除表（按相反順序）
    op.drop_table('connection_test_logs')
    op.drop_table('database_configs')
    op.drop_table('servers')