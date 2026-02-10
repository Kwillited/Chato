"""设置相关业务逻辑服务"""
from app.services.data_service import DataService
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
import json
from app.utils.naming_utils import NamingUtils
from app.utils.logging_utils import LoggingUtils

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    def __init__(self, setting_repo=None):
        """初始化设置服务
        
        Args:
            setting_repo: 设置仓库实例，用于依赖注入
        """
        self.setting_repo = setting_repo or SettingRepository()
    
    def convert_dict_keys(self, data_dict):
        """将字典的所有键从驼峰命名转换为蛇形命名
        
        Args:
            data_dict: 包含驼峰命名键的字典
            
        Returns:
            包含蛇形命名键的字典
        """
        return NamingUtils.convert_dict_keys(data_dict)
    


    def get_system_setting(self):
        """获取系统设置（包含通知设置）"""
        system_setting = self.setting_repo.get_system_setting()
        if system_setting:
            return {
                'dark_mode': system_setting.dark_mode,
                'font_size': system_setting.font_size,
                'font_family': system_setting.font_family,
                'language': system_setting.language,
                'auto_scroll': system_setting.auto_scroll,
                'show_timestamps': system_setting.show_timestamps,
                'confirm_delete': system_setting.confirm_delete,
                'streaming_enabled': system_setting.streaming_enabled,
                'chat_style_document': system_setting.chat_style_document,
                'view_mode': system_setting.view_mode,
                'default_model': system_setting.default_model,
                'rag_view_mode': system_setting.rag_view_mode,
                # 通知相关字段
                'enabled': system_setting.enabled,
                'newMessage': system_setting.new_message,
                'sound': system_setting.sound,
                'system': system_setting.system,
                'displayTime': system_setting.display_time
            }
        else:
            # 返回默认值
            return {
                'dark_mode': False,
                'font_size': 16,
                'font_family': "Inter, system-ui, sans-serif",
                'language': "zh-CN",
                'auto_scroll': True,
                'show_timestamps': True,
                'confirm_delete': True,
                'streaming_enabled': True,
                'chat_style_document': False,
                'view_mode': 'grid',
                'default_model': "",
                'rag_view_mode': True,
                # 通知相关默认值
                'enabled': True,
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
            'dark_mode', 'font_size', 'font_family', 'language', 'auto_scroll',
            'show_timestamps', 'confirm_delete', 'streaming_enabled', 'chat_style_document',
            'view_mode', 'default_model', 'rag_view_mode',
            # 通知相关字段
            'enabled', 'new_message', 'sound', 'system', 'display_time'
        }
        
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in snake_data.items() if k in valid_fields}
        
        # 使用Repository保存设置到数据库
        system_setting = self.setting_repo.create_or_update_system_setting(filtered_data)
        
        return {
            'dark_mode': system_setting.dark_mode,
            'font_size': system_setting.font_size,
            'font_family': system_setting.font_family,
            'language': system_setting.language,
            'auto_scroll': system_setting.auto_scroll,
            'show_timestamps': system_setting.show_timestamps,
            'confirm_delete': system_setting.confirm_delete,
            'streaming_enabled': system_setting.streaming_enabled,
            'chat_style_document': system_setting.chat_style_document,
            'view_mode': system_setting.view_mode,
            'default_model': system_setting.default_model,
            'rag_view_mode': system_setting.rag_view_mode,
            # 通知相关字段
            'enabled': system_setting.enabled,
            'newMessage': system_setting.new_message,
            'sound': system_setting.sound,
            'system': system_setting.system,
            'displayTime': system_setting.display_time
        }
    
    def get_all_settings(self):
        """获取所有设置"""
        # 系统设置现在包含了通知设置
        system = self.get_system_setting()
        
        return {
            'system': system
        }
