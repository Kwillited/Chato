"""统一错误处理模块"""
import functools
import traceback
from typing import Callable, Any, Tuple
from app.core.logging_config import logger
from app.utils.logging_utils import LoggingUtils


class ErrorHandler:
    """错误处理工具类，封装所有错误处理方法"""
    
    # 错误类型映射
    ERROR_TYPES = {
        'validation': 400,
        'not_found': 404,
        'unauthorized': 401,
        'forbidden': 403,
        'server': 500
    }
    
    @staticmethod
    def handle_errors(default_return: Any = None, log_error: bool = True, log_level: str = "error", re_raise: bool = False):
        """
        错误处理装饰器，统一处理函数异常
        
        Args:
            default_return: 发生异常时的默认返回值
            log_error: 是否记录错误日志
            log_level: 日志级别，可选值：debug, info, warning, error, critical
            re_raise: 是否重新抛出异常
            
        Returns:
            Callable: 装饰后的函数
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 检查是否为 HTTPException
                    from fastapi import HTTPException
                    if isinstance(e, HTTPException):
                        # HTTPException 直接重新抛出，由 FastAPI 处理
                        raise e
                    
                    if log_error:
                        # 获取日志记录器方法
                        log_method = getattr(logger, log_level, logger.error)
                        log_method(f"函数 {func.__name__} 执行失败: {str(e)}")
                        log_method(f"错误类型: {type(e).__name__}")
                        log_method(f"错误堆栈: {traceback.format_exc()}")
                    
                    if re_raise:
                        raise e
                    
                    return default_return
            return wrapper
        return decorator
    
    # 特定场景的错误处理装饰器
    @staticmethod
    def handle_api_errors(default_return: Any = None, re_raise: bool = True):
        """
        API错误处理装饰器，专为API接口设计
        
        Args:
            default_return: 发生异常时的默认返回值
            re_raise: 是否重新抛出异常
            
        Returns:
            Callable: 装饰后的函数
        """
        return ErrorHandler.handle_errors(
            default_return=default_return, 
            log_error=True, 
            log_level="error",
            re_raise=re_raise
        )
    
    @staticmethod
    def handle_db_errors(default_return: Any = None, re_raise: bool = False):
        """
        数据库错误处理装饰器，专为数据库操作设计
        
        Args:
            default_return: 发生异常时的默认返回值
            re_raise: 是否重新抛出异常
            
        Returns:
            Callable: 装饰后的函数
        """
        return ErrorHandler.handle_errors(
            default_return=default_return, 
            log_error=True, 
            log_level="error",
            re_raise=re_raise
        )
    
    @staticmethod
    def handle_vector_errors(default_return: Any = None, re_raise: bool = False):
        """
        向量操作错误处理装饰器，专为向量存储操作设计
        
        Args:
            default_return: 发生异常时的默认返回值
            re_raise: 是否重新抛出异常
            
        Returns:
            Callable: 装饰后的函数
        """
        return ErrorHandler.handle_errors(
            default_return=default_return, 
            log_error=True, 
            log_level="error",
            re_raise=re_raise
        )
    
    @staticmethod
    def handle_exception(exception: Exception, message: str = "操作失败", error_type: str = "server") -> Tuple[dict, int]:
        """
        统一处理异常，返回HTTP错误响应
        
        Args:
            exception: 捕获的异常
            message: 返回给客户端的错误信息
            error_type: 错误类型，可选值：validation, not_found, unauthorized, forbidden, server
            
        Returns:
            Tuple[dict, int]: (错误响应字典, HTTP状态码)
        """
        status_code = ErrorHandler.ERROR_TYPES.get(error_type, 500)
        
        if status_code >= 500:
            LoggingUtils.log_error(f"{message}: {str(exception)}", exc_info=True)
        else:
            LoggingUtils.log_warning(f"{message}: {str(exception)}")
        
        error_response = {
            'error': message,
            'details': str(exception),
            'error_type': error_type
        }
        
        return error_response, status_code
    
    @staticmethod
    def handle_validation_error(exception: Exception, message: str = "参数验证失败") -> Tuple[dict, int]:
        """
        处理验证异常
        
        Args:
            exception: 捕获的验证异常
            message: 返回给客户端的错误信息
            
        Returns:
            Tuple[dict, int]: (错误响应字典, HTTP状态码)
        """
        return ErrorHandler.handle_exception(
            exception=exception, 
            message=message, 
            error_type="validation"
        )
    
    @staticmethod
    def handle_not_found_error(resource: str, identifier: str) -> Tuple[dict, int]:
        """
        处理资源未找到异常
        
        Args:
            resource: 资源名称
            identifier: 资源标识符
            
        Returns:
            Tuple[dict, int]: (错误响应字典, HTTP状态码)
        """
        error_message = f"{resource} 不存在: {identifier}"
        LoggingUtils.log_warning(error_message)
        
        error_response = {
            'error': error_message,
            'error_type': 'not_found',
            'resource': resource,
            'identifier': identifier
        }
        
        return error_response, 404
    
    @staticmethod
    def handle_unauthorized_error(message: str = "未授权访问") -> Tuple[dict, int]:
        """
        处理未授权访问错误
        
        Args:
            message: 返回给客户端的错误信息
            
        Returns:
            Tuple[dict, int]: (错误响应字典, HTTP状态码)
        """
        LoggingUtils.log_warning(message)
        
        error_response = {
            'error': message,
            'error_type': 'unauthorized'
        }
        
        return error_response, 401
    
    @staticmethod
    def handle_forbidden_error(message: str = "禁止访问") -> Tuple[dict, int]:
        """
        处理禁止访问错误
        
        Args:
            message: 返回给客户端的错误信息
            
        Returns:
            Tuple[dict, int]: (错误响应字典, HTTP状态码)
        """
        LoggingUtils.log_warning(message)
        
        error_response = {
            'error': message,
            'error_type': 'forbidden'
        }
        
        return error_response, 403


# 导出装饰器函数，保持向后兼容
handle_errors = ErrorHandler.handle_errors
handle_api_errors = ErrorHandler.handle_api_errors
handle_db_errors = ErrorHandler.handle_db_errors
handle_vector_errors = ErrorHandler.handle_vector_errors
