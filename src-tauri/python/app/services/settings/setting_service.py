"""设置相关业务逻辑服务"""
from app.services.data_service import DataService
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
import json
import re

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    def __init__(self, setting_repo=None):
        """初始化设置服务
        
        Args:
            setting_repo: 设置仓库实例，用于依赖注入
        """
        self.setting_repo = setting_repo or SettingRepository()
    
    def camel_to_snake(self, camel_str):
        """将驼峰命名转换为蛇形命名
        
        Args:
            camel_str: 驼峰命名字符串
            
        Returns:
            蛇形命名字符串
        """
        # 转换驼峰命名为蛇形命名
        snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake_str
    
    def convert_dict_keys(self, data_dict):
        """将字典的所有键从驼峰命名转换为蛇形命名
        
        Args:
            data_dict: 包含驼峰命名键的字典
            
        Returns:
            包含蛇形命名键的字典
        """
        return {
            self.camel_to_snake(key): value 
            for key, value in data_dict.items()
        }
    
    def model_to_dict(self, model_obj):
        """将SQLAlchemy模型安全地转换为字典，移除无法序列化的属性
        
        Args:
            model_obj: SQLAlchemy模型实例
            
        Returns:
            可序列化的字典
        """
        # 获取模型字典，排除SQLAlchemy内部状态
        model_dict = model_obj.__dict__.copy()
        # 移除无法序列化的_sa_instance_state属性
        if '_sa_instance_state' in model_dict:
            del model_dict['_sa_instance_state']
        return model_dict
    
    def get_notification_settings(self):
        """获取通知设置"""
        notification_setting = self.setting_repo.get_notification_setting()
        if notification_setting:
            # 将蛇形命名转换为驼峰命名返回给前端
            return {
                'enabled': notification_setting.enabled,
                'newMessage': notification_setting.new_message,
                'sound': notification_setting.sound,
                'system': notification_setting.system,
                'displayTime': notification_setting.display_time
            }
        else:
            # 返回默认值
            return {
                'enabled': True,
                'newMessage': True,
                'sound': False,
                'system': True,
                'displayTime': '5秒'
            }
    
    def save_notification_settings(self, data):
        """保存通知设置"""
        # 将驼峰命名转换为蛇形命名
        snake_data = self.convert_dict_keys(data)
        # 使用Repository保存设置到数据库
        notification_setting = self.setting_repo.create_or_update_notification_setting(snake_data)
        # 将蛇形命名转换为驼峰命名返回给前端
        return {
            'enabled': notification_setting.enabled,
            'newMessage': notification_setting.new_message,
            'sound': notification_setting.sound,
            'system': notification_setting.system,
            'displayTime': notification_setting.display_time
        }
    
    def get_mcp_settings(self):
        """获取MCP设置"""
        mcp_setting = self.setting_repo.get_mcp_setting()
        if mcp_setting:
            return {
                'enabled': mcp_setting.enabled,
                'server_address': mcp_setting.server_address,
                'server_port': mcp_setting.server_port,
                'timeout': mcp_setting.timeout
            }
        else:
            # 返回默认值
            return {
                'enabled': False,
                'server_address': '',
                'server_port': 8080,
                'timeout': 30
            }
    
    def save_mcp_settings(self, data):
        """保存MCP设置"""
        # 将驼峰命名转换为蛇形命名
        snake_data = self.convert_dict_keys(data)
        # 使用Repository保存设置到数据库
        mcp_setting = self.setting_repo.create_or_update_mcp_setting(snake_data)
        return {
            'enabled': mcp_setting.enabled,
            'server_address': mcp_setting.server_address,
            'server_port': mcp_setting.server_port,
            'timeout': mcp_setting.timeout
        }
    
    def get_system_setting(self):
        """获取系统设置"""
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
                'rag_view_mode': system_setting.rag_view_mode
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
                'rag_view_mode': True
            }
    
    def save_system_setting(self, data):
        """保存系统设置"""
        # 将驼峰命名转换为蛇形命名
        snake_data = self.convert_dict_keys(data)
        
        # 只保留SystemSetting模型中存在的字段
        valid_fields = {
            'dark_mode', 'font_size', 'font_family', 'language', 'auto_scroll',
            'show_timestamps', 'confirm_delete', 'streaming_enabled', 'chat_style_document',
            'view_mode', 'default_model', 'rag_view_mode'
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
            'rag_view_mode': system_setting.rag_view_mode
        }
    
    def get_all_settings(self):
        """获取所有设置"""
        # 从各个专用表中获取所有设置
        notification = self.get_notification_settings()
        mcp = self.get_mcp_settings()
        system = self.get_system_setting()
        
        return {
            'notification': notification,
            'mcp': mcp,
            'system': system
        }
