"""统一错误处理装饰器模块"""
import functools
import traceback
from typing import Callable, Any, Optional
from app.core.logging_config import logger

def handle_errors(default_return: Any = None, log_error: bool = True, log_level: str = "error"):
    """错误处理装饰器，统一处理函数异常
    
    Args:
        default_return: 发生异常时的默认返回值
        log_error: 是否记录错误日志
        log_level: 日志级别，可选值：debug, info, warning, error, critical
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    # 获取日志记录器方法
                    log_method = getattr(logger, log_level, logger.error)
                    log_method(f"函数 {func.__name__} 执行失败: {str(e)}")
                    log_method(f"错误类型: {type(e).__name__}")
                    log_method(f"错误堆栈: {traceback.format_exc()}")
                return default_return
        return wrapper
    return decorator

# 特定场景的错误处理装饰器
def handle_api_errors(default_return: Any = None):
    """API错误处理装饰器，专为API接口设计"""
    return handle_errors(default_return=default_return, log_error=True, log_level="error")

def handle_db_errors(default_return: Any = None):
    """数据库错误处理装饰器，专为数据库操作设计"""
    return handle_errors(default_return=default_return, log_error=True, log_level="error")

def handle_vector_errors(default_return: Any = None):
    """向量操作错误处理装饰器，专为向量存储操作设计"""
    return handle_errors(default_return=default_return, log_error=True, log_level="error")
