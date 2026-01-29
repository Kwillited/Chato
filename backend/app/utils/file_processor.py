"""文件处理工具类，提供统一的文件处理功能"""
import os
import tempfile
import base64
from app.utils.logging_utils import LoggingUtils

class FileProcessor:
    """文件处理工具类，封装所有文件处理方法"""
    
    @staticmethod
    def _save_uploaded_file(file, temp_dir):
        """保存上传的文件到临时目录"""
        file_name = file['name']
        file_content_base64 = file['content']
        
        try:
            # 解码base64内容
            file_content = base64.b64decode(file_content_base64)
            
            # 保存到临时文件
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path
        except Exception as decode_error:
            LoggingUtils.log_error(f"解码文件 {file_name} 失败: {str(decode_error)}")
            return None
    
    @staticmethod
    def _process_text_file(file_path, file_name):
        """处理文本类文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _process_pdf_file(file_path, file_name):
        """处理PDF文件"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + '\n'
            return content
        except ImportError:
            return f"[PDF文件内容，无法提取，请安装PyPDF2库]"
        except Exception as e:
            LoggingUtils.log_error(f"处理PDF文件 {file_name} 失败: {str(e)}")
            return f"[PDF文件内容，处理失败: {str(e)}]"
    
    @staticmethod
    def _process_word_file(file_path, file_name):
        """处理Word文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            content = ""
            for para in doc.paragraphs:
                content += para.text + '\n'
            return content
        except ImportError:
            return f"[Word文件内容，无法提取，请安装python-docx库]"
        except Exception as e:
            LoggingUtils.log_error(f"处理Word文件 {file_name} 失败: {str(e)}")
            return f"[Word文件内容，处理失败: {str(e)}]"
    
    @staticmethod
    def _extract_file_content(file_path, file_name):
        """根据文件类型提取内容"""
        # 根据文件扩展名选择提取方式
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 只处理文本类文件
        if file_ext in ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml']:
            return FileProcessor._process_text_file(file_path, file_name)
        elif file_ext in ['.pdf']:
            return FileProcessor._process_pdf_file(file_path, file_name)
        elif file_ext in ['.doc', '.docx']:
            return FileProcessor._process_word_file(file_path, file_name)
        else:
            # 其他文件类型，只显示文件信息
            return f"[无法提取该类型文件的内容：{file_name}]"
    
    @staticmethod
    def process_uploaded_files(files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        extracted_contents = []
        
        if not files:
            return extracted_contents
        
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            for file in files:
                # 检查文件结构
                if isinstance(file, dict) and 'name' in file and 'content' in file:
                    # 保存到临时文件
                    file_path = FileProcessor._save_uploaded_file(file, temp_dir)
                    if file_path:
                        # 提取文件内容
                        content = FileProcessor._extract_file_content(file_path, file['name'])
                        if content:
                            extracted_contents.append(f"文件 {file['name']} 内容：\n{content}")
        except Exception as e:
            # 记录错误但不中断流程
            LoggingUtils.log_error(f"处理上传文件失败: {str(e)}")
        
        return extracted_contents
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息
        
        参数:
            file_path: 文件路径
        
        返回:
            文件信息字典
        """
        try:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                return {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'size': file_stat.st_size,
                    'modified_at': file_stat.st_mtime,
                    'exists': True
                }
            else:
                return {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'exists': False
                }
        except Exception as e:
            LoggingUtils.log_error(f"获取文件信息失败: {str(e)}")
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'error': str(e)
            }
    
    @staticmethod
    def validate_file_type(file_name, allowed_extensions):
        """验证文件类型
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表
        
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f'不支持的文件类型: {file_ext}，允许的类型: {allowed_extensions}'
        return True, None