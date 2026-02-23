"""Pydantic模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class MessageBase(BaseModel):
    """消息基础模型"""
    role: str
    content: str
    model: Optional[str] = None
    reasoning_content: Optional[str] = None


class MessageCreate(MessageBase):
    """创建消息模型"""
    chat_id: str
    files: Optional[List[dict]] = Field(default_factory=list)


class Message(MessageBase):
    """消息响应模型"""
    id: str
    createdAt: str
    files: Optional[List[dict]] = Field(default_factory=list)
    message_type: str = "normal"
    agent_session_id: Optional[str] = None
    agent_node: str = ""
    agent_step: int = 0
    agent_metadata: Optional[str] = ""
    
    class Config:
        from_attributes = True


class AgentMessage(Message):
    """智能体消息响应模型"""
    message_type: str = "agent"
    agent_session_id: Optional[str] = None
    agent_node: str = ""
    agent_step: int = 0
    agent_metadata: Optional[str] = ""
    
    class Config:
        from_attributes = True


class ChatBase(BaseModel):
    """对话基础模型"""
    title: str
    preview: Optional[str] = ""


class ChatUpdate(ChatBase):
    """更新对话模型"""
    pinned: Optional[int] = 0
    updated_at: Optional[str] = None


class Chat(ChatBase):
    """对话响应模型"""
    id: str
    createdAt: str
    updatedAt: str
    pinned: Optional[int] = 0
    messages: List[Message] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    """对话列表响应模型"""
    chats: List[Chat]


class ChatResponse(BaseModel):
    """单个对话响应模型"""
    chat: Chat



class PinUpdateRequest(BaseModel):
    """更新对话置顶状态请求模型"""
    pinned: int = Field(..., ge=0, le=1, description="0: 取消置顶, 1: 置顶")


class PinUpdateResponse(BaseModel):
    """更新对话置顶状态响应模型"""
    success: bool
    message: str


class DeleteChatResponse(BaseModel):
    """删除对话响应模型"""
    success: bool
    message: str


class ModelParam(BaseModel):
    """模型参数模型"""
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0.1, le=1.0)
    top_k: Optional[int] = Field(default=50, ge=1, le=100)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=0.0, le=2.0)


class RAGConfig(BaseModel):
    """RAG配置模型"""
    enabled: bool = False
    chunk_size: int = 1000
    chunk_overlap: int = 100
    k: int = 4
    knowledgeBasePath: str = ""
    retrievalMode: str = "vector"
    scoreThreshold: float = 0.7
    selectedFolders: List[str] = Field(default_factory=list)
    selectedKnowledgeBases: List[str] = Field(default_factory=list)
    topK: int = 3
    vectorDbPath: str = ""
    embedderModel: str = "qwen3-embedding-0.6b"


class FileInfo(BaseModel):
    """文件信息模型"""
    name: str
    content: str
    type: Optional[str] = None
    size: Optional[int] = None


class SendMessageRequest(BaseModel):
    """发送消息请求模型"""
    message: str = Field("", description="消息内容")
    model: str = Field(..., description="模型名称")
    modelParams: Optional[ModelParam] = Field(default_factory=ModelParam)
    ragConfig: Optional[RAGConfig] = Field(default_factory=RAGConfig)
    stream: Optional[bool] = False
    deepThinking: Optional[bool] = False
    agent: Optional[bool] = False
    files: Optional[List[FileInfo]] = Field(default_factory=list)


class ModelBase(BaseModel):
    """模型基础模型"""
    name: str
    description: Optional[str] = None
    configured: bool = False
    enabled: bool = False
    icon_class: Optional[str] = None
    icon_bg: Optional[str] = None
    icon_color: Optional[str] = None
    icon_url: Optional[str] = None
    icon_blob: Optional[str] = None


class ModelCreate(ModelBase):
    """创建模型模型"""
    pass


class ModelVersionBase(BaseModel):
    """模型版本基础模型"""
    version_name: str
    custom_name: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    streaming_config: bool = False


class ModelVersionCreate(ModelVersionBase):
    """创建模型版本模型"""
    model_id: int


class ModelResponse(ModelBase):
    """模型响应模型"""
    id: int
    versions: List[ModelVersionBase] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ModelVersionResponse(ModelVersionBase):
    """模型版本响应模型"""
    id: int
    model_id: int
    
    class Config:
        from_attributes = True








class SystemSettings(BaseModel):
    """系统设置模型"""
    dark_mode: bool = False
    streaming_enabled: bool = True
    chat_style: str = "bubble"
    view_mode: str = "grid"
    default_model: str = ""
    # 通知相关字段
    newMessage: bool = True
    sound: bool = False
    system: bool = True
    displayTime: str = "5秒"


class PatchSystemSettings(BaseModel):
    """系统设置PATCH模型"""
    dark_mode: bool | None = None
    streaming_enabled: bool | None = None
    chat_style: str | None = None
    view_mode: str | None = None
    default_model: str | None = None
    # 通知相关字段
    newMessage: bool | None = None
    sound: bool | None = None
    system: bool | None = None
    displayTime: str | None = None


class SettingResponse(BaseModel):
    """设置响应模型"""
    message: str
    settings: dict


# RAG相关模型
class DocumentInfo(BaseModel):
    """文档信息模型"""
    name: str
    folder: str
    path: str


class FolderInfo(BaseModel):
    """文件夹信息模型"""
    id: Optional[str] = None
    name: str
    path: str


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool
    message: str
    file_path: str


class DocumentListResponse(BaseModel):
    """文档列表响应模型"""
    success: bool
    documents: List[DocumentInfo]
    folder_id_map: Optional[dict] = None


class FolderListResponse(BaseModel):
    """文件夹列表响应模型"""
    success: bool
    folders: List[FolderInfo]


class FolderCreateResponse(BaseModel):
    """创建文件夹响应模型"""
    success: bool
    message: str
    id: str
    name: str
    path: str
    embedding_model: Optional[str] = "qwen3-embedding-0.6b"


class FilesInFolderResponse(BaseModel):
    """文件夹文件列表响应模型"""
    success: bool
    files: List[dict]
    folder_id: Optional[str] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    success: bool
    results: List[dict]


class DocumentDetailsResponse(BaseModel):
    """文档详情响应模型"""
    success: bool
    details: dict


class DocumentDeleteResponse(BaseModel):
    """删除文档响应模型"""
    success: bool
    message: str
    deleted_file: str
    folder: str


class FolderDeleteResponse(BaseModel):
    """删除文件夹响应模型"""
    success: bool
    message: str
    deleted_folder: str
    folder_id: Optional[str] = None


class DeleteAllResponse(BaseModel):
    """删除所有文档响应模型"""
    success: bool
    message: str
    deleted_count: int


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool
    message: str


# 智能体会话相关模型
class AgentSessionBase(BaseModel):
    """智能体会话基础模型"""
    chat_id: str
    graph_state: Optional[str] = None
    current_node: str = ""
    step_count: int = 0


class AgentSessionCreate(AgentSessionBase):
    """创建智能体会话模型"""
    pass


class AgentSessionUpdate(BaseModel):
    """更新智能体会话模型"""
    graph_state: Optional[str] = None
    current_node: Optional[str] = None
    step_count: Optional[int] = None


class AgentSession(AgentSessionBase):
    """智能体会话响应模型"""
    id: str
    createdAt: str
    updatedAt: str
    messages: Optional[List[AgentMessage]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class AgentSessionListResponse(BaseModel):
    """智能体会话列表响应模型"""
    sessions: List[AgentSession]


class AgentSessionResponse(BaseModel):
    """单个智能体会话响应模型"""
    session: AgentSession


class AgentSessionCreateResponse(BaseModel):
    """创建智能体会话响应模型"""
    session: AgentSession
