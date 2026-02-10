"""设置数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import SystemSetting, AppSetting, VectorSetting

class SettingRepository(BaseRepository):
    """设置数据访问类，处理设置相关的数据访问"""
    
    # Vector Setting Methods
    def get_vector_setting(self):
        """获取向量设置"""
        return self.db.query(VectorSetting).first()
    
    def create_or_update_vector_setting(self, vector_data):
        """创建或更新向量设置"""
        existing_setting = self.get_vector_setting()
        if existing_setting:
            # 更新现有设置
            for key, value in vector_data.items():
                setattr(existing_setting, key, value)
            return self.update(existing_setting)
        else:
            # 创建新设置
            new_setting = VectorSetting(**vector_data)
            return self.add(new_setting)
    

    
    # App Setting Methods
    def get_app_setting(self):
        """获取应用设置"""
        return self.db.query(AppSetting).first()
    
    def create_or_update_app_setting(self, app_data):
        """创建或更新应用设置"""
        existing_setting = self.get_app_setting()
        if existing_setting:
            # 更新现有设置
            for key, value in app_data.items():
                setattr(existing_setting, key, value)
            return self.update(existing_setting)
        else:
            # 创建新设置
            new_setting = AppSetting(**app_data)
            return self.add(new_setting)
    
    # System Setting Methods
    def get_system_setting(self):
        """获取系统设置"""
        return self.db.query(SystemSetting).first()
    
    def create_or_update_system_setting(self, system_data):
        """创建或更新系统设置"""
        existing_setting = self.get_system_setting()
        if existing_setting:
            # 更新现有设置
            for key, value in system_data.items():
                setattr(existing_setting, key, value)
            return self.update(existing_setting)
        else:
            # 创建新设置
            new_setting = SystemSetting(**system_data)
            return self.add(new_setting)
