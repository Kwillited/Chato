"""测试进程隔离的向量数据库服务是否解决文件删除问题"""
import sys
import os
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector.vector_db_service_mp import VectorDBServiceMP

def test_chroma_delete_with_mp():
    """测试使用进程隔离的 VectorDBServiceMP 后是否可以删除向量数据库文件"""
    print("=== 测试: 进程隔离的向量数据库服务删除文件 ===")
    
    # 创建临时目录作为向量数据库路径
    temp_dir = tempfile.mkdtemp()
    vector_db_path = os.path.join(temp_dir, "test_chroma_db_mp")
    
    try:
        # 实例化 VectorDBServiceMP
        print(f"创建进程隔离的向量数据库服务实例，路径: {vector_db_path}")
        vector_service = VectorDBServiceMP(
            vector_db_path=vector_db_path,
            embedder_model="Ollama-qwen3-embedding:0.6b",
            knowledge_base_name="test_delete_mp"
        )
        
        # 测试添加文档
        print("测试添加文档...")
        from langchain_core.documents import Document
        test_docs = [
            Document(page_content="这是测试文档 1", metadata={"source": "test1.txt"}),
            Document(page_content="这是测试文档 2", metadata={"source": "test2.txt"})
        ]
        add_result = vector_service.add_documents(test_docs)
        print(f"添加文档结果: {add_result}")
        
        # 测试搜索
        print("测试搜索文档...")
        search_result = vector_service.search_documents("测试文档")
        print(f"搜索结果数量: {len(search_result)}")
        
        # 测试获取统计信息
        print("测试获取统计信息...")
        stats = vector_service.get_vector_statistics()
        print(f"统计信息: {stats}")
        
        # 关闭服务
        print("关闭进程隔离的向量数据库服务...")
        vector_service.close()
        print("服务关闭成功")
        
        # 添加延迟，确保所有资源都被释放
        print("等待资源释放...")
        import time
        time.sleep(2)
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        # 再次等待
        time.sleep(1)
        
        # 尝试删除向量数据库文件
        print("尝试删除向量数据库文件...")
        if os.path.exists(vector_db_path):
            try:
                shutil.rmtree(vector_db_path)
                print("✅ 进程隔离后删除成功！")
                return True
            except Exception as e:
                print(f"❌ 进程隔离后删除失败: {e}")
                return False
        else:
            print("⚠️  向量数据库文件不存在")
            return False
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

def test_chroma_delete_directly():
    """测试直接实例化 VectorDBService 后是否无法删除向量数据库文件（对比测试）"""
    print("\n=== 对比测试: 直接实例化后删除向量数据库文件 ===")
    
    # 创建临时目录作为向量数据库路径
    temp_dir = tempfile.mkdtemp()
    vector_db_path = os.path.join(temp_dir, "test_chroma_db_direct")
    
    try:
        # 实例化 VectorDBService
        print(f"创建向量数据库服务实例，路径: {vector_db_path}")
        from app.services.vector.vector_db_service import VectorDBService
        vector_service = VectorDBService(
            vector_db_path=vector_db_path,
            embedder_model="Ollama-qwen3-embedding:0.6b",
            knowledge_base_name="test_delete_direct"
        )
        
        # 初始化向量存储
        print("初始化向量存储...")
        vector_store = vector_service.vector_store
        print("向量存储初始化成功")
        
        # 尝试删除向量数据库文件
        print("尝试删除向量数据库文件...")
        if os.path.exists(vector_db_path):
            try:
                shutil.rmtree(vector_db_path)
                print("✅ 直接删除成功！")
                return True
            except Exception as e:
                print(f"❌ 直接删除失败: {e}")
                return False
        else:
            print("⚠️  向量数据库文件不存在")
            return False
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

def main():
    """主测试函数"""
    print("开始测试进程隔离的向量数据库服务...\n")
    
    # 测试 1: 进程隔离删除
    test_mp_result = test_chroma_delete_with_mp()
    
    # 测试 2: 直接删除（对比）
    test_direct_result = test_chroma_delete_directly()
    
    # 总结
    print("\n=== 测试结果总结 ===")
    print(f"测试 1 (进程隔离删除): {'通过' if test_mp_result else '失败'}")
    print(f"测试 2 (直接删除): {'通过' if test_direct_result else '失败'}")
    
    if test_mp_result and not test_direct_result:
        print("\n结论: 进程隔离的向量数据库服务成功解决了文件删除问题！")
        print("✅ 推荐使用 VectorDBServiceMP 来管理向量数据库实例，以避免文件锁定问题。")
    elif test_mp_result:
        print("\n结论: 进程隔离的向量数据库服务工作正常，但直接删除也能成功，可能环境有所不同。")
    else:
        print("\n结论: 测试结果不明确，可能存在其他因素影响。")

if __name__ == "__main__":
    main()
