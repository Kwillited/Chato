"""嵌入模型仓库类"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repositories.base_repository import BaseRepository
from app.models.database.models import EmbeddingModel, EmbeddingVersion


class EmbeddingModelRepository(BaseRepository):
    """嵌入模型仓库类，处理嵌入模型的CRUD操作"""
    
    def __init__(self, db: Session):
        """初始化嵌入模型仓库
        
        Args:
            db (Session): SQLAlchemy会话
        """
        super().__init__(db)
    
    def get_all_models(self, enabled_only: bool = False) -> List[EmbeddingModel]:
        """获取所有嵌入模型
        
        Args:
            enabled_only (bool): 是否只获取启用的模型
            
        Returns:
            List[EmbeddingModel]: 嵌入模型列表
        """
        db = self.get_db()
        try:
            query = db.query(EmbeddingModel)
            # 不再过滤enabled字段，因为该字段已移至EmbeddingVersion表
            return query.all()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_model_by_name(self, model_name: str) -> Optional[EmbeddingModel]:
        """根据名称获取嵌入模型
        
        Args:
            model_name (str): 模型名称
            
        Returns:
            Optional[EmbeddingModel]: 嵌入模型实例
        """
        db = self.get_db()
        try:
            return db.query(EmbeddingModel).filter(EmbeddingModel.name == model_name).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_model_by_id(self, model_id: int) -> Optional[EmbeddingModel]:
        """根据ID获取嵌入模型
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            Optional[EmbeddingModel]: 嵌入模型实例
        """
        db = self.get_db()
        try:
            return db.query(EmbeddingModel).filter(EmbeddingModel.id == model_id).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def create_model(self, model_data: Dict[str, Any]) -> EmbeddingModel:
        """创建新的嵌入模型
        
        Args:
            model_data (Dict[str, Any]): 模型数据
            
        Returns:
            EmbeddingModel: 创建的嵌入模型实例
        """
        # 检查模型是否已存在
        existing_model = self.get_model_by_name(model_data.get('name'))
        if existing_model:
            return existing_model
        
        # 创建新模型
        model = EmbeddingModel(**model_data)
        return self.add(model)
    
    def update_model(self, model_id: int, model_data: Dict[str, Any]) -> Optional[EmbeddingModel]:
        """更新嵌入模型
        
        Args:
            model_id (int): 模型ID
            model_data (Dict[str, Any]): 模型数据
            
        Returns:
            Optional[EmbeddingModel]: 更新后的嵌入模型实例
        """
        model = self.get_model_by_id(model_id)
        if not model:
            return None
        
        # 更新模型数据
        for key, value in model_data.items():
            setattr(model, key, value)
        
        return self.update(model)
    
    def delete_model(self, model_id: int) -> bool:
        """删除嵌入模型
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            bool: 是否删除成功
        """
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        
        self.delete(model)
        return True
    
    def get_model_versions(self, model_id: int) -> List[EmbeddingVersion]:
        """获取模型的所有版本
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            List[EmbeddingVersion]: 模型版本列表
        """
        db = self.get_db()
        try:
            return db.query(EmbeddingVersion).filter(
                EmbeddingVersion.model_id == model_id
            ).all()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_version_by_name(self, model_id: int, version_name: str) -> Optional[EmbeddingVersion]:
        """根据版本名称获取模型版本
        
        Args:
            model_id (int): 模型ID
            version_name (str): 版本名称
            
        Returns:
            Optional[EmbeddingVersion]: 模型版本实例
        """
        db = self.get_db()
        try:
            return db.query(EmbeddingVersion).filter(
                and_(
                    EmbeddingVersion.model_id == model_id,
                    EmbeddingVersion.version_name == version_name
                )
            ).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def create_model_version(self, version_data: Dict[str, Any]) -> EmbeddingVersion:
        """创建新的模型版本
        
        Args:
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            EmbeddingVersion: 创建的模型版本实例
        """
        # 检查版本是否已存在
        existing_version = self.get_version_by_name(
            version_data.get('model_id'),
            version_data.get('version_name')
        )
        if existing_version:
            return existing_version
        
        # 创建新版本
        version = EmbeddingVersion(**version_data)
        return self.add(version)
    
    def update_model_version(self, version_id: int, version_data: Dict[str, Any]) -> Optional[EmbeddingVersion]:
        """更新模型版本
        
        Args:
            version_id (int): 版本ID
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            Optional[EmbeddingVersion]: 更新后的模型版本实例
        """
        db = self.get_db()
        try:
            version = db.query(EmbeddingVersion).filter(
                EmbeddingVersion.id == version_id
            ).first()
            
            if not version:
                return None
            
            # 更新版本数据
            for key, value in version_data.items():
                setattr(version, key, value)
            
            return self.update(version)
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def delete_model_version(self, version_id: int) -> bool:
        """删除模型版本
        
        Args:
            version_id (int): 版本ID
            
        Returns:
            bool: 是否删除成功
        """
        db = self.get_db()
        try:
            version = db.query(EmbeddingVersion).filter(
                EmbeddingVersion.id == version_id
            ).first()
            
            if not version:
                return False
            
            self.delete(version)
            return True
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_default_model(self) -> Optional[EmbeddingModel]:
        """获取默认的嵌入模型
        
        Returns:
            Optional[EmbeddingModel]: 默认嵌入模型实例
        """
        db = self.get_db()
        try:
            # 直接返回第一个模型，因为enabled字段已移至EmbeddingVersion表
            return db.query(EmbeddingModel).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def is_embedding_model_table_empty(self) -> bool:
        """检查嵌入模型表是否为空
        
        Returns:
            bool: 嵌入模型表是否为空
        """
        db = self.get_db()
        try:
            return db.query(EmbeddingModel).count() == 0
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
