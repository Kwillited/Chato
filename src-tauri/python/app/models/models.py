"""SQLAlchemy模型定义"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Model(Base):
    """模型信息表"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    configured = Column(Boolean, default=False)
    enabled = Column(Boolean, default=False)
    icon_class = Column(String)
    icon_bg = Column(String)
    icon_color = Column(String)
    icon_url = Column(String)
    icon_blob = Column(Text)  # SQLite中使用TEXT存储二进制数据
    
    # 关系：一个模型可以有多个版本
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")


class ModelVersion(Base):
    """模型版本表"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    version_name = Column(String, nullable=False)
    custom_name = Column(String)
    api_key = Column(String)
    api_base_url = Column(String)
    streaming_config = Column(Boolean, default=False)
    
    # 关系：多个版本属于一个模型
    model = relationship("Model", back_populates="versions")
    
    # 唯一约束：一个模型不能有重复的版本名称
    __table_args__ = ({
        'sqlite_autoincrement': True,
        'extend_existing': True
    })


class Chat(Base):
    """对话表"""
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    preview = Column(Text)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    pinned = Column(Integer, default=0)
    
    # 关系：一个对话可以有多个消息
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    actual_content = Column(Text, nullable=False)
    thinking = Column(Text)
    created_at = Column(String, nullable=False)
    model = Column(String)
    files = Column(Text)  # 存储JSON格式的文件信息
    
    # 关系：多个消息属于一个对话
    chat = relationship("Chat", back_populates="messages")


class Setting(Base):
    """设置表"""
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


class Folder(Base):
    """文件夹/知识库表"""
    __tablename__ = "folders"
    
    id = Column(String, primary_key=True)  # 使用UUID前8位
    name = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    description = Column(Text)
    
    # 关系：一个文件夹包含多个文档
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)  # 文件系统路径
    size = Column(Integer)  # 文件大小
    type = Column(String)  # 文件类型
    uploaded_at = Column(String, nullable=False)
    folder_id = Column(String, ForeignKey("folders.id", ondelete="SET NULL"))
    extra_metadata = Column(Text)  # JSON格式的扩展元数据
    
    # 关系：属于一个文件夹
    folder = relationship("Folder", back_populates="documents")
    
    # 关系：一个文档包含多个分块
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """文档分块表"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index = Column(Integer)  # 分块索引
    content = Column(Text, nullable=False)  # 分块内容
    extra_metadata = Column(Text)  # 分块元数据
    vector_id = Column(String)  # Chroma向量ID
    vector_collection = Column(String)  # 向量所属集合
    
    # 关系：属于一个文档
    document = relationship("Document", back_populates="chunks")