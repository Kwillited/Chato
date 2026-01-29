"""模型工具类，提供统一的模型管理功能"""
from app.utils.logging_utils import LoggingUtils

class ModelUtils:
    """模型工具类，封装所有模型相关方法"""
    
    @staticmethod
    def parse_model_info(model_name):
        """
        解析前端发送的模型格式 "Ollama-qwen3:0.6b"
        返回: (模型名称, 版本名称, 模型显示名称)
        """
        parsed_model_name = model_name
        parsed_version_name = None
        
        # 解析模型名称和版本
        if model_name and '-' in model_name:
            parts = model_name.split('-', 1)
            if len(parts) == 2:
                parsed_model_name = parts[0]
                parsed_version_name = parts[1]
        
        # 构建模型显示名称
        model_display_name = parsed_model_name
        # 添加对None值的处理
        if parsed_model_name and parsed_version_name:
            model_display_name = f"{parsed_model_name} - {parsed_version_name}"
        
        return parsed_model_name, parsed_version_name, model_display_name
    
    @staticmethod
    def validate_model(model_name, data_service):
        """
        验证模型是否存在且已配置
        返回: (model_object, error_response, error_code)
        """
        model = data_service.get_model_by_name(model_name)
        if not model:
            return None, {'error': '模型不存在'}, 404
        if not model['configured']:
            return None, {'error': '模型未配置，无法调用'}, 400
        return model, None, None
    
    @staticmethod
    def get_version_config(model, version_id):
        """
        从模型的versions数组中获取特定版本的配置信息
        
        参数:
            model: 模型对象
            version_id: 版本ID或名称（支持version_name和custom_name）
            
        返回:
            版本配置字典
        """
        # 如果model没有versions数组或version_id为空，返回空字典
        if not model.get('versions') or not version_id:
            return {}
        
        # 查找匹配的版本，支持version_name和custom_name
        version = next((v for v in model['versions'] 
                      if v.get('version_name') == version_id or v.get('custom_name') == version_id), None)
        
        # 返回版本的配置信息（如果找到），否则返回空字典
        return version if version else {}
    
    @staticmethod
    def get_model_params(model, version_config):
        """
        获取模型参数
        
        参数:
            model: 模型对象
            version_config: 版本配置
            
        返回:
            模型参数字典
        """
        # 默认参数
        default_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1,
            'frequency_penalty': 0
        }
        
        # 从版本配置中获取参数
        if version_config and isinstance(version_config, dict):
            model_params = version_config.get('model_params', {})
            default_params.update(model_params)
        
        return default_params
    
    @staticmethod
    def is_model_supported(model_name):
        """
        检查模型是否支持
        
        参数:
            model_name: 模型名称
            
        返回:
            bool: 是否支持
        """
        # 这里可以根据实际支持的模型列表进行检查
        # 暂时返回True，实际项目中应该有一个支持的模型列表
        supported_models = ['Ollama', 'OpenAI', 'Anthropic', 'GoogleAI', 'GitHub']
        return any(model.lower() in model_name.lower() for model in supported_models)
    
    @staticmethod
    def get_model_type(model_name):
        """
        获取模型类型
        
        参数:
            model_name: 模型名称
            
        返回:
            str: 模型类型
        """
        model_type_map = {
            'Ollama': 'local',
            'OpenAI': 'cloud',
            'Anthropic': 'cloud',
            'GoogleAI': 'cloud',
            'GitHub': 'cloud'
        }
        
        for model_key, model_type in model_type_map.items():
            if model_key.lower() in model_name.lower():
                return model_type
        
        return 'unknown'