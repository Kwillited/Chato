"""路径管理工具类"""
import os
from app.core.config import config_manager

class PathManager:
    """路径管理工具类，统一管理所有路径相关操作"""
    
    @staticmethod
    def get_user_data_dir():
        """获取用户数据目录"""
        return config_manager.get_user_data_dir()
    
    @staticmethod
    def get_rag_dir():
        """获取RAG根目录"""
        return os.path.join(PathManager.get_user_data_dir(), 'Retrieval-Augmented Generation')
    
    @staticmethod
    def get_data_dir():
        """获取文件数据目录"""
        return os.path.join(PathManager.get_rag_dir(), 'files')
    
    @staticmethod
    def get_vector_db_root():
        """获取向量数据库根目录"""
        return os.path.join(PathManager.get_rag_dir(), 'vector_db')
    
    @staticmethod
    def get_folder_path(folder_name):
        """获取文件夹路径"""
        return os.path.join(PathManager.get_data_dir(), folder_name)
    
    @staticmethod
    def get_vector_db_path(folder_name):
        """获取向量数据库路径"""
        return os.path.join(PathManager.get_vector_db_root(), folder_name)
    
    @staticmethod
    def get_file_path(folder_path, filename):
        """获取文件路径"""
        return os.path.join(folder_path, filename)
    
    @staticmethod
    def ensure_dir(path):
        """确保目录存在"""
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def normalize_path(path):
        """标准化路径"""
        return os.path.normpath(path)
    

