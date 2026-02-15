"""嵌入模型仓库类"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repositories.base_repository import BaseRepository
from app.models.database.models import EmbeddingModel, EmbeddingModelVersion


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
        query = self.db.query(EmbeddingModel)
        if enabled_only:
            query = query.filter(EmbeddingModel.enabled == True)
        return query.all()
    
    def get_model_by_name(self, model_name: str) -> Optional[EmbeddingModel]:
        """根据名称获取嵌入模型
        
        Args:
            model_name (str): 模型名称
            
        Returns:
            Optional[EmbeddingModel]: 嵌入模型实例
        """
        return self.db.query(EmbeddingModel).filter(EmbeddingModel.name == model_name).first()
    
    def get_model_by_id(self, model_id: int) -> Optional[EmbeddingModel]:
        """根据ID获取嵌入模型
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            Optional[EmbeddingModel]: 嵌入模型实例
        """
        return self.db.query(EmbeddingModel).filter(EmbeddingModel.id == model_id).first()
    
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
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
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
        
        self.db.commit()
        self.db.refresh(model)
        return model
    
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
        
        self.db.delete(model)
        self.db.commit()
        return True
    
    def get_model_versions(self, model_id: int) -> List[EmbeddingModelVersion]:
        """获取模型的所有版本
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            List[EmbeddingModelVersion]: 模型版本列表
        """
        return self.db.query(EmbeddingModelVersion).filter(
            EmbeddingModelVersion.model_id == model_id
        ).all()
    
    def get_version_by_name(self, model_id: int, version_name: str) -> Optional[EmbeddingModelVersion]:
        """根据版本名称获取模型版本
        
        Args:
            model_id (int): 模型ID
            version_name (str): 版本名称
            
        Returns:
            Optional[EmbeddingModelVersion]: 模型版本实例
        """
        return self.db.query(EmbeddingModelVersion).filter(
            and_(
                EmbeddingModelVersion.model_id == model_id,
                EmbeddingModelVersion.version_name == version_name
            )
        ).first()
    
    def create_model_version(self, version_data: Dict[str, Any]) -> EmbeddingModelVersion:
        """创建新的模型版本
        
        Args:
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            EmbeddingModelVersion: 创建的模型版本实例
        """
        # 检查版本是否已存在
        existing_version = self.get_version_by_name(
            version_data.get('model_id'),
            version_data.get('version_name')
        )
        if existing_version:
            return existing_version
        
        # 创建新版本
        version = EmbeddingModelVersion(**version_data)
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def update_model_version(self, version_id: int, version_data: Dict[str, Any]) -> Optional[EmbeddingModelVersion]:
        """更新模型版本
        
        Args:
            version_id (int): 版本ID
            version_data (Dict[str, Any]): 版本数据
            
        Returns:
            Optional[EmbeddingModelVersion]: 更新后的模型版本实例
        """
        version = self.db.query(EmbeddingModelVersion).filter(
            EmbeddingModelVersion.id == version_id
        ).first()
        
        if not version:
            return None
        
        # 更新版本数据
        for key, value in version_data.items():
            setattr(version, key, value)
        
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def delete_model_version(self, version_id: int) -> bool:
        """删除模型版本
        
        Args:
            version_id (int): 版本ID
            
        Returns:
            bool: 是否删除成功
        """
        version = self.db.query(EmbeddingModelVersion).filter(
            EmbeddingModelVersion.id == version_id
        ).first()
        
        if not version:
            return False
        
        self.db.delete(version)
        self.db.commit()
        return True
    
    def get_default_model(self) -> Optional[EmbeddingModel]:
        """获取默认的嵌入模型
        
        Returns:
            Optional[EmbeddingModel]: 默认嵌入模型实例
        """
        # 优先返回启用的模型，否则返回第一个模型
        enabled_model = self.db.query(EmbeddingModel).filter(
            EmbeddingModel.enabled == True
        ).first()
        
        if enabled_model:
            return enabled_model
        
        # 返回第一个模型
        return self.db.query(EmbeddingModel).first()
