"""嵌入模型服务类"""
import threading
from typing import List, Optional, Dict, Any
from app.services.base_service import BaseService
from app.services.data_service import DataService
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
        self.data_service = DataService()
        self._initialized = True
        self.log_info("嵌入模型服务初始化成功")
    
    def initialize_models(self) -> List[Dict[str, Any]]:
        """初始化嵌入模型，创建默认的模型提供商
        
        Returns:
            List[Dict[str, Any]]: 初始化的模型列表
        """
        try:
            # 初始化逻辑已移至 insert_default_embedding_models 函数
            # 此方法保留用于向后兼容
            self.log_info("嵌入模型初始化完成")
            return []
        except Exception as e:
            self.log_error(f"初始化嵌入模型失败: {str(e)}", exc_info=True)
            return []
    
    def get_all_models(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """获取所有嵌入模型
        
        Args:
            enabled_only (bool): 是否只获取启用的模型
            
        Returns:
            List[Dict[str, Any]]: 嵌入模型列表
        """
        try:
            models = self.data_service.get_all_embedding_models(enabled_only)
            
            model_list = []
            for model in models:
                versions = self.data_service.get_embedding_model_versions(model.id)
                model_list.append({
                    'id': model.id,
                    'name': model.name,
                    'description': model.description,
                    'type': model.type,
                    'enabled': model.enabled,
                    'configured': model.configured,
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
    
    def get_model_by_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取嵌入模型
        
        Args:
            model_name (str): 模型名称
            
        Returns:
            Optional[Dict[str, Any]]: 嵌入模型信息
        """
        try:
            model = self.data_service.get_embedding_model_by_name(model_name)
            
            if not model:
                return None
            
            versions = self.data_service.get_embedding_model_versions(model.id)
            return {
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'type': model.type,
                'enabled': model.enabled,
                'configured': model.configured,
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
    
    def update_model(self, model_id: int, model_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新嵌入模型
        
        Args:
            model_id (int): 模型ID
            model_data (Dict[str, Any]): 模型数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的模型信息
        """
        try:
            updated_model = self.data_service.update_embedding_model(model_id, model_data)
            
            if not updated_model:
                return None
            
            versions = self.data_service.get_embedding_model_versions(updated_model.id)
            return {
                'id': updated_model.id,
                'name': updated_model.name,
                'description': updated_model.description,
                'type': updated_model.type,
                'enabled': updated_model.enabled,
                'configured': updated_model.configured,
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
    
    def update_model_version(self, version_id: int, version_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新模型版本
        
        Args:
            version_id (int): 版本ID
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的版本信息
        """
        try:
            updated_version = self.data_service.update_embedding_model_version(version_id, version_data)
            
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
    
    def get_default_model(self) -> Optional[Dict[str, Any]]:
        """获取默认的嵌入模型
        
        Returns:
            Optional[Dict[str, Any]]: 默认嵌入模型信息
        """
        try:
            default_model = self.data_service.get_default_embedding_model()
            
            if not default_model:
                return None
            
            versions = self.data_service.get_embedding_model_versions(default_model.id)
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
    
    def load_embedding_model(self, model_type: str, model_name: str, **kwargs) -> Any:
        """加载嵌入模型
        
        Args:
            model_type (str): 模型类型 (huggingface, openai, ollama)
            model_name (str): 模型名称
            **kwargs: 额外参数
            
        Returns:
            Any: 嵌入模型实例
        """
        try:
            model = self.embedding_model_manager.get_embedding_model(model_type, model_name, **kwargs)
            if model:
                self.log_info(f"成功加载嵌入模型: {model_name} (类型: {model_type})")
            else:
                self.log_warning(f"加载嵌入模型失败: {model_name} (类型: {model_type})")
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

    def configure_model(self, model_name, data):
        """
        配置特定嵌入模型
        
        Args:
            model_name: 模型名称
            data: 配置数据
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        try:
            # 查找模型
            model = self.data_service.get_embedding_model_by_name(model_name)
            if not model:
                return False, '模型不存在', None
            
            # 获取要配置的版本名称
            target_version_name = data.get('version_name', '')
            
            # 查找匹配的版本
            versions = self.data_service.get_embedding_model_versions(model.id)
            version = next((v for v in versions if v.version_name == target_version_name), None)
            
            # 如果找不到匹配的版本，创建一个新的版本
            if not version:
                version_data = {
                    'model_id': model.id,
                    'version_name': target_version_name,
                    'custom_name': data.get('custom_name', ''),
                    'api_key': data.get('api_key', ''),
                    'api_base_url': data.get('api_base_url', ''),
                    'model_path': data.get('model_path', ''),
                    'dimension': data.get('dimension', 0)
                }
                self.data_service.create_embedding_model_version(version_data)
            else:
                # 更新现有版本
                self.data_service.update_embedding_model_version(
                    version.id,
                    {
                        'custom_name': data.get('custom_name', version.custom_name),
                        'api_key': data.get('api_key', version.api_key),
                        'api_base_url': data.get('api_base_url', version.api_base_url),
                        'model_path': data.get('model_path', version.model_path),
                        'dimension': data.get('dimension', version.dimension)
                    }
                )
            
            # 更新模型状态
            self.data_service.update_embedding_model(
                model.id,
                {
                    'configured': True,
                    'enabled': True
                }
            )
            
            # 重新获取更新后的模型信息
            updated_model = self.get_model_by_name(model_name)
            
            return True, f'嵌入模型 {model_name} 已配置', updated_model
        except Exception as e:
            self.log_error(f"配置嵌入模型失败: {str(e)}", exc_info=True)
            return False, f'配置嵌入模型失败: {str(e)}', None

    def delete_model(self, model_name):
        """
        删除特定嵌入模型配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            元组: (成功标志, 消息)
        """
        try:
            # 查找模型
            model = self.data_service.get_embedding_model_by_name(model_name)
            if not model:
                return False, '模型不存在'
            
            # 删除所有相关的模型版本
            versions = self.data_service.get_embedding_model_versions(model.id)
            for version in versions:
                self.data_service.delete_embedding_model_version(version.id)
            
            # 更新模型状态
            self.data_service.update_embedding_model(
                model.id,
                {
                    'configured': False,
                    'enabled': False
                }
            )
            
            return True, f'嵌入模型 {model_name} 配置已删除'
        except Exception as e:
            self.log_error(f"删除嵌入模型配置失败: {str(e)}", exc_info=True)
            return False, f'删除嵌入模型配置失败: {str(e)}'

    def update_model_enabled(self, model_name, enabled):
        """
        更新嵌入模型启用状态
        
        Args:
            model_name: 模型名称
            enabled: 是否启用
            
        Returns:
            元组: (成功标志, 消息)
        """
        try:
            # 查找模型
            model = self.data_service.get_embedding_model_by_name(model_name)
            if not model:
                return False, '模型不存在'
            
            # 更新模型启用状态
            self.data_service.update_embedding_model(
                model.id,
                {
                    'enabled': enabled
                }
            )
            
            return True, f'嵌入模型 {model_name} 启用状态已更新'
        except Exception as e:
            self.log_error(f"更新嵌入模型启用状态失败: {str(e)}", exc_info=True)
            return False, f'更新嵌入模型启用状态失败: {str(e)}'

    def delete_version(self, model_name, version_name):
        """
        删除特定嵌入模型的特定版本
        
        Args:
            model_name: 模型名称
            version_name: 版本名称
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        try:
            # 查找模型
            model = self.data_service.get_embedding_model_by_name(model_name)
            if not model:
                return False, '模型不存在', None
            
            # 查找匹配的版本
            versions = self.data_service.get_embedding_model_versions(model.id)
            version = next((v for v in versions if v.version_name == version_name), None)
            if not version:
                return False, '版本不存在', None
            
            # 删除版本
            self.data_service.delete_embedding_model_version(version.id)
            
            # 检查模型是否还有其他版本
            remaining_versions = self.data_service.get_embedding_model_versions(model.id)
            if not remaining_versions:
                # 如果没有其他版本，设置为未配置
                self.data_service.update_embedding_model(
                    model.id,
                    {
                        'configured': False,
                        'enabled': False
                    }
                )
            
            # 重新获取更新后的模型信息
            updated_model = self.get_model_by_name(model_name)
            
            return True, f'版本 {version_name} 已成功删除', updated_model
        except Exception as e:
            self.log_error(f"删除嵌入模型版本失败: {str(e)}", exc_info=True)
            return False, f'删除嵌入模型版本失败: {str(e)}', None
