"""测试嵌入模型动态加载功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import ConfigManager
from app.llm.managers.embedding_model_manager import EmbeddingModelManager
from app.services.vector.vector_store_service import VectorStoreService

# 获取配置管理器实例
config_manager = ConfigManager.get_instance()

print("=== 测试嵌入模型动态加载功能 ===")

# 测试1: 查看支持的嵌入模型
print("\n1. 支持的嵌入模型:")
supported_models = EmbeddingModelManager.get_supported_models()
for model_name, model_info in supported_models.items():
    print(f"  - {model_name}: {model_info['description']} (类型: {model_info['type']})")

# 测试2: 测试默认嵌入模型加载
print("\n2. 测试默认嵌入模型加载:")
try:
    # 创建向量存储服务实例（使用默认配置）
    vector_service = VectorStoreService()
    print(f"  向量存储服务初始化成功")
    print(f"  使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    
    # 测试向量存储初始化
    vector_store = vector_service.vector_store
    print(f"  向量存储初始化成功: {vector_store}")
    
    # 获取向量库统计信息
    stats = vector_service.get_vector_statistics()
    print(f"  向量库统计信息: {stats}")
    
except Exception as e:
    print(f"  测试失败: {e}")

# 测试3: 测试特定嵌入模型加载
print("\n3. 测试特定嵌入模型加载:")
test_models = ['qwen3-embedding-0.6b', 'all-MiniLM-L6-v2']

for model_name in test_models:
    try:
        print(f"  测试模型: {model_name}")
        # 创建向量存储服务实例（指定嵌入模型）
        vector_service = VectorStoreService(embedder_model=model_name)
        print(f"    向量存储服务初始化成功")
        print(f"    使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
        
        # 测试向量存储初始化
        vector_store = vector_service.vector_store
        print(f"    向量存储初始化成功")
        
    except Exception as e:
        print(f"    测试失败: {e}")

# 测试4: 测试配置更新
print("\n4. 测试配置更新:")
try:
    # 获取当前配置
    current_model = config_manager.get('vector.embedder_model')
    print(f"  当前配置的嵌入模型: {current_model}")
    
    # 更新配置
    new_model = 'all-MiniLM-L6-v2'
    config_manager.set('vector.embedder_model', new_model)
    print(f"  配置已更新为: {new_model}")
    
    # 重新创建向量存储服务实例
    vector_service = VectorStoreService()
    print(f"  新的向量存储服务使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    
    # 恢复原配置
    config_manager.set('vector.embedder_model', current_model)
    print(f"  配置已恢复为: {current_model}")
    
except Exception as e:
    print(f"  测试失败: {e}")

print("\n=== 测试完成 ===")
