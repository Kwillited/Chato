"""文件夹数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Folder
from app.core.memory_database import memory_db

class FolderRepository(BaseRepository):
    """文件夹数据访问类，处理文件夹相关的数据访问"""
    
    def get_all_folders(self):
        """获取所有文件夹"""
        # 从内存数据库获取所有文件夹
        return memory_db.get('folders')
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹"""
        # 从内存数据库获取文件夹
        return memory_db.get('folders', folder_id)
    
    def get_folder_by_name(self, folder_name):
        """根据名称获取文件夹"""
        # 从内存数据库查询文件夹
        folders = memory_db.query('folders', name=folder_name)
        return folders[0] if folders else None
    
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
    
    def delete_all_folders(self):
        """删除所有文件夹"""
        # 从内存数据库获取所有文件夹
        folders = memory_db.get('folders')
        # 删除所有文件夹
        for folder in folders:
            memory_db.delete('folders', folder.id)
        return True