"""测试使用Ollama作为嵌入模型"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import ConfigManager
from app.llm.managers.embedding_model_manager import EmbeddingModelManager
from app.services.vector.vector_store_service import VectorStoreService

# 获取配置管理器实例
config_manager = ConfigManager.get_instance()

print("=== 测试使用Ollama作为嵌入模型 ===")

# 测试1: 查看当前支持的嵌入模型
print("\n1. 当前支持的嵌入模型:")
supported_models = EmbeddingModelManager.get_supported_models()
for model_name, model_info in supported_models.items():
    print(f"  - {model_name}: {model_info['description']} (类型: {model_info['type']})")

# 测试2: 测试添加Ollama嵌入模型支持
print("\n2. 测试添加Ollama嵌入模型支持:")
try:
    # 首先，让我们检查是否可以直接使用Ollama作为嵌入模型
    print("  尝试使用Ollama模型作为嵌入模型...")
    
    # 假设我们有一个Ollama模型可以用于嵌入
    ollama_embedding_model = "llama3"
    
    print(f"  测试模型: {ollama_embedding_model}")
    
    # 创建向量存储服务实例（指定使用Ollama模型作为嵌入模型）
    vector_service = VectorStoreService(embedder_model=ollama_embedding_model)
    print(f"  向量存储服务初始化成功")
    print(f"  使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    
    # 测试向量存储初始化
    try:
        vector_store = vector_service.vector_store
        print(f"  向量存储初始化成功: {vector_store}")
        
        # 获取向量库统计信息
        stats = vector_service.get_vector_statistics()
        print(f"  向量库统计信息: {stats}")
        
    except Exception as e:
        print(f"  向量存储初始化失败（可能是Ollama模型不可用）: {e}")
        print("  注意: 这可能是因为Ollama未安装或指定的模型不存在")
    
    except Exception as e:
        print(f"  测试失败: {e}")
        
except Exception as e:
    print(f"  测试失败: {e}")

# 测试3: 测试配置更新为使用Ollama
print("\n3. 测试配置更新为使用Ollama:")
try:
    # 获取当前配置
    current_model = config_manager.get('vector.embedder_model')
    print(f"  当前配置的嵌入模型: {current_model}")
    
    # 更新配置为使用Ollama模型
    ollama_model = "llama3"
    config_manager.set('vector.embedder_model', ollama_model)
    print(f"  配置已更新为: {ollama_model}")
    
    # 重新创建向量存储服务实例
    vector_service = VectorStoreService()
    print(f"  新的向量存储服务使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    
    # 恢复原配置
    config_manager.set('vector.embedder_model', current_model)
    print(f"  配置已恢复为: {current_model}")
    
except Exception as e:
    print(f"  测试失败: {e}")

# 测试4: 检查Ollama是否可用
print("\n4. 检查Ollama是否可用:")
try:
    import subprocess
    
    # 检查Ollama是否安装
    result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Ollama已安装: {result.stdout.strip()}")
        
        # 检查可用的Ollama模型
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print(f"  可用的Ollama模型:")
        print(result.stdout)
    else:
        print(f"  Ollama未安装或不可用: {result.stderr.strip()}")
        
except Exception as e:
    print(f"  检查失败: {e}")

print("\n=== 测试完成 ===")
print("\n注意事项:")
print("1. 要使用Ollama作为嵌入模型，需要确保Ollama已安装并运行")
print("2. 需要有支持嵌入的Ollama模型，如llama3、mistral等")
print("3. 如果遇到连接问题，请检查Ollama服务是否正常运行")
