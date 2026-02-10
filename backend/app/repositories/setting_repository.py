"""设置数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import SystemSetting, VectorSetting
from app.core.memory_database import memory_db

class SettingRepository(BaseRepository):
    """设置数据访问类，处理设置相关的数据访问"""
    
    # Vector Setting Methods
    def get_vector_setting(self):
        """获取向量设置"""
        # 从内存数据库获取
        setting = memory_db.get('vector_settings')
        if setting:
            return setting
        
        # 如果内存中没有，从数据库获取并同步到内存
        setting = self.db.query(VectorSetting).first()
        if setting:
            memory_db.set('vector_settings', setting)
        return setting
    
    def create_or_update_vector_setting(self, vector_data):
        """创建或更新向量设置"""
        # 使用内存数据库的create_or_update方法
        return memory_db.create_or_update('vector_settings', vector_data)
    
    # System Setting Methods
    def get_system_setting(self):
        """获取系统设置"""
        # 从内存数据库获取
        setting = memory_db.get('system_settings')
        if setting:
            return setting
        
        # 如果内存中没有，从数据库获取并同步到内存
        setting = self.db.query(SystemSetting).first()
        if setting:
            memory_db.set('system_settings', setting)
        return setting
    
    def create_or_update_system_setting(self, system_data):
        """创建或更新系统设置"""
        # 使用内存数据库的create_or_update方法
        return memory_db.create_or_update('system_settings', system_data)
