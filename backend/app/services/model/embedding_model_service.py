"""嵌入模型服务类"""
import threading
from typing import List, Optional, Dict, Any
from app.services.base_service import BaseService
from app.repositories.embedding_model_repository import EmbeddingModelRepository
from app.llm.managers.embedding_model_manager import EmbeddingModelManager


class EmbeddingModelService(BaseService):
    """嵌入模型服务类，管理嵌入模型的业务逻辑"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingModelService, cls).__new__(cls)
                cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化嵌入模型服务"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        super().__init__()
        self._initialized = False
        self.embedding_model_manager = EmbeddingModelManager()
        self._initialized = True
        self.log_info("嵌入模型服务初始化成功")
    
    def initialize_models(self, db_session) -> List[Dict[str, Any]]:
        """初始化嵌入模型，将支持的模型添加到数据库
        
        Args:
            db_session: 数据库会话
            
        Returns:
            List[Dict[str, Any]]: 初始化的模型列表
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            supported_models = self.embedding_model_manager.get_supported_models()
            initialized_models = []
            
            for model_name, model_info in supported_models.items():
                # 创建模型记录
                model_data = {
                    'name': model_name,
                    'description': model_info['description'],
                    'type': model_info['type'],
                    'enabled': False,
                    'configured': False
                }
                
                # 设置默认模型
                if model_name == 'qwen3-embedding-0.6b':
                    model_data['enabled'] = True
                    model_data['configured'] = True
                
                # 创建或更新模型
                model = repo.create_model(model_data)
                
                # 创建默认版本
                version_data = {
                    'model_id': model.id,
                    'version_name': 'default',
                    'custom_name': f"{model_name} 默认版本"
                }
                repo.create_model_version(version_data)
                
                initialized_models.append({
                    'id': model.id,
                    'name': model.name,
                    'type': model.type,
                    'enabled': model.enabled
                })
            
            self.log_info(f"成功初始化 {len(initialized_models)} 个嵌入模型")
            return initialized_models
        except Exception as e:
            self.log_error(f"初始化嵌入模型失败: {str(e)}", exc_info=True)
            return []
    
    def get_all_models(self, db_session, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """获取所有嵌入模型
        
        Args:
            db_session: 数据库会话
            enabled_only (bool): 是否只获取启用的模型
            
        Returns:
            List[Dict[str, Any]]: 嵌入模型列表
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            models = repo.get_all_models(enabled_only)
            
            model_list = []
            for model in models:
                versions = repo.get_model_versions(model.id)
                model_list.append({
                    'id': model.id,
                    'name': model.name,
                    'description': model.description,
                    'type': model.type,
                    'enabled': model.enabled,
                    'configured': model.configured,
                    'icon_class': model.icon_class,
                    'icon_bg': model.icon_bg,
                    'icon_color': model.icon_color,
                    'versions': [
                        {
                            'id': version.id,
                            'version_name': version.version_name,
                            'custom_name': version.custom_name,
                            'api_key': version.api_key,
                            'api_base_url': version.api_base_url,
                            'model_path': version.model_path,
                            'dimension': version.dimension
                        }
                        for version in versions
                    ]
                })
            
            return model_list
        except Exception as e:
            self.log_error(f"获取嵌入模型列表失败: {str(e)}", exc_info=True)
            return []
    
    def get_model_by_name(self, db_session, model_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取嵌入模型
        
        Args:
            db_session: 数据库会话
            model_name (str): 模型名称
            
        Returns:
            Optional[Dict[str, Any]]: 嵌入模型信息
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            model = repo.get_model_by_name(model_name)
            
            if not model:
                return None
            
            versions = repo.get_model_versions(model.id)
            return {
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'type': model.type,
                'enabled': model.enabled,
                'configured': model.configured,
                'icon_class': model.icon_class,
                'icon_bg': model.icon_bg,
                'icon_color': model.icon_color,
                'versions': [
                    {
                        'id': version.id,
                        'version_name': version.version_name,
                        'custom_name': version.custom_name,
                        'api_key': version.api_key,
                        'api_base_url': version.api_base_url,
                        'model_path': version.model_path,
                        'dimension': version.dimension
                    }
                    for version in versions
                ]
            }
        except Exception as e:
            self.log_error(f"获取嵌入模型失败: {str(e)}", exc_info=True)
            return None
    
    def update_model(self, db_session, model_id: int, model_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新嵌入模型
        
        Args:
            db_session: 数据库会话
            model_id (int): 模型ID
            model_data (Dict[str, Any]): 模型数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的模型信息
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            updated_model = repo.update_model(model_id, model_data)
            
            if not updated_model:
                return None
            
            versions = repo.get_model_versions(updated_model.id)
            return {
                'id': updated_model.id,
                'name': updated_model.name,
                'description': updated_model.description,
                'type': updated_model.type,
                'enabled': updated_model.enabled,
                'configured': updated_model.configured,
                'icon_class': updated_model.icon_class,
                'icon_bg': updated_model.icon_bg,
                'icon_color': updated_model.icon_color,
                'versions': [
                    {
                        'id': version.id,
                        'version_name': version.version_name,
                        'custom_name': version.custom_name,
                        'api_key': version.api_key,
                        'api_base_url': version.api_base_url,
                        'model_path': version.model_path,
                        'dimension': version.dimension
                    }
                    for version in versions
                ]
            }
        except Exception as e:
            self.log_error(f"更新嵌入模型失败: {str(e)}", exc_info=True)
            return None
    
    def update_model_version(self, db_session, version_id: int, version_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新模型版本
        
        Args:
            db_session: 数据库会话
            version_id (int): 版本ID
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的版本信息
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            updated_version = repo.update_model_version(version_id, version_data)
            
            if not updated_version:
                return None
            
            return {
                'id': updated_version.id,
                'model_id': updated_version.model_id,
                'version_name': updated_version.version_name,
                'custom_name': updated_version.custom_name,
                'api_key': updated_version.api_key,
                'api_base_url': updated_version.api_base_url,
                'model_path': updated_version.model_path,
                'dimension': updated_version.dimension
            }
        except Exception as e:
            self.log_error(f"更新模型版本失败: {str(e)}", exc_info=True)
            return None
    
    def get_default_model(self, db_session) -> Optional[Dict[str, Any]]:
        """获取默认的嵌入模型
        
        Args:
            db_session: 数据库会话
            
        Returns:
            Optional[Dict[str, Any]]: 默认嵌入模型信息
        """
        try:
            repo = EmbeddingModelRepository(db_session)
            default_model = repo.get_default_model()
            
            if not default_model:
                return None
            
            versions = repo.get_model_versions(default_model.id)
            return {
                'id': default_model.id,
                'name': default_model.name,
                'description': default_model.description,
                'type': default_model.type,
                'enabled': default_model.enabled,
                'configured': default_model.configured,
                'versions': versions
            }
        except Exception as e:
            self.log_error(f"获取默认嵌入模型失败: {str(e)}", exc_info=True)
            return None
    
    def load_embedding_model(self, model_name: str, **kwargs) -> Any:
        """加载嵌入模型
        
        Args:
            model_name (str): 模型名称
            **kwargs: 额外参数
            
        Returns:
            Any: 嵌入模型实例
        """
        try:
            model = self.embedding_model_manager.get_embedding_model(model_name, **kwargs)
            if model:
                self.log_info(f"成功加载嵌入模型: {model_name}")
            else:
                self.log_warning(f"加载嵌入模型失败: {model_name}")
            return model
        except Exception as e:
            self.log_error(f"加载嵌入模型异常: {str(e)}", exc_info=True)
            return None
    
    def clear_model_cache(self) -> int:
        """清空模型缓存
        
        Returns:
            int: 清空的缓存项数量
        """
        try:
            cleared_count = self.embedding_model_manager.clear_model_cache()
            self.log_info(f"成功清空 {cleared_count} 个嵌入模型缓存")
            return cleared_count
        except Exception as e:
            self.log_error(f"清空模型缓存失败: {str(e)}", exc_info=True)
            return 0
