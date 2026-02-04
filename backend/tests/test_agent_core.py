"""测试智能体会话核心功能"""
import sys
import os
import json
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat.chat_service import ChatService
from app.models.pydantic_models import AgentMessage, AgentSession


def test_agent_core():
    """测试智能体会话核心功能"""
    print("开始测试智能体会话核心功能...")
    
    try:
        # 创建服务实例
        print("1. 创建ChatService实例...")
        chat_service = ChatService()
        print("创建成功")
        
        # 测试智能体会话创建功能
        print("2. 测试智能体会话创建功能...")
        # 创建一个测试对话ID
        test_chat_id = str(uuid.uuid4())
        
        # 创建智能体会话
        initial_graph_state = json.dumps({
            "messages": [],
            "loop_count": 0,
            "current_node": "think"
        })
        
        agent_session = chat_service.create_agent_session(
            chat_id=test_chat_id,
            graph_state=initial_graph_state,
            current_node="think",
            step_count=0
        )
        
        if not agent_session:
            print("❌ 创建智能体会话失败")
            return False
        
        session_id = agent_session['id']
        print(f"✅ 创建智能体会话成功，ID: {session_id}")
        print(f"   会话状态: {agent_session}")
        
        # 测试智能体会话更新功能
        print("3. 测试智能体会话更新功能...")
        updated_graph_state = json.dumps({
            "messages": [],
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
            print("❌ 更新智能体会话失败")
            return False
        
        print(f"✅ 更新智能体会话成功")
        print(f"   更新后状态: {updated_session}")
        
        # 测试智能体会话获取功能
        print("4. 测试智能体会话获取功能...")
        retrieved_session = chat_service.get_agent_session(session_id)
        if not retrieved_session:
            print("❌ 获取智能体会话失败")
            return False
        
        print(f"✅ 获取智能体会话成功")
        print(f"   会话ID: {retrieved_session['id']}")
        print(f"   当前节点: {retrieved_session['current_node']}")
        print(f"   步骤计数: {retrieved_session['step_count']}")
        
        # 测试获取对话的智能体会话列表
        print("5. 测试获取对话的智能体会话列表...")
        sessions = chat_service.get_agent_sessions_by_chat_id(test_chat_id)
        print(f"✅ 获取对话的智能体会话列表成功")
        print(f"   会话数量: {len(sessions)}")
        
        # 测试获取最新智能体会话
        print("6. 测试获取最新智能体会话...")
        latest_session = chat_service.get_latest_agent_session(test_chat_id)
        if not latest_session:
            print("❌ 获取最新智能体会话失败")
            return False
        
        print(f"✅ 获取最新智能体会话成功")
        print(f"   会话ID: {latest_session['id']}")
        
        # 测试删除智能体会话
        print("7. 测试删除智能体会话...")
        delete_result = chat_service.delete_agent_session(session_id)
        if not delete_result:
            print("❌ 删除智能体会话失败")
            return False
        
        print(f"✅ 删除智能体会话成功")
        
        # 验证删除是否成功
        print("8. 验证删除是否成功...")
        deleted_session = chat_service.get_agent_session(session_id)
        if deleted_session:
            print("❌ 删除智能体会话后仍能获取到会话，测试失败")
            return False
        
        print(f"✅ 验证删除成功，会话已不存在")
        
        # 测试Pydantic模型
        print("9. 测试智能体消息Pydantic模型...")
        test_agent_message = AgentMessage(
            id=str(uuid.uuid4()),
            role="assistant",
            content="【思考】：我需要查询天气信息...",
            createdAt=datetime.now().isoformat(),
            message_type="agent",
            agent_session_id=str(uuid.uuid4()),
            agent_node="think",
            agent_step=0,
            agent_metadata=json.dumps({"agent_step": 0, "node": "think"})
        )
        
        print(f"✅ 创建智能体消息Pydantic模型成功")
        print(f"   消息类型: {test_agent_message.message_type}")
        print(f"   智能体节点: {test_agent_message.agent_node}")
        
        print("\n🎉 所有核心功能测试通过！智能体会话功能正常工作")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent_core()
    sys.exit(0 if success else 1)
