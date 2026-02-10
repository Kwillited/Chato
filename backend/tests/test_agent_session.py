"""测试智能体会话功能"""
import sys
import os
import json
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import init_alembic_db
from app.services.chat.chat_service import ChatService
from app.repositories.agent_session_repository import AgentSessionRepository
from app.repositories.message_repository import MessageRepository


def test_agent_session():
    """测试智能体会话功能"""
    print("开始测试智能体会话功能...")
    
    try:
        # 创建临时数据库文件
        print("0. 创建临时数据库文件...")
        import tempfile
        import shutil
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_db_path = os.path.join(temp_dir, 'test_chato.db')
        print(f"创建临时数据库文件: {temp_db_path}")
        
        # 修改数据库路径（使用猴子补丁）
        from app.core import database
        original_get_db_path = database.get_db_path
        
        def mock_get_db_path():
            return temp_db_path
        
        database.get_db_path = mock_get_db_path
        
        # 重新初始化数据库引擎
        from app.core.database import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        
        # 创建新的引擎
        test_engine = create_engine(
            f"sqlite:///{temp_db_path}",
            connect_args={
                "check_same_thread": False,
                "uri": True,
            },
            poolclass=StaticPool,
            pool_pre_ping=True,
        )
        
        # 创建新的会话工厂
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        # 替换原始的引擎和会话工厂
        database.engine = test_engine
        database.SessionLocal = TestSessionLocal
        
        # 初始化数据库
        print("1. 初始化数据库...")
        from app.models import models
        Base.metadata.create_all(bind=test_engine)
        print("数据库初始化成功")
        
        # 保存临时目录路径，用于清理
        test_temp_dir = temp_dir
        
        # 创建服务实例
        chat_service = ChatService()
        agent_session_repo = AgentSessionRepository()
        message_repo = MessageRepository()
        
        # 创建测试对话
        print("2. 创建测试对话...")
        from app.services.data_service import DataService
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        chat = {
            'id': chat_id,
            'title': "测试智能体对话",
            'preview': '',
            'createdAt': now,
            'updatedAt': now,
            'messages': []
        }
        DataService.add_chat(chat)
        print(f"创建对话成功，ID: {chat_id}")
        
        # 创建智能体会话
        print("3. 创建智能体会话...")
        initial_graph_state = json.dumps({
            "messages": [],
            "loop_count": 0,
            "current_node": "think"
        })
        
        agent_session = chat_service.create_agent_session(
            chat_id=chat_id,
            graph_state=initial_graph_state,
            current_node="think",
            step_count=0
        )
        
        if not agent_session:
            print("创建智能体会话失败")
            return False
        
        session_id = agent_session['id']
        print(f"创建智能体会话成功，ID: {session_id}")
        
        # 创建智能体消息
        print("4. 创建智能体消息...")
        now = datetime.now().isoformat()
        agent_message = {
            'id': str(uuid.uuid4()),
            'chat_id': chat_id,
            'role': 'assistant',
            'message_type': 'agent',
            'content': '【思考】：我需要查询天气信息...',
            'createdAt': now,
            'agent_session_id': session_id,
            'agent_node': 'think',
            'agent_step': 0,
            'agent_metadata': json.dumps({
                'agent_step': 0,
                'node': 'think',
                'thought': '我需要查询天气信息'
            })
        }
        
        # 保存智能体消息
        message_repo.create_message(
            message_id=agent_message['id'],
            chat_id=agent_message['chat_id'],
            role=agent_message['role'],
            content=agent_message['content'],
            reasoning_content=None,
            created_at=agent_message['createdAt'],
            model=None,
            message_type=agent_message['message_type'],
            agent_session_id=agent_message['agent_session_id'],
            agent_node=agent_message['agent_node'],
            agent_step=agent_message['agent_step'],
            agent_metadata=agent_message['agent_metadata']
        )
        print("创建智能体消息成功")
        
        # 更新智能体会话
        print("5. 更新智能体会话...")
        updated_graph_state = json.dumps({
            "messages": [agent_message],
            "loop_count": 1,
            "current_node": "analyze"
        })
        
        updated_session = chat_service.update_agent_session(
            session_id=session_id,
            graph_state=updated_graph_state,
            current_node="analyze",
            step_count=1
        )
        
        if not updated_session:
            print("更新智能体会话失败")
            return False
        
        print(f"更新智能体会话成功，当前节点: {updated_session['current_node']}")
        
        # 获取智能体会话
        print("6. 获取智能体会话...")
        retrieved_session = chat_service.get_agent_session(session_id)
        if not retrieved_session:
            print("获取智能体会话失败")
            return False
        
        print(f"获取智能体会话成功，ID: {retrieved_session['id']}")
        print(f"会话状态: {retrieved_session['current_node']}, 步骤: {retrieved_session['step_count']}")
        
        # 获取对话的所有智能体会话
        print("7. 获取对话的所有智能体会话...")
        sessions = chat_service.get_agent_sessions_by_chat_id(chat_id)
        print(f"获取到 {len(sessions)} 个智能体会话")
        
        # 获取最新智能体会话
        print("8. 获取最新智能体会话...")
        latest_session = chat_service.get_latest_agent_session(chat_id)
        if not latest_session:
            print("获取最新智能体会话失败")
            return False
        
        print(f"获取最新智能体会话成功，ID: {latest_session['id']}")
        
        # 测试删除智能体会话
        print("9. 测试删除智能体会话...")
        delete_result = chat_service.delete_agent_session(session_id)
        if not delete_result:
            print("删除智能体会话失败")
            return False
        
        print("删除智能体会话成功")
        
        # 验证删除是否成功
        deleted_session = chat_service.get_agent_session(session_id)
        if deleted_session:
            print("删除智能体会话后仍能获取到会话，测试失败")
            return False
        
        print("验证删除成功，会话已不存在")
        
        print("\n🎉 所有测试通过！智能体会话功能正常工作")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件
        print("\n10. 清理临时文件...")
        try:
            if 'test_temp_dir' in locals() and os.path.exists(test_temp_dir):
                shutil.rmtree(test_temp_dir)
                print(f"清理临时目录成功: {test_temp_dir}")
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")


if __name__ == "__main__":
    success = test_agent_session()
    sys.exit(0 if success else 1)
