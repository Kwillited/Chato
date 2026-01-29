"""日志工具类，提供统一的日志记录功能"""
from app.core.logging_config import logger

class LoggingUtils:
    """日志工具类，封装所有日志记录方法"""
    
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