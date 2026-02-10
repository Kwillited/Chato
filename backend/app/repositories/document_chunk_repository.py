"""文档分块数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import DocumentChunk
from app.core.memory_database import memory_db

class DocumentChunkRepository(BaseRepository):
    """文档分块数据访问类，处理文档分块相关的数据访问"""
    
    def get_all_chunks(self):
        """获取所有文档分块"""
        # 从内存数据库获取所有文档分块
        return memory_db.get('document_chunks')
    
    def get_chunk_by_id(self, chunk_id):
        """根据ID获取文档分块"""
        # 从内存数据库获取文档分块
        return memory_db.get('document_chunks', chunk_id)
    
    def get_chunks_by_document_id(self, document_id):
        """根据文档ID获取所有分块"""
        # 从内存数据库查询文档分块
        chunks = memory_db.query('document_chunks', document_id=document_id)
        # 按chunk_index排序
        return sorted(chunks, key=lambda x: x.chunk_index)
    
    def get_chunks_by_vector_id(self, vector_id):
        """根据向量ID获取文档分块"""
        # 从内存数据库查询文档分块
        chunks = memory_db.query('document_chunks', vector_id=vector_id)
        return chunks[0] if chunks else None
    
    def create_chunk(self, chunk_id, document_id, chunk_index, content, extra_metadata=None, vector_id=None, vector_collection=None):
        """创建新文档分块"""
        chunk = DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            extra_metadata=extra_metadata,
            vector_id=vector_id,
            vector_collection=vector_collection
        )
        return self.add(chunk)
    
    def create_chunks_batch(self, chunks):
        """批量创建文档分块"""
        # 批量添加文档分块到内存数据库
        for chunk in chunks:
            self.add(chunk)
        return chunks
    
    def update_chunk(self, chunk_id, content=None, extra_metadata=None, vector_id=None, vector_collection=None):
        """更新文档分块"""
        chunk = self.get_chunk_by_id(chunk_id)
        if chunk:
            if content is not None:
                chunk.content = content
            if extra_metadata is not None:
                chunk.extra_metadata = extra_metadata
            if vector_id is not None:
                chunk.vector_id = vector_id
            if vector_collection is not None:
                chunk.vector_collection = vector_collection
            return self.update(chunk)
        return None
    
    def delete_chunk(self, chunk_id):
        """删除文档分块"""
        chunk = self.get_chunk_by_id(chunk_id)
        if chunk:
            self.delete(chunk)
            return True
        return False
    
    def delete_chunks_by_document_id(self, document_id):
        """根据文档ID删除所有分块"""
        chunks = self.get_chunks_by_document_id(document_id)
        for chunk in chunks:
            self.delete(chunk)
        return True
    
    def delete_chunks_by_vector_collection(self, vector_collection):
        """根据向量集合删除所有分块"""
        # 从内存数据库查询文档分块
        chunks = memory_db.query('document_chunks', vector_collection=vector_collection)
        for chunk in chunks:
            self.delete(chunk)
        return True