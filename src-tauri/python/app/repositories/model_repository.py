"""模型数据访问类"""
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models.models import Model, ModelVersion

class ModelRepository(BaseRepository):
    """模型数据访问类，处理模型相关的数据访问"""
    
    def get_all_models(self):
        """获取所有模型"""
        return self.db.query(Model).all()
    
    def get_model_by_name(self, model_name):
        """根据名称获取模型"""
        return self.db.query(Model).filter(Model.name == model_name).first()
    
    def create_model(self, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob):
        """创建新模型"""
        model = Model(
            name=name,
            description=description,
            configured=configured,
            enabled=enabled,
            icon_class=icon_class,
            icon_bg=icon_bg,
            icon_color=icon_color,
            icon_url=icon_url,
            icon_blob=icon_blob
        )
        return self.add(model)
    
    def update_model(self, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob):
        """更新模型"""
        model = self.get_model_by_name(name)
        if model:
            model.description = description
            model.configured = configured
            model.enabled = enabled
            model.icon_class = icon_class
            model.icon_bg = icon_bg
            model.icon_color = icon_color
            model.icon_url = icon_url
            model.icon_blob = icon_blob
            return self.update(model)
        return None
    
    def get_model_versions(self, model_id):
        """获取模型的所有版本"""
        return self.db.query(ModelVersion).filter(ModelVersion.model_id == model_id).all()
    
    def get_model_version(self, model_id, version_name):
        """获取特定版本的模型"""
        return self.db.query(ModelVersion).filter(
            ModelVersion.model_id == model_id,
            ModelVersion.version_name == version_name
        ).first()
    
    def create_model_version(self, model_id, version_name, custom_name, api_key, api_base_url, streaming_config):
        """创建新模型版本"""
        model_version = ModelVersion(
            model_id=model_id,
            version_name=version_name,
            custom_name=custom_name,
            api_key=api_key,
            api_base_url=api_base_url,
            streaming_config=streaming_config
        )
        return self.add(model_version)
    
    def update_model_version(self, model_id, version_name, custom_name, api_key, api_base_url, streaming_config):
        """更新模型版本，不存在则创建"""
        # 查找是否已存在该版本
        existing_version = self.get_model_version(model_id, version_name)
        if existing_version:
            # 更新现有版本
            existing_version.custom_name = custom_name
            existing_version.api_key = api_key
            existing_version.api_base_url = api_base_url
            existing_version.streaming_config = streaming_config
            return self.update(existing_version)
        else:
            # 创建新版本
            return self.create_model_version(model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
    
    def delete_model_version(self, model_id, version_name):
        """删除模型版本"""
        version = self.get_model_version(model_id, version_name)
        if version:
            self.delete(version)
            return True
        return False
    
    def get_model_icon(self, model_name):
        """根据模型名称获取图标"""
        model = self.get_model_by_name(model_name)
        if model:
            return (model.icon_blob,)
        return None
    
    def is_model_table_empty(self):
        """检查模型表是否为空"""
        return self.db.query(Model).count() == 0
    
    def create_or_update_model(self, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob):
        """创建或更新模型"""
        model = self.get_model_by_name(name)
        if model:
            return self.update_model(name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
        else:
            return self.create_model(name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
    
    def create_or_update_model_version(self, model_id, version_name, custom_name, api_key, api_base_url, streaming_config):
        """创建或更新模型版本"""
        return self.update_model_version(model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
