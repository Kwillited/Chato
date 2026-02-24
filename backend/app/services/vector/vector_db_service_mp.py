"""进程隔离的向量数据库服务 - 使用 multiprocessing 模块实现进程隔离，解决文件删除问题"""
import os
import threading
import multiprocessing
from typing import List, Dict, Any, Optional, Tuple, Callable
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.repositories.vector_repository import VectorRepository
from app.utils.error_handler import handle_vector_errors

class VectorDBProcess(multiprocessing.Process):
    """向量数据库处理进程"""
    def __init__(self, task_queue, result_queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.vector_service = None
        self.running = True
    
    def run(self):
        """进程主循环"""
        while self.running:
            try:
                # 获取任务
                task = self.task_queue.get(block=True, timeout=1)
                if task is None:
                    # 收到终止信号
                    self.running = False
                    self.result_queue.put(None)
                    break
                
                # 解析任务
                action, args, kwargs = task
                
                # 处理任务
                if action == 'init':
                    # 初始化向量服务
                    vector_db_path = args[0]
                    embedder_model = args[1]
                    knowledge_base_name = args[2]
                    result = self._init_service(vector_db_path, embedder_model, knowledge_base_name)
                elif action == 'add_documents':
                    # 添加文档
                    documents = args[0]
                    result = self._add_documents(documents)
                elif action == 'clear_vector_store':
                    # 清空向量库
                    result = self._clear_vector_store()
                elif action == 'get_vector_statistics':
                    # 获取统计信息
                    result = self._get_vector_statistics()
                elif action == 'search_documents':
                    # 搜索文档
                    query = args[0]
                    k = kwargs.get('k', 5)
                    score_threshold = kwargs.get('score_threshold')
                    search_type = kwargs.get('search_type', 'similarity')
                    fetch_k = kwargs.get('fetch_k', 20)
                    filter = kwargs.get('filter')
                    result = self._search_documents(query, k, score_threshold, search_type, fetch_k, filter)
                elif action == 'close':
                    # 关闭服务
                    result = self._close_service()
                    self.running = False
                else:
                    result = (False, f"未知操作: {action}")
                
                # 返回结果
                self.result_queue.put(result)
            except multiprocessing.queues.Empty:
                continue
            except Exception as e:
                # 异常处理
                self.result_queue.put((False, str(e)))
    
    def _init_service(self, vector_db_path, embedder_model, knowledge_base_name):
        """初始化向量服务"""
        try:
            from app.services.vector.vector_db_service import VectorDBService
            self.vector_service = VectorDBService(
                vector_db_path=vector_db_path,
                embedder_model=embedder_model,
                knowledge_base_name=knowledge_base_name
            )
            # 初始化向量存储
            _ = self.vector_service.vector_store
            # 子进程只输出必要的初始化成功日志
            import logging
            logger = logging.getLogger('chato')
            logger.info(f"[子进程:{multiprocessing.current_process().pid}] 进程隔离的向量服务初始化成功")
            return (True, "初始化成功")
        except Exception as e:
            return (False, str(e))
    
    def _add_documents(self, documents):
        """添加文档"""
        if not self.vector_service:
            return (False, "向量服务未初始化")
        return self.vector_service.add_documents(documents)
    
    def _clear_vector_store(self):
        """清空向量库"""
        if not self.vector_service:
            return (False, "向量服务未初始化")
        return self.vector_service.clear_vector_store()
    
    def _get_vector_statistics(self):
        """获取统计信息"""
        if not self.vector_service:
            return {"status": "error", "error": "向量服务未初始化"}
        return self.vector_service.get_vector_statistics()
    
    def _search_documents(self, query, k, score_threshold, search_type, fetch_k, filter):
        """搜索文档"""
        if not self.vector_service:
            return []
        return self.vector_service.search_documents(
            query=query,
            k=k,
            score_threshold=score_threshold,
            search_type=search_type,
            fetch_k=fetch_k,
            filter=filter
        )
    
    def _close_service(self):
        """关闭服务"""
        self.vector_service = None
        return (True, "服务已关闭")

class VectorDBServiceMP(BaseService):
    """进程隔离的向量数据库服务类"""
    
    # 单例实例字典，按知识库名称和嵌入模型区分
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, vector_db_path, embedder_model, knowledge_base_name=None):
        """单例模式实现，按知识库名称和嵌入模型区分实例"""
        knowledge_base_name = knowledge_base_name or "default"
        instance_key = f"{knowledge_base_name}_{embedder_model}"
        
        with cls._lock:
            if instance_key not in cls._instances:
                cls._instances[instance_key] = super(VectorDBServiceMP, cls).__new__(cls)
                cls._instances[instance_key].__init__(vector_db_path, embedder_model, knowledge_base_name)
        return cls._instances[instance_key]
    
    def __init__(self, vector_db_path, embedder_model, knowledge_base_name=None):
        """初始化进程隔离的向量数据库服务"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 参数验证
        if not vector_db_path:
            raise ValueError("必须提供 vector_db_path 参数")
        if not embedder_model:
            raise ValueError("必须提供 embedder_model 参数")
        
        # 使用配置管理器获取用户数据目录
        self.config_manager = config_manager
        self.user_data_dir = self.config_manager.get_user_data_dir()
        
        # 设置知识库名称
        self.knowledge_base_name = knowledge_base_name or "default"
        
        # 设置向量数据库路径
        self.vector_db_path = vector_db_path
        
        # 设置嵌入模型
        self.embedder_model = embedder_model
        
        # 创建进程间通信队列
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        
        # 创建并启动处理进程
        self.process = VectorDBProcess(self.task_queue, self.result_queue)
        self.process.daemon = True
        self.process.start()
        
        # 初始化向量服务
        self._init_service()
        
        # 只在主进程输出初始化日志
        if multiprocessing.current_process().name == 'MainProcess':
            self.log_info(f"初始化进程隔离的向量数据库服务: 知识库='{self.knowledge_base_name}', 嵌入模型='{self.embedder_model}', 路径='{self.vector_db_path}'")
        self._initialized = True
    
    def _init_service(self):
        """初始化向量服务"""
        # 发送初始化任务
        self.task_queue.put(('init', (self.vector_db_path, self.embedder_model, self.knowledge_base_name), {}))
        # 获取结果
        result = self.result_queue.get()
        if not result[0]:
            self.log_error(f"初始化失败: {result[1]}")
            raise Exception(f"初始化失败: {result[1]}")
        self.log_info("进程隔离的向量服务初始化成功")
    
    def _send_task(self, action, *args, **kwargs):
        """发送任务到子进程"""
        try:
            # 检查队列是否可用
            if self.task_queue._closed or self.result_queue._closed:
                # 队列已关闭，重新初始化
                self.log_warning("队列已关闭，重新初始化向量服务...")
                # 重新初始化服务
                self.task_queue = multiprocessing.Queue()
                self.result_queue = multiprocessing.Queue()
                self.process = VectorDBProcess(self.task_queue, self.result_queue)
                self.process.daemon = True
                self.process.start()
                # 重新初始化向量存储
                self._init_service()
            
            # 发送任务
            self.task_queue.put((action, args, kwargs))
            # 获取结果
            return self.result_queue.get(timeout=30)
        except Exception as e:
            self.log_error(f"发送任务失败: {e}")
            # 尝试重新初始化
            try:
                self.task_queue = multiprocessing.Queue()
                self.result_queue = multiprocessing.Queue()
                self.process = VectorDBProcess(self.task_queue, self.result_queue)
                self.process.daemon = True
                self.process.start()
                self._init_service()
                # 重新发送任务
                self.task_queue.put((action, args, kwargs))
                return self.result_queue.get(timeout=30)
            except Exception as re:
                self.log_error(f"重新初始化后发送任务仍然失败: {re}")
                # 返回默认值
                if action == 'search_documents':
                    return []
                elif action == 'clear_vector_store':
                    return (False, str(re))
                elif action == 'get_vector_statistics':
                    return {"status": "error", "error": str(re)}
                else:
                    return (False, str(re))
    
    @handle_vector_errors(default_return=(False, "添加文档失败: 未知错误"))
    def add_documents(self, documents: List[Any]) -> Tuple[bool, str]:
        """将文档片段添加到向量库中"""
        result = self._send_task('add_documents', documents)
        return result
    
    @handle_vector_errors(default_return=(False, "清空向量库失败: 未知错误"))
    def clear_vector_store(self) -> Tuple[bool, str]:
        """清空向量库"""
        result = self._send_task('clear_vector_store')
        return result
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        result = self._send_task('get_vector_statistics')
        return result
    
    def search_documents(self, query: str, k: int = 5, score_threshold: Optional[float] = None, 
                       search_type: str = "similarity", fetch_k: int = 20, 
                       filter: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索相关文档"""
        result = self._send_task('search_documents', query, 
                               k=k, 
                               score_threshold=score_threshold, 
                               search_type=search_type, 
                               fetch_k=fetch_k, 
                               filter=filter)
        return result
    
    @property
    def vector_store(self):
        """获取向量存储实例（通过进程间通信）"""
        # 触发向量存储初始化
        # 这里我们不需要返回实际的向量存储实例，因为所有操作都通过进程间通信完成
        # 这个属性只是为了保持兼容性，确保初始化过程被触发
        # 发送一个简单的任务来确保向量存储已初始化
        try:
            # 发送获取统计信息的任务，这会确保向量存储已初始化
            self.get_vector_statistics()
        except Exception:
            pass
        return self
    
    @property
    def vector_repository(self):
        """获取向量仓库实例（通过进程间通信）"""
        # 这里不需要实际返回向量仓库实例，因为所有操作都通过进程间通信完成
        # 这个属性只是为了保持兼容性，返回 self 以便调用相关方法
        return self
    

    
    def get_vector_store_stats(self):
        """获取向量库统计信息"""
        # 调用已有的获取统计信息方法
        return self.get_vector_statistics()
    
    def search_vectors(self, query, k=5, filter=None, score_threshold=None):
        """根据查询向量检索相关文档"""
        # 调用已有的搜索文档方法
        results = self.search_documents(
            query=query,
            k=k,
            score_threshold=score_threshold,
            filter=filter
        )
        # 格式化结果，与原方法返回格式保持一致
        return {
            'results': results,
            'result_count': len(results)
        }
    
    def close(self):
        """关闭服务，终止子进程"""
        try:
            # 检查队列是否可用
            if not self.task_queue._closed and not self.result_queue._closed:
                # 发送关闭任务
                self.task_queue.put(('close', (), {}))
                # 等待结果
                try:
                    result = self.result_queue.get(timeout=5)
                    self.log_info(f"服务关闭: {result}")
                except Exception as e:
                    self.log_warning(f"获取关闭结果失败: {e}")
            else:
                self.log_info("队列已关闭，直接终止进程")
        except Exception as e:
            self.log_warning(f"关闭服务时出错: {e}")
        finally:
            # 确保进程终止
            try:
                if self.process and self.process.is_alive():
                    self.process.terminate()
                    # 等待进程终止
                    self.process.join(timeout=3)
            except Exception as e:
                self.log_warning(f"终止进程时出错: {e}")
            
            # 清理队列
            try:
                if not self.task_queue._closed:
                    self.task_queue.close()
                    self.task_queue.join_thread()
                if not self.result_queue._closed:
                    self.result_queue.close()
                    self.result_queue.join_thread()
            except Exception as e:
                self.log_warning(f"清理队列时出错: {e}")
            
            # 强制垃圾回收
            try:
                import gc
                gc.collect()
            except:
                pass
    
    def __del__(self):
        """析构函数，确保服务关闭"""
        if hasattr(self, '_initialized') and self._initialized:
            self.close()
