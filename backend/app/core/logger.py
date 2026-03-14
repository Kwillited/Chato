"""统一日志模块"""
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any


class Logger:
    """统一日志类，封装所有日志功能"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 日志配置
        from .config import config_manager
        self.log_dir = os.path.join(config_manager.get_user_data_dir(), 'logs')
        self.log_file = os.path.join(self.log_dir, 'chato.log')
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.encoding = 'utf-8'
        
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化日志记录器
        self.logger = logging.getLogger('chato')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # 创建日志格式
        self.formatter = self._create_formatter()
        
        # 设置处理器
        self._setup_handlers()
        
        self._initialized = True
    
    def _create_formatter(self) -> logging.Formatter:
        """创建日志格式化器"""
        log_format = (
            '[%(asctime)s] %(name)s - %(levelname)-8s - '  
            '[%(process)d] %(filename)s:%(lineno)d - '  
            '%(funcName)s() - %(message)s'
        )
        return logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    def _setup_handlers(self) -> None:
        """设置日志处理器"""
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding=self.encoding
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(self.formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def update_config(self, config_manager) -> None:
        """更新日志配置"""
        # 根据配置更新日志级别等
        debug_mode = config_manager.get('app.debug', True)
        log_level_str = config_manager.get('app.log_level', 'debug' if debug_mode else 'info')
        
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        log_level = level_map.get(log_level_str.lower(), logging.INFO)
        self.logger.setLevel(log_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
    
    def get_logger(self) -> logging.Logger:
        """获取日志记录器"""
        return self.logger
    
    # 日志方法
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """记录信息日志"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """记录警告日志"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """记录错误日志"""
        self.logger.error(message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """记录调试日志"""
        self.logger.debug(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """记录严重错误日志"""
        self.logger.critical(message, extra=extra, exc_info=exc_info)


# 创建全局日志实例
logger = Logger()


# 导出日志实例
__all__ = ['logger']
