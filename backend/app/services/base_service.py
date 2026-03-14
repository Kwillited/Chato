"""服务基类，提供公共功能"""

# 使用新的日志模块
from app.core.logger import logger
from app.utils.error_handler import ErrorHandler
from app.utils import ValidationUtils
from app.utils.model import ModelUtils
from datetime import datetime

class BaseService:
    """所有服务类的基类，封装公共方法"""

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
        return ModelUtils.get_version_config(model, version_id)
    
    @staticmethod
    def log_info(message, extra=None):
        """记录信息日志"""
        logger.info(message, extra=extra)
    
    @staticmethod
    def log_warning(message, extra=None):
        """记录警告日志"""
        logger.warning(message, extra=extra)
    
    @staticmethod
    def log_error(message, extra=None, exc_info=False):
        """记录错误日志"""
        logger.error(message, extra=extra, exc_info=exc_info)
    
    @staticmethod
    def log_debug(message, extra=None):
        """记录调试日志"""
        logger.debug(message, extra=extra)
    
    @staticmethod
    def handle_exception(exception, message="操作失败"):
        """
        统一处理异常
        
        参数:
            exception: 捕获的异常
            message: 返回给客户端的错误信息
            
        返回:
            tuple: (错误响应字典, 状态码)
        """
        return ErrorHandler.handle_exception(exception, message)
    
    @staticmethod
    def validate_input(data, required_fields):
        """
        验证输入数据
        
        参数:
            data: 输入数据
            required_fields: 必填字段列表
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        try:
            ValidationUtils.validate_input(data, required_fields)
            return True, None
        except ValueError as e:
            return False, str(e)
    
    @staticmethod
    def get_current_timestamp():
        """
        获取当前时间戳（ISO格式）
        
        返回:
            str: ISO格式的时间戳
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def validate_uuid(uuid_str, param_name="ID"):
        """
        验证UUID格式
        
        参数:
            uuid_str: 要验证的UUID字符串
            param_name: 参数名称，用于错误信息
            
        返回:
            bool: 是否验证通过
        """
        try:
            ValidationUtils.validate_uuid(uuid_str, param_name)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_string_parameter(name, value, min_length=1, max_length=None):
        """
        验证字符串参数
        
        参数:
            name: 参数名称
            value: 参数值
            min_length: 最小长度
            max_length: 最大长度
            
        返回:
            bool: 是否验证通过
        """
        try:
            ValidationUtils.validate_string_parameter(name, value, min_length, max_length)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_service_container(cls):
        """
        获取服务容器实例
        
        返回:
            ServiceContainer: 服务容器实例
        """
        from app.core.service_container import service_container
        return service_container
    
    @classmethod
    def get_service(cls, service_name):
        """
        获取服务实例
        
        参数:
            service_name: 服务名称
            
        返回:
            服务实例
        """
        container = cls.get_service_container()
        return container.get_service(service_name)