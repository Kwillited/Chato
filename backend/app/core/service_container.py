"""服务容器，管理所有服务的生命周期"""
import threading
from typing import Dict, Type, Any


class ServiceContainer:
    """服务容器类，管理所有服务的实例和生命周期"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServiceContainer, cls).__new__(cls)
                cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化服务容器"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 服务实例字典，存储所有服务的实例
        self._services: Dict[str, Any] = {}
        # 服务构造函数字典，存储服务的构造函数和依赖
        self._service_factories: Dict[str, tuple] = {}
        
        self._initialized = True
    
    def register_service(self, service_name: str, service_class: Type, *dependencies):
        """注册服务
        
        Args:
            service_name: 服务名称
            service_class: 服务类
            dependencies: 服务依赖（依赖名称列表）
        """
        self._service_factories[service_name] = (service_class, dependencies)
    
    def get_service(self, service_identifier) -> Any:
        """获取服务实例
        
        Args:
            service_identifier: 服务名称字符串或服务类
            
        Returns:
            服务实例
        """
        # 确定服务名称
        service_name = service_identifier
        if not isinstance(service_identifier, str):
            # 如果传入的是服务类，尝试通过类名推断服务名称
            class_name = service_identifier.__name__
            # 将驼峰命名转换为下划线命名
            service_name = ''.join(['_' + i.lower() if i.isupper() else i for i in class_name]).lstrip('_')
        
        if service_name not in self._services:
            # 服务未初始化，创建实例
            if service_name not in self._service_factories:
                raise ValueError(f"服务 {service_name} 未注册")
            
            service_class, dependencies = self._service_factories[service_name]
            
            # 解析依赖
            dep_instances = []
            for dep_name in dependencies:
                dep_instances.append(self.get_service(dep_name))
            
            # 对于仓库类，自动提供数据库会话
            from app.core.database import get_db
            if service_name.endswith('_repository'):
                try:
                    db = next(get_db())
                    self._services[service_name] = service_class(db)
                except Exception as e:
                    # 如果获取数据库会话失败，使用默认构造函数
                    self._services[service_name] = service_class()
            else:
                # 创建服务实例
                self._services[service_name] = service_class(*dep_instances)
        
        return self._services[service_name]
    
    def clear_service(self, service_name: str):
        """清除服务实例
        
        Args:
            service_name: 服务名称
        """
        if service_name in self._services:
            del self._services[service_name]
    
    def clear_all_services(self):
        """清除所有服务实例"""
        self._services.clear()
    
    def has_service(self, service_name: str) -> bool:
        """检查服务是否已注册
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否已注册
        """
        return service_name in self._service_factories


# 创建全局服务容器实例
service_container = ServiceContainer()
