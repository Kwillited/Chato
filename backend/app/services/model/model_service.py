"""模型服务层，处理模型相关的业务逻辑"""

# 依赖数据服务模块
from app.services.data_service import DataService
from app.repositories.model_repository import ModelRepository
from app.services.base_service import BaseService


class ModelService(BaseService):
    """模型服务类，封装所有模型相关的业务逻辑"""

    def __init__(self, model_repo=None):
        """初始化模型服务
        
        Args:
            model_repo: 模型仓库实例，用于依赖注入
        """
        self.model_repo = model_repo or ModelRepository()

    def _filter_icon_blob(self, model):
        """过滤模型中的icon_blob字段，避免JSON序列化错误
        
        Args:
            model: 模型对象
            
        Returns:
            过滤后的模型对象
        """
        return {k: v for k, v in model.items() if k != 'icon_blob'}

    def _build_model_dict(self, model_row):
        """从数据库模型行构建模型字典
        
        Args:
            model_row: 数据库模型行
            
        Returns:
            模型字典
        """
        model_id = model_row.id
        versions = self.model_repo.get_model_versions(model_id)
        version_list = []
        for version in versions:
            version_list.append({
                'version_name': version.version_name,
                'custom_name': version.custom_name,
                'api_key': version.api_key,
                'api_base_url': version.api_base_url,
                'streaming_config': bool(version.streaming_config),
                'type': version.type or 'llm'
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
            'icon_blob': model_row.icon_blob,
            'versions': version_list
        }

    def _load_model_from_db(self, model_name):
        """从数据库加载模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型对象或None
        """
        model_row = self.model_repo.get_model_by_name(model_name)
        if not model_row:
            return None
        
        model_dict = self._build_model_dict(model_row)
        DataService.get_models().append(model_dict)
        return model_dict

    def _update_model_in_db(self, model):
        """更新模型到数据库
        
        Args:
            model: 模型对象
        """
        self.model_repo.update_model(
            name=model['name'],
            description=model['description'],
            configured=model['configured'],
            enabled=model['enabled'],
            icon_class=model['icon_class'],
            icon_bg=model['icon_bg'],
            icon_color=model['icon_color'],
            icon_url=model['icon_url'],
            icon_blob=model.get('icon_blob', None)
        )

    def get_all_models(self):
        """获取所有模型供应商以及模型版本"""
        try:
            # 先从内存数据库获取模型
            memory_models = DataService.get_models()
            
            # 如果内存中有模型数据，直接返回
            if memory_models:
                return [self._filter_icon_blob(model) for model in memory_models]
            
            # 内存中没有模型数据，从SQLite数据库加载
            db_models = self.model_repo.get_all_models()
            
            # 从数据库加载所有模型版本
            models = []
            for model_row in db_models:
                model_dict = self._build_model_dict(model_row)
                
                # 更新内存数据库
                db_model = DataService.get_model_by_name(model_dict['name'])
                if db_model:
                    # 更新现有模型
                    db_model.update(model_dict)
                else:
                    # 添加新模型
                    DataService.get_models().append(model_dict)
                
                models.append(self._filter_icon_blob(model_dict))
            
            return models
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"获取模型列表失败: {str(e)}")
            # 失败时返回内存数据库中的模型
            return [self._filter_icon_blob(model) for model in DataService.get_models()]

    def configure_model(self, model_name, data):
        """
        配置特定模型
        
        Args:
            model_name: 模型名称
            data: 配置数据
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        try:
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            
            # 如果内存数据库中找不到模型，从数据库构建模型对象并添加到内存数据库
            if not model:
                model = self._load_model_from_db(model_name)
                if not model:
                    return False, '模型不存在', None
            
            # 确保模型有versions数组
            if 'versions' not in model:
                model['versions'] = []
            
            # 更新模型的顶级配置字段
            # 对于首次配置的模型，默认设置为启用状态
            is_first_configuration = not model.get('configured')
            model.update({
                'configured': True,
                'enabled': True if is_first_configuration else data.get('enabled', model.get('enabled', True))
            })
            
            # 额外确保首次配置时的enabled状态为True
            if is_first_configuration:
                model['enabled'] = True
            
            # 先设置脏标记，确保数据会被保存
            DataService.set_dirty_flag('models')
            
            # 从数据库获取模型ID（用于后续数据库更新）
            model_row = self.model_repo.get_model_by_name(model_name)
            model_id = model_row.id
            
            # 更新数据库中的模型信息
            self._update_model_in_db(model)
            
            # 只有当提供了version_name时，才创建或更新模型版本
            target_version_name = data.get('version_name', '')
            if target_version_name:  # 只有当version_name有值时，才处理版本配置
                # 查找匹配的版本
                version = next((v for v in model['versions'] if v.get('version_name') == target_version_name), None)
                
                # 如果找不到匹配的版本，创建一个新的版本对象
                if not version:
                    version = {
                        'version_name': target_version_name
                    }
                    model['versions'].append(version)
                
                # 将配置信息写入到该版本中
                if 'custom_name' in data:
                    version['custom_name'] = data['custom_name']
                if 'api_key' in data:
                    version['api_key'] = data['api_key']
                if 'api_base_url' in data:
                    version['api_base_url'] = data['api_base_url']
                if 'type' in data:
                    version['type'] = data['type']
                version['streaming_config'] = data.get('streaming_config', False)  # 流式配置
                
                # 更新或创建模型版本
                self.model_repo.update_model_version(
                    model_id=model_id,
                    version_name=target_version_name,
                    custom_name=version.get('custom_name', ''),
                    api_key=version.get('api_key', ''),
                    api_base_url=version.get('api_base_url', ''),
                    streaming_config=version.get('streaming_config', False),
                    type=version.get('type', 'llm')
                )
            
            return True, f'模型 {model_name} 已配置', self._filter_icon_blob(model)
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"配置模型失败: {str(e)}")
            return False, f'配置模型失败: {str(e)}', None

    def delete_model(self, model_name):
        """
        删除特定模型配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            元组: (成功标志, 消息)
        """
        try:
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                return False, '模型不存在'
            
            # 从数据库获取模型信息
            model_row = self.model_repo.get_model_by_name(model_name)
            if not model_row:
                return False, '模型不存在'
            
            # 先更新内存中的模型配置
            # 清空versions数组
            if 'versions' in model:
                model['versions'] = []
            
            # 重置模型的顶级配置字段
            model.update({
                'configured': False,
                'enabled': False
            })
            
            # 设置脏标记，确保数据会被保存
            DataService.set_dirty_flag('models')
            
            # 更新数据库中的模型信息
            self._update_model_in_db(model)
            
            # 删除所有相关的模型版本
            model_id = model_row.id  # 从SQLAlchemy模型对象获取模型ID
            versions = self.model_repo.get_model_versions(model_id)
            for version in versions:
                self.model_repo.delete_model_version(model_id, version.version_name)
            
            return True, f'模型 {model_name} 配置已删除'
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"删除模型配置失败: {str(e)}")
            return False, f'删除模型配置失败: {str(e)}'

    def update_model_enabled(self, model_name, enabled):
        """
        更新模型启用状态
        
        Args:
            model_name: 模型名称
            enabled: 是否启用
            
        Returns:
            元组: (成功标志, 消息)
        """
        try:
            # 先从内存获取模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                # 如果内存中没有，从SQLite加载
                model = self._load_model_from_db(model_name)
                if not model:
                    return False, '模型不存在'
            
            # 先更新内存中的模型启用状态
            model['enabled'] = enabled
            
            # 设置脏标记，确保数据会被保存
            DataService.set_dirty_flag('models')
            
            # 更新数据库中的模型信息
            self._update_model_in_db(model)
            
            return True, f'模型 {model_name} 启用状态已更新'
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"更新模型启用状态失败: {str(e)}")
            return False, f'更新模型启用状态失败: {str(e)}'

    def delete_version(self, model_name, version_name):
        """
        删除特定模型的特定版本
        
        Args:
            model_name: 模型名称
            version_name: 版本名称
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        try:
            # 先从内存获取模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                # 如果内存中没有，从SQLite加载
                model = self._load_model_from_db(model_name)
                if not model:
                    return False, '模型不存在', None
            
            # 检查模型是否有versions数组
            if 'versions' not in model or not model['versions']:
                return False, '该模型没有版本信息', None
            
            # 查找匹配的版本
            version_index = next((i for i, v in enumerate(model['versions']) if v['version_name'] == version_name), None)
            if version_index is None:
                return False, '版本不存在', None
            
            # 先从内存的versions数组中删除该版本
            del model['versions'][version_index]

            # 如果模型没有版本了，设置为未配置
            if not model['versions']:
                model['configured'] = False
                model['enabled'] = False
            
            # 设置脏标记，确保数据会被保存
            DataService.set_dirty_flag('models')
            
            # 从数据库获取模型ID
            model_row = self.model_repo.get_model_by_name(model_name)
            model_id = model_row.id
            
            # 更新数据库中的模型信息
            self._update_model_in_db(model)
            
            # 从数据库中删除模型版本
            self.model_repo.delete_model_version(model_id, version_name)
            
            return True, f'版本 {version_name} 已成功删除', self._filter_icon_blob(model)
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"删除模型版本失败: {str(e)}")
            return False, f'删除模型版本失败: {str(e)}', None
        
    def get_model_icon(self, filename: str):
        """
        获取模型供应商图标
        
        Args:
            filename: 图标文件名，如 'OpenAI.png'
            
        Returns:
            tuple: (success, icon_data, message)
        """
        import os
        
        try:
            # 提取模型名称（去掉文件扩展名）
            model_name = filename.replace('.png', '')
            
            # 查询数据库中的图标
            result = self.model_repo.get_model_icon(model_name)
            
            if result and result[0]:
                # 从数据库返回图片
                return True, result[0], '从数据库获取图标成功'
            else:
                # 从文件系统返回图片（向后兼容）
                ICONS_DIR = r'C:\Users\admin\AppData\Local\Chato\Chato\icon'
                icon_path = os.path.join(ICONS_DIR, filename)
                if os.path.exists(icon_path):
                    with open(icon_path, 'rb') as f:
                        icon_data = f.read()
                    return True, icon_data, '从文件系统获取图标成功'
                else:
                    return False, None, '图标文件不存在'
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"获取模型图标失败: {str(e)}")
            return False, None, f'获取模型图标失败: {str(e)}'