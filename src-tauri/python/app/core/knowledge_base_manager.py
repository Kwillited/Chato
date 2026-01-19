"""知识库管理器 - 负责知识库的创建、删除和管理"""
from typing import Dict, Optional, List
from app.core.config import ConfigManager
from app.core.logging_config import logger
from app.utils.error_handler import handle_errors

class KnowledgeBaseManager:
    """知识库管理器，负责知识库的创建、删除和管理"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(KnowledgeBaseManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化知识库管理器"""
        self.config_manager = ConfigManager.get_instance()
        self.user_data_dir = self.config_manager.get_user_data_dir()
    
    @handle_errors(default_return=False)
    def create_knowledge_base(self, name: str, vector_db_path: Optional[str] = None) -> bool:
        """创建新的知识库
        
        Args:
            name: 知识库名称
            vector_db_path: 向量数据库路径，None则使用默认路径
            
        Returns:
            bool: 是否成功创建
        """
        if not name or not isinstance(name, str):
            logger.error(f"知识库名称无效: {name}")
            return False
        
        # 如果没有提供路径，生成默认路径
        if not vector_db_path:
            vector_db_path = self._generate_default_path(name)
        
        # 保存到配置
        result = self.config_manager.add_knowledge_base(name, vector_db_path)
        
        if result:
            logger.info(f"成功创建知识库: {name}, 路径: {vector_db_path}")
        else:
            logger.error(f"创建知识库失败: {name}")
        
        return result
    
    @handle_errors(default_return=False)
    def delete_knowledge_base(self, name: str) -> bool:
        """删除知识库
        
        Args:
            name: 知识库名称
            
        Returns:
            bool: 是否成功删除
        """
        if name == "default":
            logger.error("默认知识库不能删除")
            return False
        
        # 从配置中移除
        result = self.config_manager.remove_knowledge_base(name)
        
        if result:
            logger.info(f"成功删除知识库: {name}")
        else:
            logger.error(f"删除知识库失败: {name}")
        
        return result
    
    @handle_errors(default_return={})
    def list_knowledge_bases(self) -> Dict[str, str]:
        """列出所有知识库
        
        Returns:
            Dict[str, str]: 知识库名称到路径的映射
        """
        knowledge_bases = self.config_manager.get("rag.knowledge_bases", {})
        logger.debug(f"当前知识库列表: {knowledge_bases}")
        return knowledge_bases
    
    @handle_errors(default_return=None)
    def get_knowledge_base_path(self, name: str) -> Optional[str]:
        """获取知识库路径
        
        Args:
            name: 知识库名称
            
        Returns:
            Optional[str]: 知识库路径，如果不存在则返回None
        """
        knowledge_bases = self.list_knowledge_bases()
        return knowledge_bases.get(name)
    
    @handle_errors(default_return=False)
    def update_knowledge_base(self, name: str, new_path: str) -> bool:
        """更新知识库路径
        
        Args:
            name: 知识库名称
            new_path: 新的知识库路径
            
        Returns:
            bool: 是否成功更新
        """
        if not name or not new_path:
            logger.error(f"知识库名称或路径无效: {name}, {new_path}")
            return False
        
        knowledge_bases = self.list_knowledge_bases()
        if name not in knowledge_bases:
            logger.error(f"知识库不存在: {name}")
            return False
        
        knowledge_bases[name] = new_path
        self.config_manager.set("rag.knowledge_bases", knowledge_bases)
        logger.info(f"成功更新知识库路径: {name}, 新路径: {new_path}")
        return True
    
    def _generate_default_path(self, name: str) -> str:
        """生成默认的知识库路径
        
        Args:
            name: 知识库名称
            
        Returns:
            str: 默认路径
        """
        import os
        return os.path.join(
            self.user_data_dir, 'Retrieval-Augmented Generation', f'vectorDb_{name}'
        )
    
    @handle_errors(default_return=[])
    def get_all_knowledge_base_names(self) -> List[str]:
        """获取所有知识库名称
        
        Returns:
            List[str]: 知识库名称列表
        """
        knowledge_bases = self.list_knowledge_bases()
        return list(knowledge_bases.keys())
    
    @handle_errors(default_return=False)
    def exists(self, name: str) -> bool:
        """检查知识库是否存在
        
        Args:
            name: 知识库名称
            
        Returns:
            bool: 是否存在
        """
        knowledge_bases = self.list_knowledge_bases()
        return name in knowledge_bases
