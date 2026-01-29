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
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def update(self, model):
        """更新模型实例"""
        self.db.commit()
        self.db.refresh(model)
        return model
    
    def delete(self, model):
        """删除模型实例"""
        self.db.delete(model)
        self.db.commit()
    
    def commit(self):
        """提交事务"""
        self.db.commit()
    
    def rollback(self):
        """回滚事务"""
        self.db.rollback()
