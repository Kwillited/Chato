"""应用配置管理"""
import os
import json
from platformdirs import PlatformDirs

# 初始化平台目录管理
dirs = PlatformDirs(appname="Chato", appauthor="Chato")

# 默认配置
DEFAULT_CONFIG = {
    'vector': {
        'retrieval_mode': 'vector',
        'top_k': 3,
        'score_threshold': 0.7,
        'vector_db_path': '',  # 将在初始化时设置为用户数据目录中的路径
        'embedder_model': 'qwen3-embedding-0.6b',
        'vector_db_type': 'chroma',
        'chunk_size': 1000,
        'chunk_overlap': 200
    },
    'mcp': {
        'enabled': False,
        'server_address': '',
        'server_port': 8080,
        'timeout': 30
    },
    'notification': {
        'enabled': True,
        'newMessage': True,
        'sound': False,
        'system': True,
        'displayTime': '5秒'
    },
    'app': {
        'debug': True,
        'host': '0.0.0.0',
        'port': 5000
    }
}

class ConfigManager:
    """配置管理器"""
    _instance = None
    _config = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if ConfigManager._instance is not None:
            raise Exception("配置管理器是单例模式，请使用get_instance()方法获取实例")
        ConfigManager._instance = self
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 首先使用默认配置
        self._config = DEFAULT_CONFIG.copy()
        
        # 获取用户数据目录
        user_data_dir = self.get_user_data_dir()
        
        # 设置默认的向量数据库路径
        vector_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation')
        os.makedirs(vector_dir, exist_ok=True)
        self._config['vector']['vector_db_path'] = os.path.join(vector_dir, 'vectorDb')
        
        # 创建config子目录
        config_dir = os.path.join(user_data_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # 创建标准的embedding模型目录 - 确保无论RAG是否启用都会创建
        embedding_models_dir = os.path.join(user_data_dir, 'models', 'embedding')
        os.makedirs(embedding_models_dir, exist_ok=True)
        
    def get_user_data_dir(self):
        """获取用户数据目录"""
        user_data_dir = dirs.user_data_dir
        os.makedirs(user_data_dir, exist_ok=True)
        return user_data_dir
    
    def get(self, key_path, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """设置配置值"""
        keys = key_path.split('.')
        config = self._config
        
        # 导航到最后一个键的父级
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        return True
    
    def add_knowledge_base(self, name: str, path: str) -> bool:
        """添加知识库配置
        
        Args:
            name: 知识库名称
            path: 知识库路径
            
        Returns:
            bool: 是否成功添加
        """
        try:
            # 获取知识库配置
            knowledge_bases = self.get("vector.knowledge_bases", {})
            
            # 添加或更新知识库
            knowledge_bases[name] = path
            
            # 保存配置
            self.set("vector.knowledge_bases", knowledge_bases)
            
            return True
        except Exception as e:
            return False
    
    def remove_knowledge_base(self, name: str) -> bool:
        """删除知识库配置
        
        Args:
            name: 知识库名称
            
        Returns:
            bool: 是否成功删除
        """
        try:
            # 获取知识库配置
            knowledge_bases = self.get("vector.knowledge_bases", {})
            
            # 检查知识库是否存在
            if name in knowledge_bases:
                # 删除知识库
                del knowledge_bases[name]
                
                # 保存配置
                self.set("vector.knowledge_bases", knowledge_bases)
                
                return True
            
            return False
        except Exception as e:
            return False

# 创建全局配置实例
config_manager = ConfigManager.get_instance()