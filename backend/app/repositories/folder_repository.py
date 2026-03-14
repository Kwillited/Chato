"""文件夹数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Folder

class FolderRepository(BaseRepository):
    """文件夹数据访问类，处理文件夹相关的数据访问"""
    
    def get_all_folders(self):
        """获取所有文件夹"""
        db = self.get_db()
        try:
            return db.query(Folder).all()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹"""
        db = self.get_db()
        try:
            return db.query(Folder).filter(Folder.id == folder_id).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def get_folder_by_name(self, folder_name):
        """根据名称获取文件夹"""
        db = self.get_db()
        try:
            return db.query(Folder).filter(Folder.name == folder_name).first()
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()
    
    def create_folder(self, folder_id, name, path, vector_db_path=None, embedding_model=None, created_at=None, updated_at=None, description=None, chunk_size=1000, chunk_overlap=200):
        """创建新文件夹"""
        folder = Folder(
            id=folder_id,
            name=name,
            path=path,
            vector_db_path=vector_db_path,
            embedding_model=embedding_model,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return self.add(folder)
    
    def update_folder(self, folder_id, name=None, updated_at=None, description=None):
        """更新文件夹"""
        folder = self.get_folder_by_id(folder_id)
        if folder:
            if name is not None:
                folder.name = name
            if updated_at is not None:
                folder.updated_at = updated_at
            if description is not None:
                folder.description = description
            return self.update(folder)
        return None
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        folder = self.get_folder_by_id(folder_id)
        if folder:
            self.delete(folder)
            return True
        return False
    
    def delete_folder_by_name(self, folder_name):
        """根据名称删除文件夹"""
        folder = self.get_folder_by_name(folder_name)
        if folder:
            self.delete(folder)
            return True
        return False
    
    def delete_all_folders(self):
        """删除所有文件夹"""
        db = self.get_db()
        try:
            # 获取所有文件夹并逐个删除
            folders = db.query(Folder).all()
            for folder in folders:
                self.delete(folder)
            return True
        except Exception as e:
            self.rollback()
            raise e
        finally:
            if not hasattr(self, '_db') or not self._db:
                db.close()