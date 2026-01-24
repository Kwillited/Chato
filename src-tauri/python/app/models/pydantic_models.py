"""Pydantic模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Generic, TypeVar
from datetime import datetime

# 泛型类型变量
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    version: str = "1.0.0"


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


class ChatListResponse(BaseResponse[List[Chat]]):
    """对话列表响应模型"""
    data: List[Chat] = Field(default_factory=list)


class ChatResponse(BaseResponse[Chat]):
    """单个对话响应模型"""
    data: Optional[Chat] = None


class ChatCreateResponse(BaseResponse[Chat]):
    """创建对话响应模型"""
    data: Optional[Chat] = None


class PinUpdateRequest(BaseModel):
    """更新对话置顶状态请求模型"""
    pinned: int = Field(..., ge=0, le=1, description="0: 取消置顶, 1: 置顶")


class PinUpdateResponse(BaseResponse):
    """更新对话置顶状态响应模型"""
    pass


class DeleteChatResponse(BaseResponse):
    """删除对话响应模型"""
    pass


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


class SystemSettings(BaseModel):
    """系统设置模型"""
    dark_mode: bool = False
    font_size: int = 14
    chat_style_document: bool = False
    view_mode: str = "grid"
    show_hidden_files: bool = False
    auto_refresh_files: bool = True
    max_recent_files: int = 10


class SettingResponse(BaseResponse[dict]):
    """设置响应模型"""
    data: Optional[dict] = None


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


class FileUploadResponse(BaseResponse[dict]):
    """文件上传响应模型"""
    data: Optional[dict] = None


class DocumentListResponse(BaseResponse[dict]):
    """文档列表响应模型"""
    data: Optional[dict] = None


class FolderListResponse(BaseResponse[List[FolderInfo]]):
    """文件夹列表响应模型"""
    data: List[FolderInfo] = Field(default_factory=list)


class FolderCreateResponse(BaseResponse[dict]):
    """创建文件夹响应模型"""
    data: Optional[dict] = None


class FilesInFolderResponse(BaseResponse[dict]):
    """文件夹文件列表响应模型"""
    data: Optional[dict] = None


class SearchResponse(BaseResponse[List[dict]]):
    """搜索响应模型"""
    data: List[dict] = Field(default_factory=list)


class DocumentDetailsResponse(BaseResponse[dict]):
    """文档详情响应模型"""
    data: Optional[dict] = None


class DocumentDeleteResponse(BaseResponse[dict]):
    """删除文档响应模型"""
    data: Optional[dict] = None


class FolderDeleteResponse(BaseResponse[dict]):
    """删除文件夹响应模型"""
    data: Optional[dict] = None


class DeleteAllResponse(BaseResponse[dict]):
    """删除所有文档响应模型"""
    data: Optional[dict] = None


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = False
    


class SuccessResponse(BaseResponse):
    """成功响应模型"""
    pass
