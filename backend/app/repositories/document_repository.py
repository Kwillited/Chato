"""文档数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Document

class DocumentRepository(BaseRepository):
    """文档数据访问类，处理文档相关的数据访问"""
    
    def get_all_documents(self):
        """获取所有文档"""
        return self.db.query(Document).all()
    
    def get_document_by_id(self, document_id):
        """根据ID获取文档"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_document_by_name(self, document_name):
        """根据名称获取文档"""
        return self.db.query(Document).filter(Document.name == document_name).first()
    
    def get_documents_by_folder_id(self, folder_id):
        """根据文件夹ID获取文档"""
        return self.db.query(Document).filter(Document.folder_id == folder_id).all()
    
    def get_documents_by_folder_name(self, folder_name):
        """根据文件夹名称获取文档"""
        return self.db.query(Document).join(Document.folder).filter(folder_name == Document.folder.name).all()
    
    def create_document(self, document_id, name, path, size, type, uploaded_at, folder_id=None, extra_metadata=None, chunk_size=1000, chunk_overlap=200):
        """创建新文档"""
        document = Document(
            id=document_id,
            name=name,
            path=path,
            size=size,
            type=type,
            uploaded_at=uploaded_at,
            folder_id=folder_id,
            extra_metadata=extra_metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
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
            return True
        return False
    
    def delete_document_by_name(self, document_name, folder_id=None):
        """根据名称删除文档"""
        query = self.db.query(Document).filter(Document.name == document_name)
        if folder_id:
            query = query.filter(Document.folder_id == folder_id)
        document = query.first()
        if document:
            self.delete(document)
            return True
        return False
    
    def delete_documents_by_folder_id(self, folder_id):
        """根据文件夹ID删除所有文档"""
        documents = self.get_documents_by_folder_id(folder_id)
        for document in documents:
            self.delete(document)
        return True
    
    def delete_all_documents(self):
        """删除所有文档"""
        try:
            # 删除所有文档
            self.db.query(Document).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e