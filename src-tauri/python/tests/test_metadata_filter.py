"""测试元数据过滤功能"""
import os
import sys
from langchain_core.documents.base import Document

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector.vector_store_service import VectorStoreService

def test_metadata_filter():
    """测试元数据过滤功能"""
    print("=== 测试元数据过滤功能 ===")
    
    # 1. 创建向量存储服务实例
    vector_service = VectorStoreService.get_instance()
    
    # 2. 准备测试数据
    docs = [
        Document(page_content="这是关于Python的文档", metadata={"category": "programming", "language": "zh"}),
        Document(page_content="This is a document about Python", metadata={"category": "programming", "language": "en"}),
        Document(page_content="这是关于Java的文档", metadata={"category": "programming", "language": "zh"}),
        Document(page_content="这是关于人工智能的文档", metadata={"category": "ai", "language": "zh"}),
        Document(page_content="This is a document about AI", metadata={"category": "ai", "language": "en"}),
    ]
    
    print(f"准备了 {len(docs)} 个测试文档")
    
    # 3. 清空现有向量库（测试用）
    print("清空现有向量库...")
    vector_service.clear_vector_store()
    
    # 4. 添加测试文档
    print("添加测试文档...")
    result = vector_service.add_documents(docs)
    if result:
        print("测试文档添加成功")
    else:
        print("测试文档添加失败")
        return
    
    # 5. 获取向量库统计信息
    stats = vector_service.get_vector_statistics()
    print(f"向量库统计信息: {stats}")
    
    # 6. 测试不同的搜索条件
    print("\n=== 测试搜索结果 ===")
    
    # 6.1 无过滤条件
    print("\n1. 无过滤条件，搜索 'Python'")
    results = vector_service.search_documents(query="Python", k=5)
    print(f"   结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 6.2 按类别过滤
    print("\n2. 按类别过滤 'ai'，搜索 '人工智能'")
    results = vector_service.search_documents(query="人工智能", k=5, filter={"category": "ai"})
    print(f"   结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 6.3 按语言过滤
    print("\n3. 按语言过滤 'zh'，搜索 '文档'")
    results = vector_service.search_documents(query="文档", k=5, filter={"language": "zh"})
    print(f"   结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 6.4 多条件过滤
    print("\n4. 多条件过滤 'programming' 和 'zh'，搜索 'Python'")
    results = vector_service.search_documents(
        query="Python", 
        k=5, 
        filter={"category": "programming", "language": "zh"}
    )
    print(f"   结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 6.5 不存在的过滤条件
    print("\n5. 不存在的过滤条件 'category': 'nonexistent'，搜索 'Python'")
    results = vector_service.search_documents(
        query="Python", 
        k=5, 
        filter={"category": "nonexistent"}
    )
    print(f"   结果数量: {len(results)}")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 7. 测试多知识库
    print("\n=== 测试多知识库功能 ===")
    
    # 7.1 创建新的知识库
    print("\n1. 创建新的知识库 'test_kb'")
    kb_service = VectorStoreService.create_knowledge_base("test_kb")
    print(f"   知识库创建成功: {kb_service.knowledge_base_name}")
    
    # 7.2 向新知识库添加文档
    print("\n2. 向新知识库添加文档")
    kb_docs = [
        Document(page_content="这是测试知识库的文档", metadata={"kb": "test_kb"}),
        Document(page_content="Test knowledge base document", metadata={"kb": "test_kb"}),
    ]
    kb_service.add_documents(kb_docs)
    print(f"   添加了 {len(kb_docs)} 个文档到新知识库")
    
    # 7.3 搜索新知识库
    print("\n3. 搜索新知识库 'test_kb'")
    kb_results = kb_service.search_documents(query="测试", k=5)
    print(f"   结果数量: {len(kb_results)}")
    for i, doc in enumerate(kb_results):
        print(f"   {i+1}. {doc.page_content[:50]}... (metadata: {doc.metadata})")
    
    # 7.4 列出所有知识库实例
    print("\n4. 列出所有知识库实例")
    instances = VectorStoreService.list_instances()
    print(f"   实例数量: {len(instances)}")
    for name, instance in instances.items():
        print(f"   - {name}")
    
    # 8. 清理测试数据
    print("\n=== 清理测试数据 ===")
    print("清空向量库...")
    vector_service.clear_vector_store()
    kb_service.clear_vector_store()
    
    # 9. 删除测试知识库
    print("删除测试知识库 'test_kb'...")
    VectorStoreService.delete_knowledge_base("test_kb")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_metadata_filter()
