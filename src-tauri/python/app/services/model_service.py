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

    def get_all_models(self):
        """获取所有模型供应商以及模型版本"""
        try:
            # 从数据库加载最新数据
            db_models = self.model_repo.get_all_models()
            
            # 从数据库加载所有模型版本
            models = []
            for model in db_models:
                # 直接访问对象属性，而不是使用下标访问
                model_id = model.id
                name = model.name
                description = model.description
                configured = bool(model.configured)
                enabled = bool(model.enabled)
                icon_class = model.icon_class
                icon_bg = model.icon_bg
                icon_color = model.icon_color
                icon_url = model.icon_url
                icon_blob = model.icon_blob
                
                # 获取模型版本
                versions = self.model_repo.get_model_versions(model_id)
                version_list = []
                for version in versions:
                    # 直接访问对象属性，而不是使用下标访问
                    version_list.append({
                        'version_name': version.version_name,
                        'custom_name': version.custom_name,
                        'api_key': version.api_key,
                        'api_base_url': version.api_base_url,
                        'streaming_config': bool(version.streaming_config)
                    })
                
                # 构建模型对象
                model_dict = {
                    'name': name,
                    'description': description,
                    'configured': configured,
                    'enabled': enabled,
                    'icon_class': icon_class,
                    'icon_bg': icon_bg,
                    'icon_color': icon_color,
                    'icon_url': icon_url,
                    'icon_blob': icon_blob,
                    'versions': version_list
                }
                
                # 更新内存数据库
                db_model = DataService.get_model_by_name(name)
                if db_model:
                    # 更新现有模型
                    db_model.update(model_dict)
                else:
                    # 添加新模型
                    DataService.get_models().append(model_dict)
                
                # 过滤掉icon_blob字段，避免JSON序列化错误
                filtered_model = {k: v for k, v in model_dict.items() if k != 'icon_blob'}
                models.append(filtered_model)
            
            return models
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"获取模型列表失败: {str(e)}")
            # 失败时返回内存数据库中的模型
            models = []
            for model in DataService.get_models():
                filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
                models.append(filtered_model)
            return models

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
            # 从数据库获取模型信息，确保使用最新数据
            model_row = self.model_repo.get_model_by_name(model_name)
            if not model_row:
                return False, '模型不存在', None
            
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            
            # 如果内存数据库中找不到模型，从数据库构建模型对象并添加到内存数据库
            if not model:
                # 构建模型对象
                model_id = model_row.id
                name = model_row.name
                description = model_row.description
                configured = bool(model_row.configured)
                enabled = bool(model_row.enabled)
                icon_class = model_row.icon_class
                icon_bg = model_row.icon_bg
                icon_color = model_row.icon_color
                icon_url = model_row.icon_url
                icon_blob = model_row.icon_blob
                
                # 获取模型版本
                versions = self.model_repo.get_model_versions(model_id)
                version_list = []
                for version_row in versions:
                    version_list.append({
                        'version_name': version_row.version_name,
                        'custom_name': version_row.custom_name,
                        'api_key': version_row.api_key,
                        'api_base_url': version_row.api_base_url,
                        'streaming_config': bool(version_row.streaming_config)
                    })
                
                # 创建模型对象
                model = {
                    'name': name,
                    'description': description,
                    'configured': configured,
                    'enabled': enabled,
                    'icon_class': icon_class,
                    'icon_bg': icon_bg,
                    'icon_color': icon_color,
                    'icon_url': icon_url,
                    'icon_blob': icon_blob,
                    'versions': version_list
                }
                
                # 添加到内存数据库
                DataService.get_models().append(model)
            
            # 确保模型有versions数组
            if 'versions' not in model:
                model['versions'] = []
            
            # 获取要配置的版本名称（如果指定了特定版本）
            target_version_name = data.get('version_name', '')
            
            # 查找匹配的版本
            version = next((v for v in model['versions'] if v.get('version_name') == target_version_name), None)
            
            # 如果找不到匹配的版本，创建一个新的版本对象
            if not version:
                version = {}  # 初始化为空对象，只添加必要的字段
                if target_version_name:  # 只有当version_name有值时才添加
                    version['version_name'] = target_version_name
                model['versions'].append(version)
            
            # 将配置信息写入到该版本中，只添加必要的字段
            if target_version_name:  # 确保version_name存在
                version['version_name'] = target_version_name
            
            # 只更新必要的配置字段
            if 'custom_name' in data:
                version['custom_name'] = data['custom_name']
            if 'api_key' in data:
                version['api_key'] = data['api_key']
            if 'api_base_url' in data:
                version['api_base_url'] = data['api_base_url']
            version['streaming_config'] = data.get('streaming_config', False)  # 流式配置
            
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
            
            # 更新数据库中的模型信息
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
            
            # 更新或创建模型版本
            model_id = model_row.id  # 从SQLAlchemy模型对象获取模型ID
            self.model_repo.update_model_version(
                model_id=model_id,
                version_name=version['version_name'],
                custom_name=version.get('custom_name', ''),
                api_key=version.get('api_key', ''),
                api_base_url=version.get('api_base_url', ''),
                streaming_config=version.get('streaming_config', False)
            )
            
            # 设置脏标记，确保数据被保存
            DataService.set_dirty_flag('models')
            
            # 过滤掉icon_blob字段，避免JSON序列化错误
            filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
            return True, f'模型 {model_name} 已配置', filtered_model
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
            # 从数据库获取模型信息，确保使用最新数据
            model_row = self.model_repo.get_model_by_name(model_name)
            if not model_row:
                return False, '模型不存在'
            
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                return False, '模型不存在'
            
            # 清空versions数组
            if 'versions' in model:
                model['versions'] = []
            
            # 重置模型的顶级配置字段
            model.update({
                'configured': False,
                'enabled': False
            })
            
            # 更新数据库中的模型信息
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
            
            # 删除所有相关的模型版本
            model_id = model_row.id  # 从SQLAlchemy模型对象获取模型ID
            versions = self.model_repo.get_model_versions(model_id)
            for version in versions:
                self.model_repo.delete_model_version(model_id, version.version_name)
            
            # 设置脏标记，确保数据被保存
            DataService.set_dirty_flag('models')
            
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
            # 从数据库获取模型信息，确保使用最新数据
            model_row = self.model_repo.get_model_by_name(model_name)
            if not model_row:
                return False, '模型不存在'
            
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                return False, '模型不存在'
            
            # 更新模型启用状态
            model['enabled'] = enabled
            
            # 更新数据库中的模型信息
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
            
            # 设置脏标记，确保数据被保存
            DataService.set_dirty_flag('models')
            
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
            # 从数据库获取模型信息，确保使用最新数据
            model_row = self.model_repo.get_model_by_name(model_name)
            if not model_row:
                return False, '模型不存在', None
            
            # 查找匹配名称的模型
            model = DataService.get_model_by_name(model_name)
            if not model:
                return False, '模型不存在', None
            
            # 检查模型是否有versions数组
            if 'versions' not in model or not model['versions']:
                return False, '该模型没有版本信息', None
            
            # 查找匹配的版本
            version_index = next((i for i, v in enumerate(model['versions']) if v['version_name'] == version_name), None)
            if version_index is None:
                return False, '版本不存在', None
            
            # 从versions数组中删除该版本
            del model['versions'][version_index]

            # 如果模型没有版本了，设置为未配置
            if not model['versions']:
                model['configured'] = False
                model['enabled'] = False
            
            # 更新数据库中的模型信息
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
            
            # 从数据库中删除模型版本
            model_id = model_row.id  # 从SQLAlchemy模型对象获取模型ID
            self.model_repo.delete_model_version(model_id, version_name)
            
            # 设置脏标记，确保数据被保存
            DataService.set_dirty_flag('models')
            
            # 过滤掉icon_blob字段，避免JSON序列化错误
            filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
            return True, f'版本 {version_name} 已成功删除', filtered_model
        except Exception as e:
            # 使用BaseService的日志方法
            self.log_error(f"删除模型版本失败: {str(e)}")
            return False, f'删除模型版本失败: {str(e)}', None