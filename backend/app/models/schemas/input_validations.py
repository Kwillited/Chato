"""输入验证模型 - 使用Pydantic进行API输入验证"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., min_length=1, max_length=1000, description="搜索查询文本")
    k: int = Field(5, ge=1, le=100, description="返回结果数量")
    score_threshold: Optional[float] = Field(None, ge=0, le=1, description="相似度分数阈值")
    search_type: str = Field("similarity", pattern="^(similarity|mmr|similarity_score_threshold)$", description="搜索类型")
    fetch_k: int = Field(20, ge=1, le=200, description="用于MMR搜索的候选文档数量")
    filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤器")

class AddDocumentRequest(BaseModel):
    """添加文档请求模型"""
    file_path: str = Field(..., description="文档文件路径")
    knowledge_base: str = Field("default", description="知识库名称")
    chunk_size: int = Field(1000, ge=100, le=5000, description="文档分块大小")
    chunk_overlap: int = Field(200, ge=0, le=1000, description="文档分块重叠大小")

class DeleteDocumentRequest(BaseModel):
    """删除文档请求模型"""
    document_ids: List[str] = Field(..., min_items=1, description="要删除的文档ID列表")
    knowledge_base: str = Field("default", description="知识库名称")

class ClearKnowledgeBaseRequest(BaseModel):
    """清空知识库请求模型"""
    knowledge_base: str = Field(..., description="知识库名称")

class GetKnowledgeBasesRequest(BaseModel):
    """获取知识库列表请求模型"""
    pass

class KnowledgeBaseInfo(BaseModel):
    """知识库信息响应模型"""
    name: str = Field(..., description="知识库名称")
    path: str = Field(..., description="知识库路径")
    embedding_model: str = Field(..., description="嵌入模型名称")
    document_count: int = Field(..., description="文档数量")

class UpdateKnowledgeBaseRequest(BaseModel):
    """更新知识库请求模型"""
    name: str = Field(..., description="知识库名称")
    new_name: Optional[str] = Field(None, description="新的知识库名称")
    new_path: Optional[str] = Field(None, description="新的向量数据库路径")
    new_embedder_model: Optional[str] = Field(None, description="新的嵌入模型名称")

class DeleteKnowledgeBaseRequest(BaseModel):
    """删除知识库请求模型"""
    name: str = Field(..., description="知识库名称")

class RAGConfigRequest(BaseModel):
    """RAG配置请求模型"""
    enabled: bool = Field(..., description="是否启用RAG")
    retrieval_mode: str = Field(..., pattern="^(vector|hybrid|keyword)$", description="检索模式")
    top_k: int = Field(..., ge=1, le=100, description="返回结果数量")
    score_threshold: float = Field(..., ge=0, le=1, description="相似度分数阈值")
    embedder_model: str = Field(..., description="嵌入模型名称")

class ModelConfigRequest(BaseModel):
    """模型配置请求模型"""
    model_name: str = Field(..., description="模型名称")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="模型API基础URL")
    temperature: float = Field(..., ge=0, le=2, description="生成温度")
    max_tokens: int = Field(..., ge=1, le=10000, description="最大生成 tokens 数")

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="检查时间戳")
    components: Dict[str, str] = Field(..., description="组件状态")

# 验证器示例
class ExampleRequest(BaseModel):
    """示例请求模型"""
    name: str = Field(..., description="名称")
    age: int = Field(..., description="年龄")
    
    @validator('age')
    def age_must_be_adult(cls, v):
        """验证年龄必须是成年人"""
        if v < 18:
            raise ValueError('年龄必须大于等于18岁')
        return v
