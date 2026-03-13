"""设置相关业务逻辑服务"""
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
from app.utils.data import NamingUtils
from app.core.database import get_db
from app.core.cache import cache_manager

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    def __init__(self, setting_repo: SettingRepository):
        """初始化设置服务
        
        Args:
            setting_repo: 设置仓库实例，用于依赖注入
        """
        from app.services.data_service import DataService
        self.setting_repo = setting_repo
        self.data_service = DataService()
    
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
        # 优先从内存缓存获取设置
        settings = self.data_service.get_settings() or {}
        system_settings = settings.get('system', {})
        
        if system_settings:
            # 从内存缓存返回设置，转换为前端期望的格式
            return {
                'dark_mode': system_settings.get('darkMode', False),
                'streaming_enabled': system_settings.get('streamingEnabled', True),
                'chat_style': system_settings.get('chatStyle', 'bubble'),
                'view_mode': system_settings.get('viewMode', 'grid'),
                'default_model': system_settings.get('defaultModel', ""),
                # 通知相关字段
                'newMessage': system_settings.get('newMessage', True),
                'sound': system_settings.get('sound', False),
                'system': system_settings.get('system', True),
                'displayTime': system_settings.get('displayTime', '5秒'),
                'vector_db_path': system_settings.get('vector_db_path', ''),
                'default_top_k': system_settings.get('default_top_k', 3),
                'default_score_threshold': system_settings.get('default_score_threshold', 0.7)
            }
        
        # 如果内存缓存中没有设置，从数据库获取
        system_setting = self.setting_repo.get_system_setting()
        if system_setting:
            return {
                'dark_mode': getattr(system_setting, 'dark_mode', False) or False,
                'streaming_enabled': getattr(system_setting, 'streaming_enabled', True) or True,
                'chat_style': getattr(system_setting, 'chat_style', 'bubble') or 'bubble',
                'view_mode': getattr(system_setting, 'view_mode', 'grid') or 'grid',
                'default_model': getattr(system_setting, 'default_model', "") or "",
                # 通知相关字段
                'newMessage': getattr(system_setting, 'new_message', True) or True,
                'sound': getattr(system_setting, 'sound', False) or False,
                'system': getattr(system_setting, 'system', True) or True,
                'displayTime': getattr(system_setting, 'display_time', '5秒') or '5秒',
                'vector_db_path': getattr(system_setting, 'vector_db_path', ''),
                'default_top_k': getattr(system_setting, 'default_top_k', 3),
                'default_score_threshold': getattr(system_setting, 'default_score_threshold', 0.7)
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
                'sound': True,
                'system': True,
                'displayTime': '5秒',
                'vector_db_path': '',
                'default_top_k': 3,
                'default_score_threshold': 0.7
            }
    
    def save_system_setting(self, data):
        """保存系统设置（包含通知设置）"""
        # 1. 获取当前的设置数据
        current_settings = self.data_service.get_settings() or {}
        system_settings = current_settings.get('system', {})
        
        # 2. 更新内存缓存中的设置
        # 处理前端发送的蛇形命名格式数据
        # 直接映射蛇形命名到驼峰命名
        field_mapping = {
            'dark_mode': 'darkMode',
            'streaming_enabled': 'streamingEnabled',
            'chat_style': 'chatStyle',
            'view_mode': 'viewMode',
            'default_model': 'defaultModel',
            'new_message': 'newMessage',
            'display_time': 'displayTime'
        }
        
        for key, value in data.items():
            # 检查是否需要转换命名格式
            if key in field_mapping:
                # 蛇形命名转驼峰命名
                system_settings[field_mapping[key]] = value
            else:
                # 不需要转换的字段直接使用
                system_settings[key] = value
        
        # 更新内存缓存
        current_settings['system'] = system_settings
        for key, value in current_settings.items():
            self.data_service.update_setting(key, value)
        
        # 3. 设置脏标记，触发自动保存
        self.data_service.set_dirty_flag('settings')
        
        # 4. 从内存缓存返回更新后的数据
        # 直接返回内存中最新的设置数据，转换为前端期望的格式
        return {
            'dark_mode': system_settings.get('darkMode', False),
            'streaming_enabled': system_settings.get('streamingEnabled', True),
            'chat_style': system_settings.get('chatStyle', 'bubble'),
            'view_mode': system_settings.get('viewMode', 'grid'),
            'default_model': system_settings.get('defaultModel', ''),
            'newMessage': system_settings.get('newMessage', True),
            'sound': system_settings.get('sound', False),
            'system': system_settings.get('system', True),
            'displayTime': system_settings.get('displayTime', '5秒'),
            'vector_db_path': system_settings.get('vector_db_path', ''),
            'default_top_k': system_settings.get('default_top_k', 3),
            'default_score_threshold': system_settings.get('default_score_threshold', 0.7)
        }
    
    def get_all_settings(self):
        """获取所有设置"""
        # 系统设置现在包含了通知设置
        system = self.get_system_setting()
        
        return {
            'system': system
        }