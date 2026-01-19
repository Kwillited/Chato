"""测试文档删除功能"""
import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag.document_service import DocumentService

# 创建测试文档和文件夹
def setup_test_data(data_dir):
    """创建测试数据"""
    # 创建测试文件夹
    test_folder = os.path.join(data_dir, 'test_folder')
    os.makedirs(test_folder, exist_ok=True)
    
    # 创建测试文件
    test_files = [
        ('test1.txt', ''),
        ('test2.txt', ''),
        ('test3.txt', 'test_folder'),
        ('test4.txt', 'test_folder')
    ]
    
    for filename, folder in test_files:
        if folder:
            file_path = os.path.join(data_dir, folder, filename)
        else:
            file_path = os.path.join(data_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(f"This is a test file: {filename}")
    
    print(f"创建了 {len(test_files)} 个测试文件")

def test_delete_document():
    """测试删除单个文档"""
    print("=== 测试删除单个文档 ===")
    
    # 创建文档服务实例
    doc_service = DocumentService()
    
    # 测试删除存在的文件
    print("1. 测试删除存在的文件")
    result = doc_service.delete_document('test1.txt')
    print(f"   结果: {result}")
    assert result['success'] == True
    
    # 测试删除不存在的文件
    print("\n2. 测试删除不存在的文件")
    result = doc_service.delete_document('non_existent_file.txt')
    print(f"   结果: {result}")
    assert result['success'] == True
    
    # 测试删除文件夹中的文件
    print("\n3. 测试删除文件夹中的文件")
    result = doc_service.delete_document('test3.txt', 'test_folder')
    print(f"   结果: {result}")
    assert result['success'] == True

def test_delete_folder():
    """测试删除文件夹"""
    print("\n=== 测试删除文件夹 ===")
    
    # 创建文档服务实例
    doc_service = DocumentService()
    
    # 测试删除存在的文件夹
    print("1. 测试删除存在的文件夹")
    result = doc_service.delete_folder('test_folder')
    print(f"   结果: {result}")
    assert result['success'] == True
    
    # 测试删除不存在的文件夹
    print("\n2. 测试删除不存在的文件夹")
    result = doc_service.delete_folder('non_existent_folder')
    print(f"   结果: {result}")
    assert result['success'] == True

def test_delete_all_documents():
    """测试删除所有文档"""
    print("\n=== 测试删除所有文档 ===")
    
    # 创建文档服务实例
    doc_service = DocumentService()
    
    # 测试删除所有文档
    print("1. 测试删除所有文档")
    result = doc_service.delete_all_documents()
    print(f"   结果: {result}")
    assert result['success'] == True
    
    # 测试再次删除所有文档（空目录）
    print("\n2. 测试再次删除所有文档（空目录）")
    result = doc_service.delete_all_documents()
    print(f"   结果: {result}")
    assert result['success'] == True
    assert result['deleted_count'] == 0

def main():
    """主测试函数"""
    print("开始测试文档删除功能...")
    
    # 获取数据目录
    from app.core.config import config_manager
    user_data_dir = config_manager.get_user_data_dir()
    data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')
    
    # 创建测试数据
    print(f"\n准备测试数据，数据目录: {data_dir}")
    setup_test_data(data_dir)
    
    # 运行测试
    test_delete_document()
    test_delete_folder()
    test_delete_all_documents()
    
    print("\n所有测试通过！")

if __name__ == "__main__":
    main()