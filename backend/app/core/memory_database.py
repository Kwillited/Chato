"""内存数据库管理类"""
from typing import Dict, Any, Optional, List
from app.core.database import SessionLocal
from app.models.database.models import SystemSetting, VectorSetting, Chat, Message, AgentSession

class MemoryDatabaseManager:
    """内存数据库管理器，实现内存与SQLite的同步"""
    _instance = None
    _memory_data = None
    _db = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化内存数据库"""
        if MemoryDatabaseManager._instance is not None:
            raise Exception("内存数据库管理器是单例模式，请使用get_instance()方法获取实例")
        
        MemoryDatabaseManager._instance = self
        self._db = SessionLocal()
        self._memory_data = {
            'system_settings': None,
            'vector_settings': None,
            'chats': []
        }
        
        # 初始化时从SQLite加载数据到内存
        self.load_from_database()
    
    def load_from_database(self):
        """从SQLite数据库加载数据到内存"""
        try:
            # 加载系统设置
            system_setting = self._db.query(SystemSetting).first()
            if system_setting:
                self._memory_data['system_settings'] = system_setting
            
            # 加载向量设置
            vector_setting = self._db.query(VectorSetting).first()
            if vector_setting:
                self._memory_data['vector_settings'] = vector_setting
            
            # 加载聊天数据
            from sqlalchemy import desc
            chats = self._db.query(Chat).order_by(desc(Chat.updated_at)).all()
            self._memory_data['chats'] = chats
        except Exception as e:
            print(f"从数据库加载数据失败: {e}")
    
    def save_to_database(self, model_type: str, data: Any):
        """将内存数据保存到SQLite数据库"""
        try:
            if model_type == 'system_settings':
                existing = self._db.query(SystemSetting).first()
                if existing:
                    # 更新现有记录
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    # 移除 commit，让调用方决定何时提交
                    # self._db.commit()
                    # self._db.refresh(existing)
                    return existing
                else:
                    # 创建新记录
                    new_setting = SystemSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    # 移除 commit，让调用方决定何时提交
                    # self._db.commit()
                    # self._db.refresh(new_setting)
                    return new_setting
            

            
            elif model_type == 'vector_settings':
                existing = self._db.query(VectorSetting).first()
                if existing:
                    for key, value in data.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    # 移除 commit，让调用方决定何时提交
                    # self._db.commit()
                    # self._db.refresh(existing)
                    return existing
                else:
                    new_setting = VectorSetting(**{k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                    self._db.add(new_setting)
                    # 移除 commit，让调用方决定何时提交
                    # self._db.commit()
                    # self._db.refresh(new_setting)
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
                        
                        # 移除 commit，让调用方决定何时提交
                        # self._db.commit()
                        return data
                    except Exception as e:
                        print(f"保存聊天数据失败: {e}")
                        # 移除 rollback，让调用方决定何时回滚
                        # self._db.rollback()
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
                        
                        # 移除 commit，让调用方决定何时提交
                        # self._db.commit()
                        # 更新内存数据库中的对象
                        self._memory_data['chats'] = new_chats
                        return new_chats
            
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
            # 移除 rollback，让调用方决定何时回滚
            # self._db.rollback()
            return None
    
    def get(self, model_type: str) -> Optional[Any]:
        """从内存数据库获取数据"""
        return self._memory_data.get(model_type)
    
    def set(self, model_type: str, data: Any) -> bool:
        """设置内存数据库数据并同步到SQLite"""
        try:
            # 更新内存数据
            self._memory_data[model_type] = data
            
            # 同步到SQLite
            result = self.save_to_database(model_type, data)
            return result is not None
        except Exception as e:
            print(f"设置内存数据库数据失败: {e}")
            return False
    
    def update(self, model_type: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新内存数据库数据并同步到SQLite"""
        try:
            # 获取现有数据
            existing_data = self._memory_data.get(model_type)
            if not existing_data:
                return None
            
            # 更新内存数据
            for key, value in updates.items():
                if hasattr(existing_data, key):
                    setattr(existing_data, key, value)
            
            # 同步到SQLite
            result = self.save_to_database(model_type, existing_data)
            return result
        except Exception as e:
            print(f"更新内存数据库数据失败: {e}")
            return None
    
    def create_or_update(self, model_type: str, data: Dict[str, Any]) -> Any:
        """创建或更新数据"""
        try:
            # 检查内存中是否已有数据
            existing_data = self._memory_data.get(model_type)
            
            if existing_data:
                # 更新现有数据
                for key, value in data.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                
                # 同步到SQLite
                result = self.save_to_database(model_type, existing_data)
                try:
                    # 提交事务，确保更改被保存到数据库
                    self._db.commit()
                except Exception as commit_error:
                    print(f"提交事务失败: {commit_error}")
                    # 不调用 rollback()，因为 commit() 失败后事务可能已经关闭
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
                self._memory_data[model_type] = new_data
                
                # 同步到SQLite
                result = self.save_to_database(model_type, new_data)
                try:
                    # 提交事务，确保更改被保存到数据库
                    self._db.commit()
                except Exception as commit_error:
                    print(f"提交事务失败: {commit_error}")
                    # 不调用 rollback()，因为 commit() 失败后事务可能已经关闭
                return result
        except Exception as e:
            print(f"创建或更新数据失败: {e}")
            # 尝试回滚，但捕获可能的错误
            try:
                self._db.rollback()
            except:
                # 忽略回滚错误，因为事务可能已经关闭
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
                self._memory_data[model_type] = data
                return True
            return False
        except Exception as e:
            print(f"刷新内存数据失败: {e}")
            return False

# 创建全局内存数据库实例
memory_db = MemoryDatabaseManager.get_instance()