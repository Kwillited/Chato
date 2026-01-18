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
        return DataService.get_settings().get('notification', {
            'enabled': True,
            'newMessage': True,
            'sound': False,
            'system': True,
            'displayTime': '5秒'
        })
    
    def save_notification_settings(self, data):
        """保存通知设置"""
        # 确保notification设置键存在
        if 'notification' not in DataService.get_settings():
            DataService.get_settings()['notification'] = {
                'enabled': True,
                'newMessage': True,
                'sound': False,
                'system': True,
                'displayTime': '5秒'
            }
        # 合并通知设置
        DataService.get_settings()['notification'].update(data)
        
        # 先设置脏标记
        DataService.set_dirty_flag('settings')
        
        # 再使用Repository保存设置到数据库
        self.setting_repo.create_or_update_setting('notification', DataService.get_settings()['notification'])
        
        return DataService.get_settings()['notification']
    
    def get_mcp_settings(self):
        """获取MCP设置"""
        return DataService.get_settings().get('mcp', {
            'enabled': False,
            'server_address': '',
            'server_port': 8080,
            'timeout': 30
        })
    
    def save_mcp_settings(self, data):
        """保存MCP设置"""
        # 确保mcp设置键存在
        if 'mcp' not in DataService.get_settings():
            DataService.get_settings()['mcp'] = {
                'enabled': False,
                'server_address': '',
                'server_port': 8080,
                'timeout': 30
            }
        # 合并MCP设置
        DataService.get_settings()['mcp'].update(data)
        
        # 先设置脏标记
        DataService.set_dirty_flag('settings')
        
        # 再使用Repository保存设置到数据库
        self.setting_repo.create_or_update_setting('mcp', DataService.get_settings()['mcp'])
        
        return DataService.get_settings()['mcp']
    
    def get_basic_settings(self):
        """获取基本设置"""
        return DataService.get_settings().get('system', {})
    
    def save_basic_settings(self, data):
        """保存基本设置"""
        # 确保system设置键存在
        if 'system' not in DataService.get_settings():
            DataService.get_settings()['system'] = {
                'theme': 'light',
                'language': 'zh-CN',
                'autoSave': True,
                'showPreview': True,
                'maxMessages': 100
            }
        # 合并基本设置
        DataService.get_settings()['system'].update(data)
        
        # 先设置脏标记
        DataService.set_dirty_flag('settings')
        
        # 再使用Repository保存设置到数据库
        self.setting_repo.create_or_update_setting('system', DataService.get_settings()['system'])
        
        return DataService.get_settings()['system']
    
    def get_all_settings(self):
        """获取所有设置"""
        return DataService.get_settings()
    
    def load_settings_from_db(self):
        """从数据库加载设置到内存"""
        settings = self.setting_repo.get_all_settings()
        
        for setting in settings:
            if hasattr(setting, 'key'):
                # 处理ORM对象
                key = setting.key
                value_json = setting.value
            else:
                # 处理元组
                key = setting[0]
                value_json = setting[1]
            
            try:
                # 尝试将JSON字符串转换为字典
                setting_value = json.loads(value_json)
                DataService.get_settings()[key] = setting_value
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接保存为字符串
                DataService.get_settings()[key] = value_json
        
        return DataService.get_settings()
