"""服务基类，提供公共功能"""
from functools import wraps

# 使用提取的工具类
from app.utils.logging_utils import LoggingUtils
from app.utils.exception_handler import ExceptionHandler
from app.utils.input_validator import InputValidator
from app.utils.model_utils import ModelUtils

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
        LoggingUtils.log_info(message, extra=extra)
    
    @staticmethod
    def log_warning(message, extra=None):
        """记录警告日志"""
        LoggingUtils.log_warning(message, extra=extra)
    
    @staticmethod
    def log_error(message, extra=None, exc_info=False):
        """记录错误日志"""
        LoggingUtils.log_error(message, extra=extra, exc_info=exc_info)
    
    @staticmethod
    def log_debug(message, extra=None):
        """记录调试日志"""
        LoggingUtils.log_debug(message, extra=extra)
    
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
        return ExceptionHandler.handle_exception(exception, message)
    
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
        return InputValidator.validate_input(data, required_fields)