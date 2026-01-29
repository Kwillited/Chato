"""异常处理工具类，提供统一的异常处理功能"""
from app.utils.logging_utils import LoggingUtils

class ExceptionHandler:
    """异常处理工具类，封装所有异常处理方法"""
    
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
        LoggingUtils.log_error(f"{message}: {str(exception)}", exc_info=True)
        return {'error': message}, 500
    
    @staticmethod
    def handle_validation_error(exception, message="参数验证失败"):
        """
        处理验证异常
        
        参数:
            exception: 捕获的验证异常
            message: 返回给客户端的错误信息
            
        返回:
            tuple: (错误响应字典, 状态码)
        """
        LoggingUtils.log_error(f"{message}: {str(exception)}")
        return {'error': message, 'details': str(exception)}, 400
    
    @staticmethod
    def handle_not_found_error(resource, identifier):
        """
        处理资源未找到异常
        
        参数:
            resource: 资源名称
            identifier: 资源标识符
            
        返回:
            tuple: (错误响应字典, 状态码)
        """
        error_message = f"{resource} 不存在: {identifier}"
        LoggingUtils.log_warning(error_message)
        return {'error': error_message}, 404