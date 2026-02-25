"""设置数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import SystemSetting
from app.core.cache import cache_manager

class SettingRepository(BaseRepository):
    """设置数据访问类，处理设置相关的数据访问"""
    
    def __init__(self, db):
        """初始化设置仓库
        
        Args:
            db: 数据库会话
        """
        super().__init__(db)
    

    
    # System Setting Methods
    def get_system_setting(self):
        """获取系统设置"""
        # 直接从数据库获取，不再使用 system_settings 缓存
        # 因为设置现在通过 settings 缓存统一管理
        setting = self.db.query(SystemSetting).first()
        return setting
    
    def create_or_update_system_setting(self, system_data):
        """创建或更新系统设置"""
        # 检查是否存在
        existing = self.db.query(SystemSetting).first()
        if existing:
            # 更新现有记录
            for key, value in system_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            # 不再更新 system_settings 缓存
            # 因为设置现在通过 settings 缓存统一管理
            return existing
        else:
            # 创建新记录
            # 先删除所有现有记录（如果有）
            self.db.query(SystemSetting).delete()
            # 创建新记录
            new_setting = SystemSetting(**system_data)
            self.db.add(new_setting)
            self.db.commit()
            # 不再更新 system_settings 缓存
            # 因为设置现在通过 settings 缓存统一管理
            return new_setting