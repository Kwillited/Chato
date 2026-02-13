"""模型转换工具类，提供统一的模型转换功能"""

class ModelConverter:
    """模型转换工具类，封装所有模型转换方法"""
    
    @staticmethod
    def model_to_dict(model_obj):
        """
        将SQLAlchemy模型安全地转换为字典，移除无法序列化的属性
        
        参数:
            model_obj: SQLAlchemy模型实例
            
        返回:
            可序列化的字典
        """
        # 获取模型字典，排除SQLAlchemy内部状态
        model_dict = model_obj.__dict__.copy()
        # 移除无法序列化的_sa_instance_state属性
        if '_sa_instance_state' in model_dict:
            del model_dict['_sa_instance_state']
        return model_dict
    
    @staticmethod
    def filter_model_fields(model, exclude_fields=None):
        """
        过滤模型中的指定字段，避免JSON序列化错误
        
        参数:
            model: 模型对象
            exclude_fields: 要排除的字段列表，默认为None
            
        返回:
            过滤后的模型对象
        """
        if exclude_fields is None:
            exclude_fields = ['icon_blob']
        
        if isinstance(model, dict):
            return {k: v for k, v in model.items() if k not in exclude_fields}
        else:
            # 如果是对象，先转换为字典再过滤
            model_dict = ModelConverter.model_to_dict(model)
            return {k: v for k, v in model_dict.items() if k not in exclude_fields}
    
    @staticmethod
    def build_model_dict(model_row, version_repo=None):
        """
        从数据库模型行构建模型字典
        
        参数:
            model_row: 数据库模型行
            version_repo: 版本仓库实例，用于获取模型版本
            
        返回:
            模型字典
        """
        model_id = model_row.id
        version_list = []
        
        if version_repo:
            versions = version_repo.get_model_versions(model_id)
            for version in versions:
                version_list.append({
                    'version_name': version.version_name,
                    'custom_name': version.custom_name,
                    'api_key': version.api_key,
                    'api_base_url': version.api_base_url,
                    'streaming_config': bool(version.streaming_config)
                })
        
        return {
            'name': model_row.name,
            'description': model_row.description,
            'configured': bool(model_row.configured),
            'enabled': bool(model_row.enabled),
            'icon_class': model_row.icon_class,
            'icon_bg': model_row.icon_bg,
            'icon_color': model_row.icon_color,
            'icon_url': model_row.icon_url,
            'icon_blob': getattr(model_row, 'icon_blob', None),
            'versions': version_list
        }
    
    @staticmethod
    def convert_to_bool(value):
        """
        将值转换为布尔类型
        
        参数:
            value: 要转换的值
            
        返回:
            布尔值
        """
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'y', 't')
        elif isinstance(value, int):
            return value != 0
        else:
            return bool(value)
    
    @staticmethod
    def sanitize_model_data(model_data):
        """
        清理模型数据，确保数据类型正确
        
        参数:
            model_data: 模型数据字典
            
        返回:
            清理后的模型数据字典
        """
        if not isinstance(model_data, dict):
            return model_data
        
        sanitized_data = {}
        for key, value in model_data.items():
            # 处理布尔类型字段
            if key in ['configured', 'enabled', 'streaming_config', 'dark_mode', 'auto_scroll', 'show_timestamps', 'confirm_delete', 'streaming_enabled', 'rag_view_mode']:
                sanitized_data[key] = ModelConverter.convert_to_bool(value)
            else:
                sanitized_data[key] = value
        
        return sanitized_data
