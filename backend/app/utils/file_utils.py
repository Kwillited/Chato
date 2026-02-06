"""文件工具类，提供统一的文件操作功能"""
import os
import tempfile
import base64
from app.utils.logging_utils import LoggingUtils


class FileUtils:
    """文件工具类，封装所有文件操作方法"""
    
    # 文件扩展名常量
    TEXT_EXTENSIONS = ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml']
    PDF_EXTENSIONS = ['.pdf']
    WORD_EXTENSIONS = ['.doc', '.docx']
    SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS + PDF_EXTENSIONS + WORD_EXTENSIONS
    
    @staticmethod
    def get_file_extension(file_name):
        """
        获取文件扩展名
        
        参数:
            file_name: 文件名
            
        返回:
            文件扩展名（小写）
        """
        return os.path.splitext(file_name)[1].lower()
    
    @staticmethod
    def is_text_file(file_name):
        """
        判断是否为文本文件
        
        参数:
            file_name: 文件名
            
        返回:
            是否为文本文件
        """
        return FileUtils.get_file_extension(file_name) in FileUtils.TEXT_EXTENSIONS
    
    @staticmethod
    def is_pdf_file(file_name):
        """
        判断是否为PDF文件
        
        参数:
            file_name: 文件名
            
        返回:
            是否为PDF文件
        """
        return FileUtils.get_file_extension(file_name) in FileUtils.PDF_EXTENSIONS
    
    @staticmethod
    def is_word_file(file_name):
        """
        判断是否为Word文件
        
        参数:
            file_name: 文件名
            
        返回:
            是否为Word文件
        """
        return FileUtils.get_file_extension(file_name) in FileUtils.WORD_EXTENSIONS
    
    @staticmethod
    def is_supported_file(file_name):
        """
        判断是否为支持的文件类型
        
        参数:
            file_name: 文件名
            
        返回:
            是否为支持的文件类型
        """
        return FileUtils.is_text_file(file_name) or FileUtils.is_pdf_file(file_name) or FileUtils.is_word_file(file_name)
    
    @staticmethod
    def _save_uploaded_file(file, temp_dir, max_size=10*1024*1024):
        """
        保存上传的文件到临时目录
        
        参数:
            file: 文件字典
            temp_dir: 临时目录
            max_size: 文件大小限制（默认10MB）
            
        返回:
            文件路径或 None
        """
        file_name = file['name']
        file_content_base64 = file['content']
        
        try:
            # 清理文件名，防止路径遍历
            file_name = os.path.basename(file_name)
            
            # 检查base64内容大小
            if len(file_content_base64) * 3/4 > max_size:
                LoggingUtils.log_error(f"文件 {file_name} 超过大小限制")
                return None
            
            # 解码base64内容
            file_content = base64.b64decode(file_content_base64)
            
            # 再次检查文件大小
            if len(file_content) > max_size:
                LoggingUtils.log_error(f"文件 {file_name} 超过大小限制")
                return None
            
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
        """
        处理文本类文件
        
        参数:
            file_path: 文件路径
            file_name: 文件名
            
        返回:
            文件内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _process_pdf_file(file_path, file_name):
        """
        处理PDF文件
        
        参数:
            file_path: 文件路径
            file_name: 文件名
            
        返回:
            文件内容
        """
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
        """
        处理Word文件
        
        参数:
            file_path: 文件路径
            file_name: 文件名
            
        返回:
            文件内容
        """
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
        """
        根据文件类型提取内容
        
        参数:
            file_path: 文件路径
            file_name: 文件名
            
        返回:
            提取的文件内容
        """
        # 根据文件扩展名选择提取方式
        file_ext = FileUtils.get_file_extension(file_name)
        
        # 只处理文本类文件
        if FileUtils.is_text_file(file_name):
            return FileUtils._process_text_file(file_path, file_name)
        elif FileUtils.is_pdf_file(file_name):
            return FileUtils._process_pdf_file(file_path, file_name)
        elif FileUtils.is_word_file(file_name):
            return FileUtils._process_word_file(file_path, file_name)
        else:
            # 其他文件类型，只显示文件信息
            return f"[无法提取该类型文件的内容：{file_name}]"
    
    @staticmethod
    def process_uploaded_files(files):
        """
        处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
            
        返回:
            提取的文件内容列表
        """
        extracted_contents = []
        temp_dir = None
        
        if not files:
            return extracted_contents
        
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            for file in files:
                # 检查文件结构
                if isinstance(file, dict) and 'name' in file and 'content' in file:
                    # 保存到临时文件
                    file_path = FileUtils._save_uploaded_file(file, temp_dir)
                    if file_path:
                        # 提取文件内容
                        content = FileUtils._extract_file_content(file_path, file['name'])
                        if content:
                            extracted_contents.append(f"文件 {file['name']} 内容：\n{content}")
        except Exception as e:
            # 记录错误但不中断流程
            LoggingUtils.log_error(f"处理上传文件失败: {str(e)}")
        finally:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except Exception as cleanup_error:
                    LoggingUtils.log_error(f"清理临时目录失败: {str(cleanup_error)}")
        
        return extracted_contents
    
    @staticmethod
    def get_file_info(file_path):
        """
        获取文件信息
        
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
                    'exists': True,
                    'extension': FileUtils.get_file_extension(file_path)
                }
            else:
                return {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'exists': False,
                    'extension': FileUtils.get_file_extension(file_path)
                }
        except Exception as e:
            LoggingUtils.log_error(f"获取文件信息失败: {str(e)}")
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'error': str(e),
                'extension': FileUtils.get_file_extension(file_path)
            }
    
    @staticmethod
    def validate_file_extension(file_name, allowed_extensions, param_name='文件'):
        """
        验证文件扩展名
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表，例如 ['.txt', '.pdf']
            param_name: 参数名称（用于错误消息）
            
        返回:
            str: 验证后的文件名
            
        异常:
            ValueError: 扩展名不允许时抛出
        """
        if not file_name:
            raise ValueError(f'{param_name}名称不能为空')
        
        if not allowed_extensions:
            return file_name
        
        ext = FileUtils.get_file_extension(file_name)
        if ext not in allowed_extensions:
            allowed_str = ', '.join(allowed_extensions)
            raise ValueError(f'{param_name}类型不允许。允许的类型: {allowed_str}')
        
        return file_name
    
    @staticmethod
    def validate_file_type(file_name, allowed_extensions, param_name='文件'):
        """
        验证文件类型
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表，例如 ['.txt', '.pdf']
            param_name: 参数名称（用于错误消息）
            
        返回:
            str: 验证后的文件名
            
        异常:
            ValueError: 类型不允许时抛出
        """
        return FileUtils.validate_file_extension(file_name, allowed_extensions, param_name)
    
    @staticmethod
    def validate_file_type_with_result(file_name, allowed_extensions=None):
        """
        验证文件类型并返回结果
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        try:
            FileUtils.validate_file_extension(file_name, allowed_extensions)
            return True, None
        except ValueError as e:
            return False, str(e)
    
    @staticmethod
    def get_files_from_vector_results(vector_results):
        """
        根据向量检索结果获取文件信息
        
        参数:
            vector_results: 向量检索结果
            
        返回:
            文件信息列表
        """
        file_results = []
        for result in vector_results:
            metadata = result.get('metadata', {})
            file_path = metadata.get('file_path', '')
            if file_path:
                filename = os.path.basename(file_path)
                file_results.append({
                    'file': filename,
                    'path': file_path,
                    'folder': metadata.get('folder_id', ''),
                    'content': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', ''),
                    'extension': FileUtils.get_file_extension(filename)
                })
        return file_results
    
    @staticmethod
    def traditional_search(query, documents, k=5):
        """
        传统内容检索逻辑
        
        参数:
            query: 查询文本
            documents: 文档列表
            k: 返回结果数量
            
        返回:
            搜索结果列表
        """
        try:
            results = []
            query_lower = query.lower()
            
            for doc in documents:
                file_path = doc.get('path', '')
                if file_path:
                    try:
                        # 尝试读取文本文件内容进行搜索
                        file_name = doc.get('name', '')
                        if FileUtils.is_text_file(file_name):
                            # 只对文本文件使用'r'模式打开
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query_lower in content.lower():
                                    results.append({
                                        'file': file_name,
                                        'path': file_path,
                                        'folder': doc.get('folder', ''),
                                        'extension': FileUtils.get_file_extension(file_name)
                                    })
                        # 对于PDF和Word文件，使用专门的处理方法
                        elif FileUtils.is_pdf_file(file_name) or FileUtils.is_word_file(file_name):
                            # 使用提取方法获取内容
                            content = FileUtils._extract_file_content(file_path, file_name)
                            if query_lower in content.lower():
                                results.append({
                                    'file': file_name,
                                    'path': file_path,
                                    'folder': doc.get('folder', ''),
                                    'extension': FileUtils.get_file_extension(file_name)
                                })
                        # 对于其他类型的文件，只搜索文件名
                        elif query_lower in file_name.lower():
                            results.append({
                                'file': file_name,
                                'path': file_path,
                                'folder': doc.get('folder', ''),
                                'extension': FileUtils.get_file_extension(file_name)
                            })
                    except Exception as file_error:
                        LoggingUtils.log_error(f"❌ 读取文件 {doc.get('name', '')} 时出错: {file_error}")
            
            # 返回前k个结果
            return results[:k]
        except Exception as e:
            LoggingUtils.log_error(f"❌ 传统搜索失败: {str(e)}")
            return []
    
    @staticmethod
    def search_files(query, search_type='vector', k=5, vector_service=None, data_service=None):
        """
        搜索文件内容
        
        参数:
            query: 查询文本
            search_type: 搜索类型 ('vector' 或 'traditional')
            k: 返回结果数量
            vector_service: 向量服务实例，用于向量搜索
            data_service: 数据服务实例，用于获取文档列表
            
        返回:
            搜索结果列表
        """
        try:
            LoggingUtils.log_info(f"🔍 开始文件搜索: 查询='{query}', 类型='{search_type}', 结果数量={k}")
            
            if search_type == 'vector' and vector_service:
                # 调用向量服务进行向量检索
                vector_results = vector_service.search_vectors(query, k=k)
                if vector_results['success']:
                    # 根据向量检索结果获取文件信息
                    file_results = FileUtils.get_files_from_vector_results(vector_results['results'])
                    return file_results
                else:
                    LoggingUtils.log_error(f"❌ 向量检索失败: {vector_results['message']}")
                    return []
            elif data_service:
                # 传统内容检索逻辑
                documents = data_service.get_documents()
                return FileUtils.traditional_search(query, documents, k=k)
            else:
                LoggingUtils.log_error("❌ 搜索失败: 缺少必要的服务实例")
                return []
        except Exception as e:
            LoggingUtils.log_error(f"❌ 文件搜索失败: {str(e)}")
            return []
    
    @staticmethod
    def read_file_content(file_path, encoding='utf-8'):
        """
        读取文件内容
        
        参数:
            file_path: 文件路径
            encoding: 文件编码
            
        返回:
            文件内容
        """
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except Exception as e:
            LoggingUtils.log_error(f"读取文件内容失败: {str(e)}")
            return ""
    

    
    @staticmethod
    def validate_file(file_name, allowed_extensions=None, use_exception=False, param_name='文件'):
        """
        统一文件验证接口
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表
            use_exception: 是否使用异常处理方式
            param_name: 参数名称（用于错误消息）
            
        返回:
            如果 use_exception 为 True，验证通过返回文件名，失败抛出异常
            如果 use_exception 为 False，返回 (是否验证通过, 错误信息) 元组
        """
        if use_exception:
            return FileUtils.validate_file_type(file_name, allowed_extensions, param_name)
        else:
            try:
                FileUtils.validate_file_extension(file_name, allowed_extensions, param_name)
                return True, None
            except ValueError as e:
                return False, str(e)
