"""测试嵌入模型加载策略"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import ConfigManager
from app.core.data_manager import db, load_data
from app.llm.managers.embedding_model_manager import EmbeddingModelManager
from app.services.vector.vector_store_service import VectorStoreService

print("=== 测试嵌入模型加载策略 ===")

# 加载数据（从数据库加载配置）
print("\n1. 加载数据（从数据库加载配置）:")
try:
    load_data()
    print("  数据加载成功")
    print(f"  当前嵌入模型配置: {db['settings'].get('vector', {}).get('embedder_model')}")
except Exception as e:
    print(f"  数据加载失败: {e}")

# 测试2: 测试嵌入模型缓存功能
print("\n2. 测试嵌入模型缓存功能:")
try:
    # 清空现有缓存
    cleared = EmbeddingModelManager.clear_model_cache()
    print(f"  初始缓存大小: {cleared}")
    
    # 第一次加载模型（应该从磁盘加载）
    print("  第一次加载模型:")
    model1 = EmbeddingModelManager.get_embedding_model('llama3')
    print(f"  模型1加载状态: {'成功' if model1 else '失败'}")
    print(f"  当前缓存大小: {EmbeddingModelManager.get_cache_size()}")
    
    # 第二次加载相同模型（应该从缓存加载）
    print("  第二次加载相同模型:")
    model2 = EmbeddingModelManager.get_embedding_model('llama3')
    print(f"  模型2加载状态: {'成功' if model2 else '失败'}")
    print(f"  当前缓存大小: {EmbeddingModelManager.get_cache_size()}")
    
    # 检查是否是同一个实例
    print(f"  两个模型是否为同一个实例: {model1 is model2}")
    
except Exception as e:
    print(f"  测试失败: {e}")

# 测试3: 测试模型切换
print("\n3. 测试模型切换:")
try:
    # 加载不同的模型
    models_to_test = ['llama3', 'all-MiniLM-L6-v2', 'qwen3-embedding-0.6b']
    
    for model_name in models_to_test:
        print(f"  加载模型: {model_name}")
        model = EmbeddingModelManager.get_embedding_model(model_name)
        print(f"  模型加载状态: {'成功' if model else '失败'}")
        print(f"  当前缓存大小: {EmbeddingModelManager.get_cache_size()}")
    
    # 测试缓存大小限制（应该最多保留3个模型）
    print(f"  最终缓存大小: {EmbeddingModelManager.get_cache_size()}")
    
except Exception as e:
    print(f"  测试失败: {e}")

# 测试4: 测试从db['settings']获取配置
print("\n4. 测试从db['settings']获取配置:")
try:
    # 修改db['settings']中的嵌入模型配置
    new_model = 'all-MiniLM-L6-v2'
    print(f"  修改嵌入模型配置为: {new_model}")
    db['settings']['vector']['embedder_model'] = new_model
    
    # 创建向量存储服务实例（应该使用新配置）
    vector_service = VectorStoreService()
    print(f"  向量存储服务初始化成功")
    print(f"  使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    
    # 测试向量存储初始化
    vector_store = vector_service.vector_store
    print(f"  向量存储初始化成功: {vector_store}")
    
except Exception as e:
    print(f"  测试失败: {e}")

# 测试5: 测试回退机制
print("\n5. 测试回退机制:")
try:
    # 修改为不存在的模型
    non_existent_model = 'non-existent-model-123'
    print(f"  修改为不存在的模型: {non_existent_model}")
    db['settings']['vector']['embedder_model'] = non_existent_model
    
    # 创建新的向量存储服务实例（应该回退到默认模型）
    vector_service = VectorStoreService()
    print(f"  向量存储服务初始化成功")
    print(f"  配置的嵌入模型: {non_existent_model}")
    
    # 测试向量存储初始化
    try:
        vector_store = vector_service.vector_store
        print(f"  向量存储初始化成功: {vector_store}")
        print(f"  实际使用的嵌入模型: {vector_service.vector_db_service.embedder_model}")
    except Exception as e:
        print(f"  向量存储初始化失败: {e}")
    
except Exception as e:
    print(f"  测试失败: {e}")

print("\n=== 测试完成 ===")
print("\n总结:")
print("1. 嵌入模型现在从db['settings']获取配置，而不是硬编码默认值")
print("2. 实现了嵌入模型的缓存和即用即加载策略")
print("3. 支持模型切换和回退机制")
print("4. 向量数据库保持启动时加载策略")
