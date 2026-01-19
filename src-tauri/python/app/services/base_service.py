"""服务基类，提供公共功能"""
import logging
from functools import wraps

# 使用项目统一的日志记录器
from app.core.logging_config import logger

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
        # 如果model没有versions数组或version_id为空，返回空字典
        if not model.get('versions') or not version_id:
            return {}
        
        # 查找匹配的版本，支持version_name和custom_name
        version = next((v for v in model['versions'] 
                      if v.get('version_name') == version_id or v.get('custom_name') == version_id), None)
        
        # 返回版本的配置信息（如果找到），否则返回空字典
        return version if version else {}
    
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
        BaseService.log_error(f"{message}: {str(exception)}", exc_info=True)
        return {'error': message}, 500
    
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
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
            if not data[field]:
                return False, f'字段 {field} 不能为空'
        return True, None