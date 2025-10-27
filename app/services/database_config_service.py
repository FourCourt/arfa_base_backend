from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet
import base64
import time
import logging
from app.models.database_config import (
    DatabaseConfig, DatabaseConfigCreate, DatabaseConfigUpdate, 
    DatabaseType, TestStatus, TestType, TestResult, ConnectionTestLog
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

class DatabaseConfigService(BaseService[DatabaseConfig]):
    """資料庫配置服務"""
    
    def __init__(self):
        super().__init__(DatabaseConfig)
        # 生成加密密鑰（實際應用中應該從環境變數或配置文件中讀取）
        # 這裡為了演示方便直接生成，實際應保持一致
        self.encryption_key = Fernet.generate_key() 
        self.cipher_suite = Fernet(self.encryption_key)
    
    def create_config(self, db: Session, user_id: int, config_data: DatabaseConfigCreate) -> DatabaseConfig:
        """創建資料庫配置"""
        # 檢查配置名稱是否已存在於該伺服器下
        existing_config = db.query(DatabaseConfig).filter(
            and_(DatabaseConfig.server_id == config_data.server_id, 
                 DatabaseConfig.config_name == config_data.config_name)
        ).first()
        if existing_config:
            raise ValueError("配置名稱已存在於該伺服器下")
        
        # 加密密碼
        encrypted_password = self._encrypt_password(config_data.password)
        
        # 如果設為預設，先取消其他配置的預設狀態
        if config_data.is_default:
            db.query(DatabaseConfig).filter(
                and_(DatabaseConfig.server_id == config_data.server_id, 
                     DatabaseConfig.is_default == True)
            ).update({"is_default": False})
        
        config_dict = config_data.dict()
        config_dict.pop('password')  # 移除原始密碼
        config_dict['password_hash'] = encrypted_password
        
        config = self.create(db, user_id=user_id, **config_dict)
        return config
    
    def get_user_configs(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DatabaseConfig]:
        """獲取使用者所有資料庫配置"""
        return db.query(DatabaseConfig).filter(DatabaseConfig.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_server_configs(self, db: Session, server_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[DatabaseConfig]:
        """獲取指定伺服器的資料庫配置"""
        return db.query(DatabaseConfig).filter(
            and_(DatabaseConfig.server_id == server_id, DatabaseConfig.user_id == user_id)
        ).offset(skip).limit(limit).all()
    
    def get_config_by_id(self, db: Session, config_id: int, user_id: int) -> Optional[DatabaseConfig]:
        """根據ID獲取資料庫配置，並驗證使用者權限"""
        return db.query(DatabaseConfig).filter(
            and_(DatabaseConfig.id == config_id, DatabaseConfig.user_id == user_id)
        ).first()
    
    def update_config(self, db: Session, config_id: int, user_id: int, update_data: DatabaseConfigUpdate) -> Optional[DatabaseConfig]:
        """更新資料庫配置"""
        config = self.get_config_by_id(db, config_id, user_id)
        if not config:
            return None
        
        # 檢查更新後的配置名稱是否與其他配置衝突
        if update_data.config_name and update_data.config_name != config.config_name:
            existing_config = db.query(DatabaseConfig).filter(
                and_(DatabaseConfig.server_id == config.server_id, 
                     DatabaseConfig.config_name == update_data.config_name, 
                     DatabaseConfig.id != config_id)
            ).first()
            if existing_config:
                raise ValueError("配置名稱已存在於該伺服器下")
        
        # 如果設為預設，先取消其他配置的預設狀態
        if update_data.is_default:
            db.query(DatabaseConfig).filter(
                and_(DatabaseConfig.server_id == config.server_id, 
                     DatabaseConfig.is_default == True,
                     DatabaseConfig.id != config_id)
            ).update({"is_default": False})
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # 如果有新密碼，需要加密
        if 'password' in update_dict:
            update_dict['password_hash'] = self._encrypt_password(update_dict['password'])
            update_dict.pop('password')
        
        updated_config = self.update(db, config_id, **update_dict)
        return updated_config
    
    def delete_config(self, db: Session, config_id: int, user_id: int) -> bool:
        """刪除資料庫配置"""
        config = self.get_config_by_id(db, config_id, user_id)
        if not config:
            return False
        return self.delete(db, config_id)
    
    def get_default_config(self, db: Session, server_id: int, user_id: int) -> Optional[DatabaseConfig]:
        """獲取指定伺服器的預設資料庫配置"""
        return db.query(DatabaseConfig).filter(
            and_(DatabaseConfig.server_id == server_id, 
                 DatabaseConfig.user_id == user_id,
                 DatabaseConfig.is_default == True)
        ).first()
    
    def test_connection(self, db: Session, config_id: int, user_id: int) -> Dict[str, Any]:
        """測試資料庫連接（保存結果）"""
        config = self.get_config_by_id(db, config_id, user_id)
        if not config:
            raise ValueError("配置不存在或無權限訪問")
        
        # 解密密碼
        decrypted_password = self._decrypt_password(config.password_hash)
        
        # 測試連接
        test_result = self._test_database_connection(
            config.host, config.port, config.database_name, 
            config.username, decrypted_password, config.db_type
        )
        
        # 更新配置的測試狀態
        config.test_status = TestStatus.SUCCESS if test_result['success'] else TestStatus.FAILED
        config.last_tested_at = test_result['tested_at']
        config.test_error_message = test_result.get('error_message')
        
        # 記錄測試日誌
        self._log_test_result(db, config_id, user_id, TestType.CONNECTION, test_result)
        
        db.commit()
        
        return test_result
    
    def test_connection_without_save(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """測試資料庫連接（不保存結果）"""
        return self._test_database_connection(
            test_data['host'], test_data['port'], test_data['database_name'],
            test_data['username'], test_data['password'], test_data['db_type']
        )
    
    def _encrypt_password(self, password: str) -> str:
        """加密密碼"""
        password_bytes = password.encode('utf-8')
        encrypted_password = self.cipher_suite.encrypt(password_bytes)
        return base64.b64encode(encrypted_password).decode('utf-8')
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """解密密碼"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
            decrypted_password = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_password.decode('utf-8')
        except Exception as e:
            logger.error(f"解密密碼失敗: {str(e)}")
            return ""
    
    def _test_database_connection(self, host: str, port: int, database_name: str, 
                                 username: str, password: str, db_type: DatabaseType) -> Dict[str, Any]:
        """測試資料庫連接"""
        start_time = time.time()
        
        try:
            # 根據資料庫類型構建連接字串
            if db_type == DatabaseType.MYSQL:
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
            elif db_type == DatabaseType.POSTGRESQL:
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
            elif db_type == DatabaseType.SQLITE:
                connection_string = f"sqlite:///{database_name}"
            else:
                raise ValueError(f"不支援的資料庫類型: {db_type}")
            
            # 創建引擎並測試連接
            engine = create_engine(connection_string, pool_pre_ping=True)
            
            with engine.connect() as connection:
                # 執行簡單查詢測試連接
                if db_type == DatabaseType.SQLITE:
                    connection.execute("SELECT 1")
                else:
                    connection.execute("SELECT 1")
            
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                'success': True,
                'message': '連接測試成功',
                'response_time_ms': response_time,
                'tested_at': time.time(),
                'error_message': None,
                'error_code': None
            }
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            error_message = str(e)
            error_code = type(e).__name__
            
            logger.error(f"資料庫連接測試失敗: {error_message}")
            
            return {
                'success': False,
                'message': '連接測試失敗',
                'response_time_ms': response_time,
                'tested_at': time.time(),
                'error_message': error_message,
                'error_code': error_code
            }
    
    def _log_test_result(self, db: Session, config_id: int, user_id: int, 
                        test_type: TestType, test_result: Dict[str, Any]):
        """記錄測試結果"""
        test_log = ConnectionTestLog(
            connection_id=config_id,
            user_id=user_id,
            test_type=test_type,
            status=TestResult.SUCCESS if test_result['success'] else TestResult.FAILED,
            response_time_ms=test_result.get('response_time_ms'),
            error_message=test_result.get('error_message'),
            error_code=test_result.get('error_code')
        )
        
        db.add(test_log)
        db.commit()
