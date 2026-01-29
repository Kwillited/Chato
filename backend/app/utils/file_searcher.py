"""文件搜索工具类，提供统一的文件搜索功能"""
import os
from app.utils.logging_utils import LoggingUtils

class FileSearcher:
    """文件搜索工具类，封装所有文件搜索方法"""
    
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
                    'content': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
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
                        if file_path.lower().endswith(('.txt', '.md', '.csv', '.pdf', '.docx')):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query_lower in content.lower():
                                    results.append({
                                        'file': doc.get('name', ''),
                                        'path': file_path,
                                        'folder': doc.get('folder', '')
                                    })
                        # 对于其他类型的文件，只搜索文件名
                        elif query_lower in doc.get('name', '').lower():
                            results.append({
                                'file': doc.get('name', ''),
                                'path': file_path,
                                'folder': doc.get('folder', '')
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
                    file_results = FileSearcher.get_files_from_vector_results(vector_results['results'])
                    return file_results
                else:
                    LoggingUtils.log_error(f"❌ 向量检索失败: {vector_results['message']}")
                    return []
            elif data_service:
                # 传统内容检索逻辑
                documents = data_service.get_documents()
                return FileSearcher.traditional_search(query, documents, k=k)
            else:
                LoggingUtils.log_error("❌ 搜索失败: 缺少必要的服务实例")
                return []
        except Exception as e:
            LoggingUtils.log_error(f"❌ 文件搜索失败: {str(e)}")
            return []
    
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
        text_extensions = ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml']
        return FileSearcher.get_file_extension(file_name) in text_extensions
    
    @staticmethod
    def is_pdf_file(file_name):
        """
        判断是否为PDF文件
        
        参数:
            file_name: 文件名
            
        返回:
            是否为PDF文件
        """
        return FileSearcher.get_file_extension(file_name) == '.pdf'
    
    @staticmethod
    def is_word_file(file_name):
        """
        判断是否为Word文件
        
        参数:
            file_name: 文件名
            
        返回:
            是否为Word文件
        """
        word_extensions = ['.doc', '.docx']
        return FileSearcher.get_file_extension(file_name) in word_extensions