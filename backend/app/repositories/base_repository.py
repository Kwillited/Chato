"""基础Repository类"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

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
        # 对于设置相关模型，使用传统数据库操作
        model_type = self._get_model_type(model)
        if model_type:
            # 直接添加到数据库
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model
        
        # 对于其他模型，继续使用直接数据库操作
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def update(self, model):
        """更新模型实例"""
        # 对于设置相关模型，使用传统数据库操作
        model_type = self._get_model_type(model)
        if model_type:
            # 直接更新数据库
            self.db.commit()
            self.db.refresh(model)
            return model
        
        # 对于其他模型，继续使用直接数据库操作
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def delete(self, model):
        """删除模型实例"""
        # 对于设置相关模型，不支持删除操作
        model_type = self._get_model_type(model)
        if model_type:
            # 可以选择将其设置为默认值
            return
        
        # 对于其他模型，继续使用直接数据库操作
        self.db.delete(model)
        self.db.commit()
    
    def commit(self):
        """提交事务"""
        # 对于设置相关模型，内存数据库会自动提交
        # 对于其他模型，继续使用直接数据库操作
        self.db.commit()
    
    def rollback(self):
        """回滚事务"""
        # 对于设置相关模型，需要从数据库重新加载
        # 对于其他模型，继续使用直接数据库操作
        self.db.rollback()
    
    def _get_model_type(self, model) -> str:
        """获取模型类型对应的内存数据库键名"""
        model_class_name = model.__class__.__name__
        
        if model_class_name == 'SystemSetting':
            return 'system_settings'
        elif model_class_name == 'VectorSetting':
            return 'vector_settings'
        
        return None
