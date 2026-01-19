"""文档管理服务 - 负责文档的上传、存储、管理和检索"""
import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from app.core.config import config_manager
from app.services.base_service import BaseService

# 使用config_manager获取标准用户数据目录
user_data_dir = config_manager.get_user_data_dir()

RAG_DIR = os.path.join(user_data_dir, 'Retrieval-Augmented Generation')
DATA_DIR = os.path.join(RAG_DIR, 'files')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class DocumentService(BaseService):
    """文档管理服务类 - 封装所有与文档文件系统相关的操作"""
    
    def __init__(self):
        """初始化文档管理服务"""
        pass
    
    def _get_folder_name_by_id(self, folder_id):
        """根据folder_id查找对应的folder_name"""
        if not folder_id:
            return ''
        
        # 遍历所有文件夹，查找匹配的folder_id
        if os.path.exists(DATA_DIR):
            for item in os.listdir(DATA_DIR):
                item_path = os.path.join(DATA_DIR, item)
                if os.path.isdir(item_path):
                    marker_file_path = os.path.join(item_path, '.kb_marker.json')
                    if os.path.exists(marker_file_path):
                        try:
                            import json
                            with open(marker_file_path, 'r', encoding='utf-8') as f:
                                marker_data = json.load(f)
                                if marker_data.get('id') == folder_id:
                                    return item
                        except Exception:
                            pass
        return folder_id  # 如果找不到，返回原folder_id
    
    def _get_file_save_path(self, filename, folder_name):
        """构建文件保存路径"""
        if folder_name:
            # 如果指定了文件夹，保存到该文件夹
            # 只对文件夹名使用secure_filename，保留文件名中的中文
            folder_path = os.path.join(DATA_DIR, secure_filename(folder_name))
            os.makedirs(folder_path, exist_ok=True)
            # 直接使用原始文件名，确保包含中文
            return os.path.join(folder_path, filename)
        else:
            # 否则保存到根目录，直接使用原始文件名
            return os.path.join(DATA_DIR, filename)
    
    def save_document(self, file, folder_id=''):
        """保存文档到文件系统"""
        # 检查文件名是否为空
        if file.filename == '':
            raise ValueError('文件名不能为空')
        
        # 保留原始文件名，确保中文文件名不被截断
        original_filename = file.filename
        
        # 根据folder_id获取实际的folder_name
        folder_name = self._get_folder_name_by_id(folder_id)
        
        # 确定保存路径，使用原始文件名
        file_path = self._get_file_save_path(original_filename, folder_name)
        
        # 保存文件 - 处理FastAPI UploadFile对象
        with open(file_path, 'wb') as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return {
            'filename': original_filename,
            'full_path': file_path,
            'file_path': original_filename,
            'folder_id': folder_id
        }
    
    def get_documents(self):
        """获取文档列表"""
        # 直接读取目录获取文档列表
        documents = []
        if os.path.exists(DATA_DIR):
            # 递归遍历所有文件
            for root, _, files in os.walk(DATA_DIR):
                for file in files:
                    if os.path.isfile(os.path.join(root, file)) and \
                       not file.startswith('.') and file != 'Thumbs.db':
                        # 计算相对路径
                        relative_path = os.path.relpath(root, DATA_DIR)
                        folder_name = relative_path if relative_path != '.' else ''
                        
                        documents.append({
                            'name': file,
                            'folder': folder_name,
                            'path': os.path.join(root, file)
                        })
        return documents
    
    def delete_document(self, filename, folder_name=''):
        """删除指定文档/文件"""
        # 参数验证
        if not filename:
            raise ValueError('文件名不能为空')
        
        # 构建文件路径，直接使用原始文件名
        if folder_name:
            # 如果指定了文件夹，构建完整路径
            # 只对文件夹名使用secure_filename，保留文件名中的中文
            folder_path = os.path.join(DATA_DIR, secure_filename(folder_name))
            file_path = os.path.join(folder_path, filename)
        else:
            # 在根目录查找文件，直接使用原始文件名
            file_path = os.path.join(DATA_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            # 优化：返回友好的错误信息，而不是抛出异常
            self.log_warning(f"尝试删除不存在的文件: {file_path}")
            return {
                'deleted_file': filename,
                'folder': folder_name,
                'message': f'文档 {filename} 不存在',
                'success': True  # 返回True，因为文件已经不存在
            }
        
        # 删除文件
        try:
            os.remove(file_path)
            return {
                'deleted_file': filename,
                'folder': folder_name,
                'message': f'文档 {filename} 已成功删除',
                'success': True
            }
        except Exception as e:
            self.log_error(f"删除文件 {file_path} 时出错: {e}")
            return {
                'deleted_file': filename,
                'folder': folder_name,
                'message': f'删除文档 {filename} 失败: {str(e)}',
                'success': False
            }
    
    def get_folders(self):
        """获取文件夹列表"""
        # 读取DATA_DIR目录下的所有文件夹
        folders = []
        if os.path.exists(DATA_DIR):
            for item in os.listdir(DATA_DIR):
                item_path = os.path.join(DATA_DIR, item)
                if os.path.isdir(item_path) and not item.startswith('.') and item != 'Thumbs.db':
                    # 尝试从标记文件中读取id
                    folder_id = None
                    marker_file_path = os.path.join(item_path, '.kb_marker.json')
                    if os.path.exists(marker_file_path):
                        try:
                            import json
                            with open(marker_file_path, 'r', encoding='utf-8') as f:
                                marker_data = json.load(f)
                                folder_id = marker_data.get('id')
                        except Exception:
                            pass
                    
                    folders.append({
                        'id': folder_id,
                        'name': item,
                        'path': item_path
                    })
        return folders
    
    def create_folder(self, folder_name):
        """创建文件夹/知识库"""
        if not folder_name:
            raise ValueError('文件夹名称不能为空')
        
        # 安全验证文件夹名称
        folder_name = secure_filename(folder_name)
        
        # 创建文件夹
        folder_path = os.path.join(DATA_DIR, folder_name)
        if os.path.exists(folder_path):
            raise ValueError('文件夹已存在')
        
        os.makedirs(folder_path, exist_ok=True)
        
        # 生成唯一ID
        folder_id = str(uuid.uuid4())[:8]
        
        # 创建标记文件
        marker_file_path = os.path.join(folder_path, '.kb_marker.json')
        import json
        with open(marker_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': folder_id,
                'name': folder_name,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }, f, ensure_ascii=False, indent=2)
        
        return {
            'id': folder_id,
            'name': folder_name,
            'path': folder_path,
            'message': f'文件夹 {folder_name} 创建成功'
        }
    
    def get_files_in_folder(self, folder_name):
        """获取指定文件夹中的文件"""
        # 构建文件夹路径
        folder_path = os.path.join(DATA_DIR, folder_name)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise ValueError('文件夹不存在')
        
        # 读取文件夹中的文件
        files = []
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and not file.startswith('.') and file != 'Thumbs.db':
                files.append({
                    'name': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified_at': os.path.getmtime(file_path)
                })
        return files
    
    def delete_all_documents(self):
        """删除所有文档，包括所有文件夹和文件"""
        # 先检查DATA_DIR是否存在
        if not os.path.exists(DATA_DIR):
            return {
                'deleted_count': 0,
                'skipped_count': 0,
                'message': '没有文档需要删除',
                'success': True
            }
        
        # 统计删除的文件数量和跳过的文件数量
        deleted_count = 0
        skipped_count = 0
        
        # 递归删除所有文件和文件夹
        for root, dirs, files in os.walk(DATA_DIR, topdown=False):
            # 先删除所有文件
            for file in files:
                if not file.startswith('.') and file != 'Thumbs.db':
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        self.log_error(f"删除文件 {file_path} 时出错: {e}")
                        skipped_count += 1
            
            # 然后删除所有子目录
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    self.log_error(f"删除目录 {dir_path} 时出错: {e}")
                    skipped_count += 1
        
        # 重新初始化DATA_DIR目录（如果被删除）
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 构建返回消息
        message = f'已删除 {deleted_count} 个文件和所有文件夹'
        if skipped_count > 0:
            message += f'，跳过了 {skipped_count} 个无法删除的项目'
        
        return {
            'deleted_count': deleted_count,
            'skipped_count': skipped_count,
            'message': message,
            'success': True
        }
    
    def delete_folder(self, folder_name):
        """删除文件夹/知识库"""
        if not folder_name:
            raise ValueError('文件夹名称不能为空')
        
        # 安全验证文件夹名称
        folder_name = secure_filename(folder_name)
        
        # 构建文件夹路径
        folder_path = os.path.join(DATA_DIR, folder_name)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            self.log_warning(f"尝试删除不存在的文件夹: {folder_path}")
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 不存在',
                'success': True  # 返回True，因为文件夹已经不存在
            }
        
        # 删除文件夹及其所有内容
        try:
            shutil.rmtree(folder_path)
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 已成功删除',
                'success': True
            }
        except Exception as e:
            self.log_error(f"删除文件夹 {folder_path} 时出错: {e}")
            return {
                'deleted_folder': folder_name,
                'message': f'删除文件夹 {folder_name} 失败: {str(e)}',
                'success': False
            }
