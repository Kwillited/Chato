"""基础Repository类"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.memory_database import memory_db

class BaseRepository:
    """基础Repository类，提供通用的数据访问方法"""
    
    def __init__(self, db: Session = None):
        """初始化Repository
        
        Args:
            db: SQLAlchemy会话对象，用于依赖注入
        """
        self.db = db or SessionLocal()
    
    def get_db(self):
        """获取数据库会话"""
        return self.db
    
    def close(self):
        """关闭数据库会话"""
        if self.db:
            self.db.close()
    
    def add(self, model):
        """添加模型实例到数据库"""
        # 对于所有模型，使用内存数据库
        model_type = self._get_model_type(model)
        if model_type:
            memory_db.set(model_type, model)
            return model
        
        # 如果无法确定模型类型，返回None
        return None
    
    def update(self, model):
        """更新模型实例"""
        # 对于所有模型，使用内存数据库
        model_type = self._get_model_type(model)
        if model_type:
            memory_db.set(model_type, model)
            return model
        
        # 如果无法确定模型类型，返回None
        return None
    
    def delete(self, model):
        """删除模型实例"""
        # 对于所有模型，使用内存数据库
        model_type = self._get_model_type(model)
        if model_type:
            # 对于有ID的模型，使用delete方法
            if hasattr(model, 'id'):
                memory_db.delete(model_type, model.id)
            else:
                # 对于无ID的模型，设置为None
                memory_db.set(model_type, None)
            return
    
    def commit(self):
        """提交事务"""
        # 所有数据操作都通过内存数据库，内存数据库会自动提交
        pass
    
    def rollback(self):
        """回滚事务"""
        # 所有数据操作都通过内存数据库，需要从数据库重新加载
        pass
    
    def _get_model_type(self, model) -> str:
        """获取模型类型对应的内存数据库键名"""
        model_class_name = model.__class__.__name__
        
        if model_class_name == 'SystemSetting':
            return 'system_settings'
        elif model_class_name == 'AppSetting':
            return 'app_settings'
        elif model_class_name == 'VectorSetting':
            return 'vector_settings'
        elif model_class_name == 'NotificationSetting':
            return 'notification_settings'
        elif model_class_name == 'Chat':
            return 'chats'
        elif model_class_name == 'Message':
            return 'messages'
        elif model_class_name == 'Document':
            return 'documents'
        elif model_class_name == 'DocumentChunk':
            return 'document_chunks'
        elif model_class_name == 'Folder':
            return 'folders'
        elif model_class_name == 'AgentSession':
            return 'agent_sessions'
        elif model_class_name == 'Model':
            return 'models'
        elif model_class_name == 'ModelVersion':
            return 'model_versions'
        elif model_class_name == 'MCPConfig':
            return 'mcp_configs'
        elif model_class_name == 'MCPTool':
            return 'mcp_tools'
        elif model_class_name == 'MCPServer':
            return 'mcp_servers'
        
        return None
