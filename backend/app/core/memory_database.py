"""内存数据库管理类"""
from typing import Dict, Any, Optional
from app.core.database import SessionLocal
from app.models.database.models import SystemSetting, AppSetting, VectorSetting, NotificationSetting

class MemoryDatabaseManager:
    """内存数据库管理器，实现内存与SQLite的同步"""
    _instance = None
    _memory_data = None
    _db = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化内存数据库"""
        if MemoryDatabaseManager._instance is not None:
            raise Exception("内存数据库管理器是单例模式，请使用get_instance()方法获取实例")
        
        MemoryDatabaseManager._instance = self
        self._db = SessionLocal()
        self._memory_data = {
            'system_settings': None,
            'app_settings': None,
            'vector_settings': None,
            'notification_settings': None
        }
        
        # 初始化时从SQLite加载数据到内存
        self.load_from_database()
    
    def load_from_database(self):
        """从SQLite数据库加载数据到内存"""
        try:
            # 加载系统设置
            system_setting = self._db.query(SystemSetting).first()
            if system_setting:
                self._memory_data['system_settings'] = system_setting
            
            # 加载应用设置
            app_setting = self._db.query(AppSetting).first()
            if app_setting:
                self._memory_data['app_settings'] = app_setting
            
            # 加载向量设置
            vector_setting = self._db.query(VectorSetting).first()
            if vector_setting:
                self._memory_data['vector_settings'] = vector_setting
            
            # 加载通知设置
            notification_setting = self._db.query(NotificationSetting).first()
            if notification_setting:
                self._memory_data['notification_settings'] = notification_setting
        except Exception as e:
            print(f"从数据库加载数据失败: {e}")
    
    def save_to_database(self, model_type: str, data: Any):
        """将内存数据保存到SQLite数据库"""
        try:
            if model_type == 'system_settings':
                existing = self._db.query(SystemSetting).first()
                if existing:
                    # 更新现有记录
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    self._db.commit()
                    self._db.refresh(existing)
                    return existing
                else:
                    # 创建新记录
                    new_setting = SystemSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    self._db.commit()
                    self._db.refresh(new_setting)
                    return new_setting
            
            elif model_type == 'app_settings':
                existing = self._db.query(AppSetting).first()
                if existing:
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    self._db.commit()
                    self._db.refresh(existing)
                    return existing
                else:
                    new_setting = AppSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    self._db.commit()
                    self._db.refresh(new_setting)
                    return new_setting
            
            elif model_type == 'vector_settings':
                existing = self._db.query(VectorSetting).first()
                if existing:
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    self._db.commit()
                    self._db.refresh(existing)
                    return existing
                else:
                    new_setting = VectorSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    self._db.commit()
                    self._db.refresh(new_setting)
                    return new_setting
            
            elif model_type == 'notification_settings':
                existing = self._db.query(NotificationSetting).first()
                if existing:
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    self._db.commit()
                    self._db.refresh(existing)
                    return existing
                else:
                    new_setting = NotificationSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    self._db.commit()
                    self._db.refresh(new_setting)
                    return new_setting
            
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
            self._db.rollback()
            return None
    
    def get(self, model_type: str) -> Optional[Any]:
        """从内存数据库获取数据"""
        return self._memory_data.get(model_type)
    
    def set(self, model_type: str, data: Any) -> bool:
        """设置内存数据库数据并同步到SQLite"""
        try:
            # 更新内存数据
            self._memory_data[model_type] = data
            
            # 同步到SQLite
            result = self.save_to_database(model_type, data)
            return result is not None
        except Exception as e:
            print(f"设置内存数据库数据失败: {e}")
            return False
    
    def update(self, model_type: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新内存数据库数据并同步到SQLite"""
        try:
            # 获取现有数据
            existing_data = self._memory_data.get(model_type)
            if not existing_data:
                return None
            
            # 更新内存数据
            for key, value in updates.items():
                if hasattr(existing_data, key):
                    setattr(existing_data, key, value)
            
            # 同步到SQLite
            result = self.save_to_database(model_type, existing_data)
            return result
        except Exception as e:
            print(f"更新内存数据库数据失败: {e}")
            return None
    
    def create_or_update(self, model_type: str, data: Dict[str, Any]) -> Any:
        """创建或更新数据"""
        try:
            # 检查内存中是否已有数据
            existing_data = self._memory_data.get(model_type)
            
            if existing_data:
                # 更新现有数据
                for key, value in data.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, existing_data)
                return result
            else:
                # 创建新数据
                if model_type == 'system_settings':
                    new_data = SystemSetting(**data)
                elif model_type == 'app_settings':
                    new_data = AppSetting(**data)
                elif model_type == 'vector_settings':
                    new_data = VectorSetting(**data)
                elif model_type == 'notification_settings':
                    new_data = NotificationSetting(**data)
                else:
                    return None
                
                # 保存到内存
                self._memory_data[model_type] = new_data
                
                # 同步到SQLite
                result = self.save_to_database(model_type, new_data)
                return result
        except Exception as e:
            print(f"创建或更新数据失败: {e}")
            return None
    
    def refresh(self, model_type: str) -> bool:
        """从SQLite刷新内存数据"""
        try:
            if model_type == 'system_settings':
                data = self._db.query(SystemSetting).first()
            elif model_type == 'app_settings':
                data = self._db.query(AppSetting).first()
            elif model_type == 'vector_settings':
                data = self._db.query(VectorSetting).first()
            elif model_type == 'notification_settings':
                data = self._db.query(NotificationSetting).first()
            else:
                return False
            
            if data:
                self._memory_data[model_type] = data
                return True
            return False
        except Exception as e:
            print(f"刷新内存数据失败: {e}")
            return False

# 创建全局内存数据库实例
memory_db = MemoryDatabaseManager.get_instance()