"""回调管理器 - 用于RAG系统的监控和调试"""
import logging
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)


class CallbackManager:
    """回调管理器类 - 处理RAG系统的各种事件回调"""
    
    def __init__(self):
        """初始化回调管理器"""
        self._callbacks: Dict[str, List[Callable]] = {
            'document_load_start': [],
            'document_load_end': [],
            'text_split_start': [],
            'text_split_end': [],
            'vectorization_start': [],
            'vectorization_end': [],
            'search_start': [],
            'search_end': [],
            'rag_chain_start': [],
            'rag_chain_end': [],
            'error': []
        }
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """注册回调函数
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
        else:
            logger.warning(f"未知事件类型: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable) -> None:
        """注销回调函数
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self._callbacks:
            if callback in self._callbacks[event_type]:
                self._callbacks[event_type].remove(callback)
    
    def trigger_callback(self, event_type: str, **kwargs) -> None:
        """触发指定事件类型的所有回调函数
        
        Args:
            event_type: 事件类型
            **kwargs: 事件参数
        """
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"执行回调失败: {str(e)}")
        else:
            logger.warning(f"未知事件类型: {event_type}")
    
    def clear_callbacks(self, event_type: str = None) -> None:
        """清除回调函数
        
        Args:
            event_type: 事件类型，None表示清除所有事件的回调
        """
        if event_type:
            if event_type in self._callbacks:
                self._callbacks[event_type].clear()
        else:
            for event in self._callbacks:
                self._callbacks[event].clear()
    
    def get_callback_count(self, event_type: str = None) -> int:
        """获取回调函数数量
        
        Args:
            event_type: 事件类型，None表示获取所有事件的回调数量
        
        Returns:
            int: 回调函数数量
        """
        if event_type:
            if event_type in self._callbacks:
                return len(self._callbacks[event_type])
            return 0
        else:
            return sum(len(callbacks) for callbacks in self._callbacks.values())


# 创建全局回调管理器实例
global_callback_manager = CallbackManager()


# 便捷函数
def register_callback(event_type: str, callback: Callable) -> None:
    """便捷函数：注册回调"""
    global_callback_manager.register_callback(event_type, callback)


def trigger_callback(event_type: str, **kwargs) -> None:
    """便捷函数：触发回调"""
    global_callback_manager.trigger_callback(event_type, **kwargs)


def get_callback_manager() -> CallbackManager:
    """获取全局回调管理器实例"""
    return global_callback_manager
