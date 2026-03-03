"""日志配置模块"""
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional

class LogConfig:
    """日志配置类，封装日志相关的配置和操作"""
    
    # 日志级别映射
    LOG_LEVEL_MAP = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    def __init__(self):
        """初始化日志配置"""
        self.log_level = logging.INFO
        
        # 直接使用用户数据目录作为默认日志位置
        from .config import config_manager
        self.log_dir = os.path.join(config_manager.get_user_data_dir(), 'logs')
        self.log_file = os.path.join(self.log_dir, 'chato.log')
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.encoding = 'utf-8'
        
        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger('chato')
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False  # 防止日志传播到root logger
        
        # 创建日志格式
        self.formatter = self._create_formatter()
        
        # 创建处理器
        self._setup_handlers()
    
    def _create_formatter(self) -> logging.Formatter:
        """创建日志格式化器
        
        Returns:
            logging.Formatter: 日志格式化器
        """
        # 完善日志格式，包含更多上下文信息
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
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.formatter)
        
        # 创建文件处理器，支持日志轮转
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding=self.encoding
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        
        # 添加处理器到记录器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def update_config(self, config_manager) -> None:
        """根据配置更新日志设置
        
        Args:
            config_manager: 配置管理器实例
        """
        # 更新日志级别
        debug_mode = config_manager.get('app.debug', True)
        log_level_str = config_manager.get('app.log_level', 'debug' if debug_mode else 'info')
        self.log_level = self.LOG_LEVEL_MAP.get(log_level_str.lower(), logging.INFO)
        
        # 保持日志目录为用户数据目录（已经在初始化时设置）
        self.log_dir = os.path.join(config_manager.get_user_data_dir(), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 更新日志文件路径
        self.log_file = os.path.join(self.log_dir, 'chato.log')
        
        # 更新日志记录器级别
        self.logger.setLevel(self.log_level)
        
        # 更新处理器
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
            # 如果是文件处理器，检查路径是否需要更新
            if isinstance(handler, RotatingFileHandler):
                # 检查文件路径是否不同
                if handler.baseFilename != self.log_file:
                    # 关闭旧的处理器
                    self.logger.removeHandler(handler)
                    handler.close()
                    
                    # 创建新的文件处理器
                    new_handler = RotatingFileHandler(
                        self.log_file,
                        maxBytes=self.max_bytes,
                        backupCount=self.backup_count,
                        encoding=self.encoding
                    )
                    new_handler.setLevel(self.log_level)
                    new_handler.setFormatter(self.formatter)
                    self.logger.addHandler(new_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志记录器
        
        Returns:
            logging.Logger: 日志记录器
        """
        return self.logger

# 创建日志配置实例
log_config = LogConfig()

# 获取日志记录器
logger = log_config.get_logger()


def update_log_config(config_manager):
    """根据配置更新日志设置（兼容旧API）"""
    log_config.update_config(config_manager)

# 导出日志记录器和更新函数
__all__ = ['logger', 'update_log_config']
