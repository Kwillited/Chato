"""设置相关业务逻辑服务"""
from app.services.data_service import DataService
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
import json
from app.utils.data import NamingUtils
from app.utils.logging_utils import LoggingUtils
from app.core.memory_cache import MemoryCache

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    def __init__(self, setting_repo=None, memory_cache=None):
        """初始化设置服务
        
        Args:
            setting_repo: 设置仓库实例，用于依赖注入
            memory_cache: 内存缓存实例，用于依赖注入
        """
        self.setting_repo = setting_repo or SettingRepository()
        self.memory_cache = memory_cache or MemoryCache()
    
    def convert_dict_keys(self, data_dict):
        """将字典的所有键从驼峰命名转换为蛇形命名
        
        Args:
            data_dict: 包含驼峰命名键的字典
            
        Returns:
            包含蛇形命名键的字典
        """
        return NamingUtils.convert_dict_keys(data_dict)
    
    def get_basic_settings(self):
        """获取基本设置"""
        # 从内存缓存获取系统设置
        system_setting = self.setting_repo.get_system_setting()
        if system_setting:
            return {
                'theme': 'dark' if system_setting.dark_mode else 'light',
                'autoSave': True,  # 默认值
                'showPreview': True,  # 默认值
                'maxMessages': 100  # 默认值
            }
        else:
            # 返回默认值
            return {
                'theme': 'light',
                'autoSave': True,
                'showPreview': True,
                'maxMessages': 100
            }
    
    def save_basic_settings(self, data):
        """保存基本设置"""
        # 将驼峰命名转换为蛇形命名
        snake_data = self.convert_dict_keys(data)
        
        # 构建系统设置数据
        system_data = {
            'dark_mode': (data.get('theme') == 'dark'),
            'streaming_enabled': True,
            'chat_style': 'bubble',
            'view_mode': 'grid',
            'default_model': "",
            'new_message': True,
            'sound': False,
            'system': True,
            'display_time': '5秒'
        }
        
        # 保存设置
        self.setting_repo.create_or_update_system_setting(system_data)
        
        # 返回更新后的设置
        return self.get_basic_settings()
    
    def get_system_setting(self):
        """获取系统设置（包含通知设置）"""
        # 从设置仓库获取系统设置
        system_setting = self.setting_repo.get_system_setting()
        if system_setting:
            return {
                'dark_mode': system_setting.dark_mode,
                'streaming_enabled': system_setting.streaming_enabled,
                'chat_style': system_setting.chat_style,
                'view_mode': system_setting.view_mode,
                'default_model': system_setting.default_model,
                # 通知相关字段
                'newMessage': system_setting.new_message,
                'sound': system_setting.sound,
                'system': system_setting.system,
                'displayTime': system_setting.display_time
            }
        else:
            # 返回默认值
            return {
                'dark_mode': False,
                'streaming_enabled': True,
                'chat_style': 'bubble',
                'view_mode': 'grid',
                'default_model': "",
                # 通知相关默认值
                'newMessage': True,
                'sound': False,
                'system': True,
                'displayTime': '5秒'
            }
    
    def save_system_setting(self, data):
        """保存系统设置（包含通知设置）"""
        # 将驼峰命名转换为蛇形命名
        snake_data = self.convert_dict_keys(data)
        
        # 只保留SystemSetting模型中存在的字段
        valid_fields = {
            'dark_mode', 'streaming_enabled', 'chat_style',
            'view_mode', 'default_model',
            # 通知相关字段
            'new_message', 'sound', 'system', 'display_time'
        }
        
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in snake_data.items() if k in valid_fields}
        
        # 使用设置仓库保存设置
        system_setting = self.setting_repo.create_or_update_system_setting(filtered_data)
        
        # 如果保存成功，返回更新后的设置
        if system_setting:
            return {
                'dark_mode': system_setting.dark_mode,
                'streaming_enabled': system_setting.streaming_enabled,
                'chat_style': system_setting.chat_style,
                'view_mode': system_setting.view_mode,
                'default_model': system_setting.default_model,
                # 通知相关字段
                'newMessage': system_setting.new_message,
                'sound': system_setting.sound,
                'system': system_setting.system,
                'displayTime': system_setting.display_time
            }
        else:
            # 如果保存失败，返回原始数据
            return data
    
    def get_all_settings(self):
        """获取所有设置"""
        # 系统设置现在包含了通知设置
        system = self.get_system_setting()
        
        return {
            'system': system
        }
