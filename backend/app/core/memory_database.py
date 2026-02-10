"""内存数据库管理类"""
from typing import Dict, Any, Optional, List, Type, Tuple
from app.core.database import SessionLocal
from app.models.database.models import (
    SystemSetting, AppSetting, VectorSetting, NotificationSetting,
    Chat, Message, Document, DocumentChunk, Folder, AgentSession, Model, ModelVersion
)
from app.models.database.mcp_models import MCPConfig, MCPTool, MCPServer

# 模型类型映射
MODEL_TYPE_MAPPING = {
    'system_settings': SystemSetting,
    'app_settings': AppSetting,
    'vector_settings': VectorSetting,
    'notification_settings': NotificationSetting,
    'chats': Chat,
    'messages': Message,
    'documents': Document,
    'document_chunks': DocumentChunk,
    'folders': Folder,
    'agent_sessions': AgentSession,
    'models': Model,
    'model_versions': ModelVersion,
    'mcp_configs': MCPConfig,
    'mcp_tools': MCPTool,
    'mcp_servers': MCPServer
}

class MemoryDatabaseManager:
    """内存数据库管理器，实现内存与SQLite的同步"""
    _instance = None
    _memory_data = None
    _db = None
    _model_indexes = None  # 用于存储模型ID索引，提高查询性能
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化内存数据库"""
        if MemoryDatabaseManager._instance is not None:
            raise Exception("内存数据库管理器是单例模式，请使用get_instance()方法获取实例")
        
        MemoryDatabaseManager._instance = self
        self._memory_data = {
            'system_settings': None,
            'app_settings': None,
            'vector_settings': None,
            'notification_settings': None,
            'chats': [],
            'messages': [],
            'documents': [],
            'document_chunks': [],
            'folders': [],
            'agent_sessions': [],
            'models': [],
            'model_versions': [],
            'mcp_configs': [],
            'mcp_tools': [],
            'mcp_servers': []
        }
        
        # 初始化索引
        self._model_indexes = {
            'chats': {},
            'messages': {},
            'documents': {},
            'document_chunks': {},
            'folders': {},
            'agent_sessions': {},
            'models': {},
            'model_versions': {},
            'mcp_configs': {},
            'mcp_tools': {},
            'mcp_servers': {}
        }
        
        # 初始化时从SQLite加载数据到内存
        self.load_from_database()
    
    def load_from_database(self):
        """从SQLite数据库加载数据到内存"""
        try:
            # 创建临时会话用于加载数据
            db = SessionLocal()
            try:
                # 加载设置数据
                self._load_setting_data(db)
                
                # 加载其他数据
                self._load_collection_data('chats', Chat, db)
                self._load_collection_data('messages', Message, db)
                self._load_collection_data('documents', Document, db)
                self._load_collection_data('document_chunks', DocumentChunk, db)
                self._load_collection_data('folders', Folder, db)
                self._load_collection_data('agent_sessions', AgentSession, db)
                self._load_collection_data('models', Model, db)
                self._load_collection_data('model_versions', ModelVersion, db)
                self._load_collection_data('mcp_configs', MCPConfig, db)
                self._load_collection_data('mcp_tools', MCPTool, db)
                self._load_collection_data('mcp_servers', MCPServer, db)
            finally:
                db.close()
        except Exception as e:
            print(f"从数据库加载数据失败: {e}")
    
    def _load_setting_data(self, db):
        """加载设置数据"""
        # 加载系统设置
        system_setting = db.query(SystemSetting).first()
        if system_setting:
            self._memory_data['system_settings'] = system_setting
        
        # 加载应用设置
        app_setting = db.query(AppSetting).first()
        if app_setting:
            self._memory_data['app_settings'] = app_setting
        
        # 加载向量设置
        vector_setting = db.query(VectorSetting).first()
        if vector_setting:
            self._memory_data['vector_settings'] = vector_setting
        
        # 加载通知设置
        notification_setting = db.query(NotificationSetting).first()
        if notification_setting:
            self._memory_data['notification_settings'] = notification_setting
    
    def _load_collection_data(self, model_type: str, model_class: Type, db):
        """加载集合数据"""
        items = db.query(model_class).all()
        self._memory_data[model_type] = items
        
        # 更新索引
        for item in items:
            if hasattr(item, 'id'):
                self._model_indexes[model_type][item.id] = item
    
    def save_to_database(self, model_type: str, data: Any):
        """将内存数据保存到SQLite数据库"""
        try:
            # 创建临时会话用于保存数据
            db = SessionLocal()
            try:
                # 处理设置数据
                if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    existing = db.query(model_class).first()
                    if existing:
                        # 更新现有记录
                        for key, value in data.__dict__.items():
                            if not key.startswith('_'):
                                setattr(existing, key, value)
                        db.commit()
                        db.refresh(existing)
                        return existing
                    else:
                        # 创建新记录
                        new_item = model_class(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                        db.add(new_item)
                        db.commit()
                        db.refresh(new_item)
                        return new_item
                
                # 处理集合数据
                else:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    
                    # 检查是否已存在
                    if hasattr(data, 'id'):
                        existing = db.query(model_class).filter_by(id=data.id).first()
                        if existing:
                            # 更新现有记录
                            for key, value in data.__dict__.items():
                                if not key.startswith('_'):
                                    setattr(existing, key, value)
                            db.commit()
                            db.refresh(existing)
                            return existing
                    
                    # 创建新记录
                    new_item = model_class(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    db.add(new_item)
                    db.commit()
                    db.refresh(new_item)
                    return new_item
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
            return None
    
    def get(self, model_type: str, item_id: Optional[Any] = None) -> Optional[Any]:
        """从内存数据库获取数据"""
        # 处理设置数据
        if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
            return self._memory_data.get(model_type)
        
        # 处理集合数据
        if item_id:
            return self._model_indexes[model_type].get(item_id)
        return self._memory_data.get(model_type)
    
    def set(self, model_type: str, data: Any) -> bool:
        """设置内存数据库数据并同步到SQLite"""
        try:
            # 处理设置数据
            if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                # 更新内存数据
                self._memory_data[model_type] = data
                
                # 同步到SQLite
                result = self.save_to_database(model_type, data)
                return result is not None
            
            # 处理集合数据
            else:
                # 更新内存数据
                if hasattr(data, 'id'):
                    # 检查是否已存在
                    existing_index = next(
                        (i for i, item in enumerate(self._memory_data[model_type]) 
                         if hasattr(item, 'id') and item.id == data.id),
                        None
                    )
                    
                    if existing_index is not None:
                        # 更新现有数据
                        self._memory_data[model_type][existing_index] = data
                    else:
                        # 添加新数据
                        self._memory_data[model_type].append(data)
                    
                    # 更新索引
                    self._model_indexes[model_type][data.id] = data
                else:
                    # 添加新数据（无ID）
                    self._memory_data[model_type].append(data)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, data)
                return result is not None
        except Exception as e:
            print(f"设置内存数据库数据失败: {e}")
            return False
    
    def update(self, model_type: str, item_id: Any, updates: Dict[str, Any]) -> Optional[Any]:
        """更新内存数据库数据并同步到SQLite"""
        try:
            # 处理设置数据
            if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                existing_data = self._memory_data.get(model_type)
                if not existing_data:
                    return None
                
                # 更新内存数据
                for key, value in updates.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, existing_data)
                return result
            
            # 处理集合数据
            else:
                existing_data = self._model_indexes[model_type].get(item_id)
                if not existing_data:
                    return None
                
                # 更新内存数据
                for key, value in updates.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, existing_data)
                return result
        except Exception as e:
            print(f"更新内存数据库数据失败: {e}")
            return None
    
    def delete(self, model_type: str, item_id: Any) -> bool:
        """删除内存数据库数据并同步到SQLite"""
        try:
            # 处理设置数据
            if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                # 设置为None
                self._memory_data[model_type] = None
                
                # 删除数据库中的记录
                db = SessionLocal()
                try:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    existing = db.query(model_class).first()
                    if existing:
                        db.delete(existing)
                        db.commit()
                finally:
                    db.close()
                return True
            
            # 处理集合数据
            else:
                # 从内存中删除
                existing_data = self._model_indexes[model_type].get(item_id)
                if not existing_data:
                    return False
                
                # 从列表中删除
                self._memory_data[model_type] = [
                    item for item in self._memory_data[model_type]
                    if not (hasattr(item, 'id') and item.id == item_id)
                ]
                
                # 从索引中删除
                del self._model_indexes[model_type][item_id]
                
                # 从数据库中删除
                db = SessionLocal()
                try:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    existing = db.query(model_class).filter_by(id=item_id).first()
                    if existing:
                        db.delete(existing)
                        db.commit()
                except Exception as e:
                    print(f"删除数据库记录失败: {e}")
                    db.rollback()
                finally:
                    db.close()
                return True
        except Exception as e:
            print(f"删除内存数据库数据失败: {e}")
            return False
    
    def create_or_update(self, model_type: str, data: Dict[str, Any]) -> Any:
        """创建或更新数据"""
        try:
            # 处理设置数据
            if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                existing_data = self._memory_data.get(model_type)
                
                if existing_data:
                    # 更新现有数据
                    for key, value in data.items():
                        if hasattr(existing_data, key):
                            setattr(existing_data, key, value)
                    
                    # 同步到SQLite
                    result = self.save_to_database(model_type, existing_data)
                    return result
                else:
                    # 创建新数据
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    new_data = model_class(**data)
                    
                    # 保存到内存
                    self._memory_data[model_type] = new_data
                    
                    # 同步到SQLite
                    result = self.save_to_database(model_type, new_data)
                    return result
            
            # 处理集合数据
            else:
                # 检查是否有ID
                if 'id' in data:
                    existing_data = self._model_indexes[model_type].get(data['id'])
                    
                    if existing_data:
                        # 更新现有数据
                        for key, value in data.items():
                            if hasattr(existing_data, key):
                                setattr(existing_data, key, value)
                        
                        # 同步到SQLite
                        result = self.save_to_database(model_type, existing_data)
                        return result
                
                # 创建新数据
                model_class = MODEL_TYPE_MAPPING[model_type]
                new_data = model_class(**data)
                
                # 保存到内存
                self._memory_data[model_type].append(new_data)
                if hasattr(new_data, 'id'):
                    self._model_indexes[model_type][new_data.id] = new_data
                
                # 同步到SQLite
                result = self.save_to_database(model_type, new_data)
                return result
        except Exception as e:
            print(f"创建或更新数据失败: {e}")
            return None
    
    def query(self, model_type: str, **filters) -> List[Any]:
        """查询内存数据库数据"""
        # 处理集合数据
        if model_type not in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
            results = []
            for item in self._memory_data[model_type]:
                match = True
                for key, value in filters.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        return []
    
    def refresh(self, model_type: str) -> bool:
        """从SQLite刷新内存数据"""
        try:
            # 创建临时会话用于刷新数据
            db = SessionLocal()
            try:
                # 处理设置数据
                if model_type in ['system_settings', 'app_settings', 'vector_settings', 'notification_settings']:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    data = db.query(model_class).first()
                    if data:
                        self._memory_data[model_type] = data
                    return True
                
                # 处理集合数据
                else:
                    model_class = MODEL_TYPE_MAPPING[model_type]
                    self._load_collection_data(model_type, model_class, db)
                    return True
            finally:
                db.close()
        except Exception as e:
            print(f"刷新内存数据失败: {e}")
            return False
    
    # 删除旧的 _load_collection_data 方法，因为我们已经使用了带 db 参数的新版本
    # def _load_collection_data(self, model_type: str, model_class: Type):
    #     """加载集合数据"""
    #     items = self._db.query(model_class).all()
    #     self._memory_data[model_type] = items
    #     
    #     # 更新索引
    #     self._model_indexes[model_type] = {}
    #     for item in items:
    #         if hasattr(item, 'id'):
    #             self._model_indexes[model_type][item.id] = item

# 创建全局内存数据库实例
memory_db = MemoryDatabaseManager.get_instance()