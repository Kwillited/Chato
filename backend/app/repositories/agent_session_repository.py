"""智能体会话数据访问类"""
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.database.models import AgentSession

class AgentSessionRepository(BaseRepository):
    """智能体会话数据访问类，处理智能体会话相关的数据访问"""
    
    def get_session_by_id(self, session_id):
        """根据ID获取智能体会话"""
        return self.db.query(AgentSession).filter(AgentSession.id == session_id).first()
    
    def get_sessions_by_chat_id(self, chat_id):
        """根据对话ID获取所有智能体会话"""
        return self.db.query(AgentSession).filter(AgentSession.chat_id == chat_id).order_by(desc(AgentSession.created_at)).all()
    
    def create_session(self, session_id, chat_id, created_at, updated_at, graph_state=None, current_node="", step_count=0):
        """创建新智能体会话"""
        session = AgentSession(
            id=session_id,
            chat_id=chat_id,
            created_at=created_at,
            updated_at=updated_at,
            graph_state=graph_state,
            current_node=current_node,
            step_count=step_count
        )
        return self.add(session)
    
    def update_session(self, session_id, updated_at, graph_state=None, current_node=None, step_count=None):
        """更新智能体会话"""
        session = self.get_session_by_id(session_id)
        if session:
            session.updated_at = updated_at
            if graph_state is not None:
                session.graph_state = graph_state
            if current_node is not None:
                session.current_node = current_node
            if step_count is not None:
                session.step_count = step_count
            return self.update(session)
        return None
    
    def update_session_state(self, session_id, updated_at, current_node, step_count):
        """更新智能体会话状态"""
        return self.update_session(session_id, updated_at, current_node=current_node, step_count=step_count)
    
    def update_graph_state(self, session_id, updated_at, graph_state):
        """更新智能体会话的图状态"""
        return self.update_session(session_id, updated_at, graph_state=graph_state)
    
    def delete_session(self, session_id):
        """删除智能体会话"""
        session = self.get_session_by_id(session_id)
        if session:
            self.delete(session)
            return True
        return False
    
    def delete_sessions_by_chat_id(self, chat_id):
        """根据对话ID删除所有智能体会话"""
        # 批量删除，利用SQLAlchemy的删除API
        result = self.db.query(AgentSession).filter(AgentSession.chat_id == chat_id).delete()
        self.db.commit()
        return result
    
    def delete_all_sessions(self):
        """删除所有智能体会话"""
        result = self.db.query(AgentSession).delete()
        self.db.commit()
        return result
    
    def get_all_sessions(self):
        """获取所有智能体会话"""
        return self.db.query(AgentSession).all()
    
    def create_or_update_session(self, session_id, chat_id, created_at, updated_at, graph_state=None, current_node="", step_count=0):
        """创建或更新智能体会话"""
        session = self.get_session_by_id(session_id)
        if session:
            # 更新现有会话
            session.chat_id = chat_id
            session.created_at = created_at
            session.updated_at = updated_at
            session.graph_state = graph_state
            session.current_node = current_node
            session.step_count = step_count
            return self.update(session)
        else:
            # 创建新会话
            return self.create_session(session_id, chat_id, created_at, updated_at, graph_state, current_node, step_count)
    
    def get_latest_session_by_chat_id(self, chat_id):
        """获取对话的最新智能体会话"""
        return self.db.query(AgentSession).filter(AgentSession.chat_id == chat_id).order_by(desc(AgentSession.created_at)).first()