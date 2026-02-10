"""测试删除所有对话功能"""
import pytest
from app.services.chat.chat_service import ChatService
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.data_service import DataService

class TestDeleteAllChats:
    """测试删除所有对话功能"""
    
    def setup_method(self):
        """测试前的设置"""
        # 初始化测试数据
        self.chat_repo = ChatRepository()
        self.message_repo = MessageRepository()
        self.chat_service = ChatService(self.chat_repo, self.message_repo)
        
        # 清空内存数据
        DataService.clear_chats()
        
        # 清空数据库数据
        self.message_repo.delete_all_messages()
        self.chat_repo.delete_all_chats()
    
    def teardown_method(self):
        """测试后的清理"""
        # 清空测试数据
        self.message_repo.delete_all_messages()
        self.chat_repo.delete_all_chats()
        DataService.clear_chats()
    
    def test_delete_all_chats_with_no_chats(self):
        """测试删除空对话列表"""
        # 当没有对话时，删除所有对话应该返回True
        result = self.chat_service.delete_all_chats()
        assert result is True
        
        # 验证数据库和内存中都没有对话
        chats = self.chat_repo.get_all_chats()
        assert len(chats) == 0
        assert len(DataService.get_chats()) == 0
    
    def test_delete_all_chats_with_multiple_chats(self):
        """测试删除多个对话"""
        # 创建两个测试对话
        import uuid
        from datetime import datetime
        chat_id1 = str(uuid.uuid4())
        now = datetime.now().isoformat()
        chat1 = {
            'id': chat_id1,
            'title': "测试对话1",
            'preview': '',
            'createdAt': now,
            'updatedAt': now,
            'messages': []
        }
        DataService.add_chat(chat1)
        
        chat_id2 = str(uuid.uuid4())
        chat2 = {
            'id': chat_id2,
            'title': "测试对话2",
            'preview': '',
            'createdAt': now,
            'updatedAt': now,
            'messages': []
        }
        DataService.add_chat(chat2)
        
        # 验证对话已创建
        assert len(DataService.get_chats()) == 2
        
        # 删除所有对话
        result = self.chat_service.delete_all_chats()
        assert result is True
        
        # 验证数据库和内存中都没有对话
        chats = self.chat_repo.get_all_chats()
        assert len(chats) == 0
        assert len(DataService.get_chats()) == 0
    
    def test_delete_all_chats_with_messages(self):
        """测试删除包含消息的对话"""
        # 创建一个测试对话
        import uuid
        from datetime import datetime
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        chat = {
            'id': chat_id,
            'title': "测试对话",
            'preview': '',
            'createdAt': now,
            'updatedAt': now,
            'messages': []
        }
        DataService.add_chat(chat)
        
        # 创建一个测试消息
        from app.repositories.message_repository import MessageRepository
        message_repo = MessageRepository()
        from datetime import datetime
        now = datetime.now().isoformat()
        message_repo.create_message(
            message_id="test-message-1",
            chat_id=chat_id,
            role="user",
            content="测试消息",
            reasoning_content=None,
            created_at=now,
            model="test-model"
        )
        
        # 验证对话和消息已创建
        chat_from_db = self.chat_repo.get_chat_by_id(chat_id)
        assert chat_from_db is not None
        messages = self.message_repo.get_messages_by_chat_id(chat_id)
        assert len(messages) == 1
        
        # 删除所有对话
        result = self.chat_service.delete_all_chats()
        assert result is True
        
        # 验证数据库和内存中都没有对话和消息
        chats = self.chat_repo.get_all_chats()
        assert len(chats) == 0
        messages = self.message_repo.get_messages_by_chat_id(chat_id)
        assert len(messages) == 0
        assert len(DataService.get_chats()) == 0
    
    def test_delete_all_chats_service_layer(self):
        """测试Service层的delete_all_chats方法"""
        # 创建一个测试对话
        import uuid
        from datetime import datetime
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        chat = {
            'id': chat_id,
            'title': "测试对话",
            'preview': '',
            'createdAt': now,
            'updatedAt': now,
            'messages': []
        }
        DataService.add_chat(chat)
        
        # 验证对话已创建
        assert len(DataService.get_chats()) == 1
        
        # 调用API路由中的delete_all_chats函数
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.delete("/api/chats/delete-all")
        
        # 验证响应
        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "所有对话已删除"}
        
        # 验证对话已删除
        assert len(DataService.get_chats()) == 0