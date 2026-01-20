"""设置相关业务逻辑服务"""
from app.services.data_service import DataService
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
import json

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    def __init__(self, setting_repo=None):
        """初始化设置服务
        
        Args:
            setting_repo: 设置仓库实例，用于依赖注入
        """
        self.setting_repo = setting_repo or SettingRepository()
    
    def get_notification_settings(self):
        """获取通知设置"""
        notification_setting = self.setting_repo.get_notification_setting()
        if notification_setting:
            return notification_setting.__dict__
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
        # 使用Repository保存设置到数据库
        notification_setting = self.setting_repo.create_or_update_notification_setting(data)
        return notification_setting.__dict__
    
    def get_mcp_settings(self):
        """获取MCP设置"""
        mcp_setting = self.setting_repo.get_mcp_setting()
        if mcp_setting:
            return mcp_setting.__dict__
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
        # 使用Repository保存设置到数据库
        mcp_setting = self.setting_repo.create_or_update_mcp_setting(data)
        return mcp_setting.__dict__
    
    def get_system_setting(self):
        """获取系统设置"""
        system_setting = self.setting_repo.get_system_setting()
        if system_setting:
            return system_setting.__dict__
        else:
            # 返回默认值
            return {
                'dark_mode': False,
                'font_size': 14,
                'chat_style_document': False,
                'view_mode': 'grid',
                'show_hidden_files': False,
                'auto_refresh_files': True,
                'max_recent_files': 10
            }
    
    def save_system_setting(self, data):
        """保存系统设置"""
        # 使用Repository保存设置到数据库
        system_setting = self.setting_repo.create_or_update_system_setting(data)
        return system_setting.__dict__
    
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
