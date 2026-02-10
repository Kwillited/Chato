"""文档数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Document
from app.core.memory_database import memory_db

class DocumentRepository(BaseRepository):
    """文档数据访问类，处理文档相关的数据访问"""
    
    def get_all_documents(self):
        """获取所有文档"""
        # 从内存数据库获取所有文档
        return memory_db.get('documents')
    
    def get_document_by_id(self, document_id):
        """根据ID获取文档"""
        # 从内存数据库获取文档
        return memory_db.get('documents', document_id)
    
    def get_document_by_name(self, document_name):
        """根据名称获取文档"""
        # 从内存数据库查询文档
        documents = memory_db.query('documents', name=document_name)
        return documents[0] if documents else None
    
    def get_documents_by_folder_id(self, folder_id):
        """根据文件夹ID获取文档"""
        # 从内存数据库查询文档
        return memory_db.query('documents', folder_id=folder_id)
    
    def get_documents_by_folder_name(self, folder_name):
        """根据文件夹名称获取文档"""
        # 从内存数据库获取所有文档
        documents = memory_db.get('documents')
        # 从内存数据库获取文件夹
        folders = memory_db.query('folders', name=folder_name)
        if not folders:
            return []
        
        folder_id = folders[0].id
        # 过滤出对应文件夹的文档
        return [doc for doc in documents if doc.folder_id == folder_id]
    
    def create_document(self, document_id, name, path, size, type, uploaded_at, folder_id=None, extra_metadata=None):
        """创建新文档"""
        document = Document(
            id=document_id,
            name=name,
            path=path,
            size=size,
            type=type,
            uploaded_at=uploaded_at,
            folder_id=folder_id,
            extra_metadata=extra_metadata
        )
        return self.add(document)
    
    def update_document(self, document_id, name=None, path=None, size=None, type=None, uploaded_at=None, folder_id=None, extra_metadata=None):
        """更新文档"""
        document = self.get_document_by_id(document_id)
        if document:
            if name is not None:
                document.name = name
            if path is not None:
                document.path = path
            if size is not None:
                document.size = size
            if type is not None:
                document.type = type
            if uploaded_at is not None:
                document.uploaded_at = uploaded_at
            if folder_id is not None:
                document.folder_id = folder_id
            if extra_metadata is not None:
                document.extra_metadata = extra_metadata
            return self.update(document)
        return None
    
    def delete_document(self, document_id):
        """删除文档"""
        document = self.get_document_by_id(document_id)
        if document:
            self.delete(document)
            # 同时删除关联的文档分块
            chunks = memory_db.query('document_chunks', document_id=document_id)
            for chunk in chunks:
                memory_db.delete('document_chunks', chunk.id)
            return True
        return False
    
    def delete_document_by_name(self, document_name, folder_id=None):
        """根据名称删除文档"""
        # 从内存数据库查询文档
        documents = memory_db.query('documents', name=document_name)
        if folder_id:
            documents = [doc for doc in documents if doc.folder_id == folder_id]
        
        if documents:
            document = documents[0]
            self.delete(document)
            # 同时删除关联的文档分块
            chunks = memory_db.query('document_chunks', document_id=document.id)
            for chunk in chunks:
                memory_db.delete('document_chunks', chunk.id)
            return True
        return False
    
    def delete_documents_by_folder_id(self, folder_id):
        """根据文件夹ID删除所有文档"""
        documents = self.get_documents_by_folder_id(folder_id)
        for document in documents:
            self.delete(document)
            # 同时删除关联的文档分块
            chunks = memory_db.query('document_chunks', document_id=document.id)
            for chunk in chunks:
                memory_db.delete('document_chunks', chunk.id)
        return True
    
    def delete_all_documents(self):
        """删除所有文档"""
        # 从内存数据库获取所有文档
        documents = memory_db.get('documents')
        # 删除所有文档及其关联的分块
        for document in documents:
            memory_db.delete('documents', document.id)
            # 删除关联的文档分块
            chunks = memory_db.query('document_chunks', document_id=document.id)
            for chunk in chunks:
                memory_db.delete('document_chunks', chunk.id)
        return True