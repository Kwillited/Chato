"""内存数据库管理类"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.database.models import SystemSetting, VectorSetting, Chat, Message, AgentSession
from app.core.memory_cache import MemoryCache

class MemoryDatabaseManager:
    """内存数据库管理器，实现内存与SQLite的同步"""
    
    def __init__(self, db: Session, memory_cache: MemoryCache):
        """初始化内存数据库
        
        Args:
            db: 数据库会话
            memory_cache: 内存缓存实例
        """
        self._db = db
        self._memory_cache = memory_cache
        
        # 初始化时从SQLite加载数据到内存
        self.load_from_database()
    
    def load_from_database(self):
        """从SQLite数据库加载数据到内存"""
        try:
            # 加载系统设置
            system_setting = self._db.query(SystemSetting).first()
            if system_setting:
                self._memory_cache.set('system_settings', system_setting)
            
            # 加载向量设置
            vector_setting = self._db.query(VectorSetting).first()
            if vector_setting:
                self._memory_cache.set('vector_settings', vector_setting)
            
            # 加载聊天数据
            from sqlalchemy import desc
            chats = self._db.query(Chat).order_by(desc(Chat.updated_at)).all()
            self._memory_cache.set('chats', chats)
        except Exception as e:
            print(f"从数据库加载数据失败: {e}")
    
    def save_to_database(self, model_type: str, data: Any):
        """将内存数据保存到SQLite数据库"""
        try:
            if model_type == 'system_settings':
                # 确保系统设置表只有一条记录
                existing = self._db.query(SystemSetting).first()
                if existing:
                    # 更新现有记录
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    return existing
                else:
                    # 创建新记录
                    # 先删除所有现有记录（如果有）
                    self._db.query(SystemSetting).delete()
                    # 创建新记录
                    new_setting = SystemSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    # 更新内存缓存
                    self._memory_cache.set(model_type, new_setting)
                    return new_setting
            
            elif model_type == 'vector_settings':
                # 确保向量设置表只有一条记录
                existing = self._db.query(VectorSetting).first()
                if existing:
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    return existing
                else:
                    # 先删除所有现有记录（如果有）
                    self._db.query(VectorSetting).delete()
                    # 创建新记录
                    new_setting = VectorSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    # 更新内存缓存
                    self._memory_cache.set(model_type, new_setting)
                    return new_setting
            
            elif model_type == 'chats':
                # 保存聊天数据
                if isinstance(data, list):
                    try:
                        # 先删除所有现有聊天及其相关记录
                        self._db.query(Message).delete()
                        self._db.query(AgentSession).delete()
                        self._db.query(Chat).delete()
                        
                        # 添加所有聊天
                        for chat in data:
                            # 检查对象状态，如果已删除则重新创建
                            if hasattr(chat, '_sa_instance_state'):
                                if chat._sa_instance_state.deleted:
                                    from sqlalchemy.orm import make_transient
                                    make_transient(chat)
                            # 直接添加对象到会话中
                            self._db.add(chat)
                        
                        return data
                    except Exception as e:
                        print(f"保存聊天数据失败: {e}")
                        # 尝试重新创建对象
                        self._db.query(Message).delete()
                        self._db.query(AgentSession).delete()
                        self._db.query(Chat).delete()
                        
                        # 重新创建聊天对象
                        from app.models.database.models import Chat as ChatModel
                        new_chats = []
                        for chat in data:
                            # 创建新的聊天对象
                            new_chat = ChatModel(
                                id=chat.id,
                                title=chat.title,
                                preview=chat.preview,
                                created_at=chat.created_at,
                                updated_at=chat.updated_at,
                                pinned=getattr(chat, 'pinned', 0)
                            )
                            self._db.add(new_chat)
                            new_chats.append(new_chat)
                        
                        # 更新内存缓存中的对象
                        self._memory_cache.set('chats', new_chats)
                        return new_chats
            
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
            # 回滚事务
            try:
                self._db.rollback()
            except:
                pass
            return None
    
    def get(self, model_type: str) -> Optional[Any]:
        """从内存数据库获取数据"""
        return self._memory_cache.get(model_type)
    
    def set(self, model_type: str, data: Any) -> bool:
        """设置内存数据库数据并同步到SQLite"""
        try:
            # 更新内存数据
            self._memory_cache.set(model_type, data)
            
            # 同步到SQLite
            result = self.save_to_database(model_type, data)
            # 提交事务
            self._db.commit()
            return result is not None
        except Exception as e:
            print(f"设置内存数据库数据失败: {e}")
            # 回滚事务
            try:
                self._db.rollback()
            except:
                pass
            return False
    
    def update(self, model_type: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新内存数据库数据并同步到SQLite"""
        try:
            # 更新内存数据
            existing_data = self._memory_cache.update(model_type, updates)
            if not existing_data:
                return None
            
            # 同步到SQLite
            result = self.save_to_database(model_type, existing_data)
            # 提交事务
            self._db.commit()
            return result
        except Exception as e:
            print(f"更新内存数据库数据失败: {e}")
            # 回滚事务
            try:
                self._db.rollback()
            except:
                pass
            return None
    
    def create_or_update(self, model_type: str, data: Dict[str, Any]) -> Any:
        """创建或更新数据"""
        try:
            # 检查内存中是否已有数据
            existing_data = self._memory_cache.get(model_type)
            
            if existing_data:
                # 更新现有数据
                for key, value in data.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, existing_data)
                # 提交事务
                self._db.commit()
                return result
            else:
                # 创建新数据
                if model_type == 'system_settings':
                    new_data = SystemSetting(**data)
                elif model_type == 'vector_settings':
                    new_data = VectorSetting(**data)
                else:
                    return None
                
                # 保存到内存
                self._memory_cache.set(model_type, new_data)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, new_data)
                # 提交事务
                self._db.commit()
                return result
        except Exception as e:
            print(f"创建或更新数据失败: {e}")
            # 回滚事务
            try:
                self._db.rollback()
            except:
                pass
            return None
    
    def refresh(self, model_type: str) -> bool:
        """从SQLite刷新内存数据"""
        try:
            if model_type == 'system_settings':
                data = self._db.query(SystemSetting).first()
            elif model_type == 'vector_settings':
                data = self._db.query(VectorSetting).first()
            elif model_type == 'chats':
                from sqlalchemy import desc
                data = self._db.query(Chat).order_by(desc(Chat.updated_at)).all()
            else:
                return False
            
            if data:
                self._memory_cache.set(model_type, data)
                return True
            return False
        except Exception as e:
            print(f"刷新内存数据失败: {e}")
            return False

# 为了保持向后兼容，创建一个默认实例
# 注意：这只是为了兼容旧代码，新代码应该使用依赖注入获取实例
from app.core.database import SessionLocal
_default_memory_cache = MemoryCache()
_default_db = SessionLocal()
memory_db = MemoryDatabaseManager(_default_db, _default_memory_cache)