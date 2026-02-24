"""测试 langchain_chroma 实例化后是否无法删除向量数据库文件，以及进程隔离是否可以解决这个问题"""
import sys
import os
import subprocess
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector.vector_db_service import VectorDBService

def test_chroma_delete_directly():
    """测试直接实例化 VectorDBService 后是否无法删除向量数据库文件"""
    print("=== 测试 1: 直接实例化后删除向量数据库文件 ===")
    
    # 创建临时目录作为向量数据库路径
    temp_dir = tempfile.mkdtemp()
    vector_db_path = os.path.join(temp_dir, "test_chroma_db")
    
    try:
        # 实例化 VectorDBService
        print(f"创建向量数据库服务实例，路径: {vector_db_path}")
        vector_service = VectorDBService(
            vector_db_path=vector_db_path,
            embedder_model="Ollama-qwen3-embedding:0.6b",
            knowledge_base_name="test_delete"
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
    
    return True

def test_chroma_delete_with_process_isolation():
    """测试使用进程隔离后是否可以删除向量数据库文件"""
    print("\n=== 测试 2: 进程隔离后删除向量数据库文件 ===")
    
    # 创建临时目录作为向量数据库路径
    temp_dir = tempfile.mkdtemp()
    vector_db_path = os.path.join(temp_dir, "test_chroma_db")
    
    # 创建一个子进程脚本来实例化 VectorDBService
    child_script = os.path.join(temp_dir, "child_process.py")
    child_script_content = f"""
import sys
sys.path.insert(0, r'{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}')

from app.services.vector.vector_db_service import VectorDBService

# 实例化 VectorDBService
vector_service = VectorDBService(
    vector_db_path=r'{vector_db_path}',
    embedder_model="Ollama-qwen3-embedding:0.6b",
    knowledge_base_name="test_delete"
)

# 初始化向量存储
vector_store = vector_service.vector_store
print("子进程: 向量存储初始化成功")
"""
    
    with open(child_script, 'w', encoding='utf-8') as f:
        f.write(child_script_content)
    
    try:
        # 运行子进程
        print("运行子进程初始化向量存储...")
        result = subprocess.run(
            [sys.executable, child_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("子进程执行成功:")
            print(result.stdout)
        else:
            print("子进程执行失败:")
            print(f"返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
        
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
        return False
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

def test_chroma_delete_after_service_references_cleared():
    """测试清除服务引用后是否可以删除向量数据库文件"""
    print("\n=== 测试 3: 清除服务引用后删除向量数据库文件 ===")
    
    # 创建临时目录作为向量数据库路径
    temp_dir = tempfile.mkdtemp()
    vector_db_path = os.path.join(temp_dir, "test_chroma_db")
    
    try:
        # 实例化 VectorDBService
        print(f"创建向量数据库服务实例，路径: {vector_db_path}")
        vector_service = VectorDBService(
            vector_db_path=vector_db_path,
            embedder_model="Ollama-qwen3-embedding:0.6b",
            knowledge_base_name="test_delete"
        )
        
        # 初始化向量存储
        print("初始化向量存储...")
        vector_store = vector_service.vector_store
        print("向量存储初始化成功")
        
        # 清除引用
        print("清除服务引用...")
        del vector_store
        del vector_service
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        # 尝试删除向量数据库文件
        print("尝试删除向量数据库文件...")
        if os.path.exists(vector_db_path):
            try:
                shutil.rmtree(vector_db_path)
                print("✅ 清除引用后删除成功！")
                return True
            except Exception as e:
                print(f"❌ 清除引用后删除失败: {e}")
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
    print("开始测试 langchain_chroma 删除问题...\n")
    
    # 测试 1: 直接删除
    test1_result = test_chroma_delete_directly()
    
    # 测试 2: 进程隔离删除
    test2_result = test_chroma_delete_with_process_isolation()
    
    # 测试 3: 清除引用后删除
    test3_result = test_chroma_delete_after_service_references_cleared()
    
    # 总结
    print("\n=== 测试结果总结 ===")
    print(f"测试 1 (直接删除): {'通过' if test1_result else '失败'}")
    print(f"测试 2 (进程隔离删除): {'通过' if test2_result else '失败'}")
    print(f"测试 3 (清除引用后删除): {'通过' if test3_result else '失败'}")
    
    if not test1_result and test2_result:
        print("\n结论: langchain_chroma 实例化后确实无法直接删除向量数据库文件，但进程隔离可以解决这个问题。")
    elif test1_result:
        print("\n结论: langchain_chroma 实例化后可以直接删除向量数据库文件，不存在文件锁定问题。")
    else:
        print("\n结论: 测试结果不明确，可能存在其他因素影响。")

if __name__ == "__main__":
    main()
