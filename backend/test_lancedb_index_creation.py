"""测试LanceDB索引创建功能"""
import os
import tempfile
from langchain_core.documents import Document
from app.repositories.lancedb_repository import LanceDBRepository


def test_index_creation():
    """测试建表时是否成功创建索引"""
    # 创建临时目录作为向量数据库路径
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔧 创建临时目录: {temp_dir}")
        
        # 初始化LanceDBRepository
        repo = LanceDBRepository()
        
        # 连接到LanceDB
        repo.connect(vector_db_path=temp_dir)
        
        # 加载嵌入模型（使用ollama的qwen3-embedding:0.6b）
        print("🤖 加载嵌入模型: qwen3-embedding:0.6b")
        repo.load_embedding_model("ollama-qwen3-embedding:0.6b")
        
        # 测试数据
        test_documents = [
            Document(page_content="测试文档1内容", metadata={"source": "test1"}),
            Document(page_content="测试文档2内容", metadata={"source": "test2"})
        ]
        
        # 使用唯一的表名，确保每次测试都创建新表
        import uuid
        unique_table_name = f"test_index_creation_{uuid.uuid4().hex[:8]}"
        print(f"📁 创建向量存储，表名: {unique_table_name}")
        try:
            repo.create_vector_store(
                folder_id=unique_table_name,
                documents=test_documents
            )
            print("✅ 向量存储创建成功")
        except Exception as e:
            print(f"❌ 向量存储创建失败: {e}")
            return False
        
        # 检查是否成功创建索引
        print("🔍 检查索引创建状态")
        print(f"向量存储实例: {repo.vector_store}")
        
        # 直接从连接中获取表
        try:
            table = repo.conn.open_table(unique_table_name)
            print(f"✅ 表已创建: {table.name}")
            
            # 检查表结构
            schema = table.schema
            print(f"📋 表结构: {schema}")
            
            # 检查索引
            try:
                # 尝试执行全文搜索，验证索引是否存在
                result = table.search("测试").limit(1).to_pandas()
                print(f"✅ 全文搜索测试成功，返回结果数: {len(result)}")
                print("🎉 索引创建成功！")
                return True
            except Exception as e:
                print(f"❌ 全文搜索测试失败: {e}")
                return False
        except Exception as e:
            print(f"❌ 无法打开表: {e}")
            return False


if __name__ == "__main__":
    print("🚀 开始测试LanceDB索引创建...")
    success = test_index_creation()
    if success:
        print("✅ 测试通过！建表时成功创建索引")
    else:
        print("❌ 测试失败！建表时未能创建索引")
