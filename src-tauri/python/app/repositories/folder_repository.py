"""文件夹数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.models import Folder

class FolderRepository(BaseRepository):
    """文件夹数据访问类，处理文件夹相关的数据访问"""
    
    def get_all_folders(self):
        """获取所有文件夹"""
        return self.db.query(Folder).all()
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹"""
        return self.db.query(Folder).filter(Folder.id == folder_id).first()
    
    def get_folder_by_name(self, folder_name):
        """根据名称获取文件夹"""
        return self.db.query(Folder).filter(Folder.name == folder_name).first()
    
    def create_folder(self, folder_id, name, created_at, updated_at, description=""):
        """创建新文件夹"""
        folder = Folder(
            id=folder_id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            description=description
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