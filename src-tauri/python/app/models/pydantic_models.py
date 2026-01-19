"""Pydantic模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class MessageBase(BaseModel):
    """消息基础模型"""
    role: str
    content: str
    model: Optional[str] = None
    thinking: Optional[str] = None


class MessageCreate(MessageBase):
    """创建消息模型"""
    chat_id: str
    files: Optional[List[dict]] = Field(default_factory=list)


class Message(MessageBase):
    """消息响应模型"""
    id: str
    createdAt: str
    files: Optional[List[dict]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ChatBase(BaseModel):
    """对话基础模型"""
    title: str
    preview: Optional[str] = ""


class ChatCreate(ChatBase):
    """创建对话模型"""
    pass


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


class ChatCreateResponse(BaseModel):
    """创建对话响应模型"""
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
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
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
    vectorDbType: str = "chroma"
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


class NotificationSettings(BaseModel):
    """通知设置模型"""
    enabled: bool = True
    newMessage: bool = True
    sound: bool = False
    system: bool = True
    displayTime: str = "5秒"


class MCPSettings(BaseModel):
    """MCP设置模型"""
    enabled: bool = False
    server_address: str = ""
    server_port: int = 8080
    timeout: int = 30


class BasicSettings(BaseModel):
    """基本设置模型"""
    theme: str = "light"
    language: str = "zh-CN"
    autoSave: bool = True
    showPreview: bool = True
    maxMessages: int = 100


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
