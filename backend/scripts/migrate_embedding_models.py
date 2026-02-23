"""嵌入模型数据库迁移脚本"""
import os
import sys
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine, Base
from app.models.database.models import EmbeddingModel, EmbeddingVersion
from app.services.model.embedding_model_service import EmbeddingModelService


def create_tables():
    """创建嵌入模型相关的数据库表"""
    try:
        # 创建表
        Base.metadata.create_all(bind=engine)
        print("✅ 成功创建嵌入模型相关的数据库表")
    except Exception as e:
        print(f"❌ 创建数据库表失败: {str(e)}")
        raise


def initialize_embedding_models():
    """初始化嵌入模型数据"""
    try:
        from app.core.database import get_db
        db = next(get_db())
        
        # 初始化嵌入模型
        embedding_model_service = EmbeddingModelService()
        models = embedding_model_service.initialize_models(db)
        
        print(f"✅ 成功初始化 {len(models)} 个嵌入模型")
        for model in models:
            print(f"  - {model['name']} (类型: {model['type']}, 启用: {model['enabled']})")
            
        return models
    except Exception as e:
        print(f"❌ 初始化嵌入模型失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """主函数"""
    print("开始嵌入模型数据库迁移...")
    
    try:
        # 创建表
        create_tables()
        
        # 初始化数据
        initialize_embedding_models()
        
        print("\n🎉 嵌入模型数据库迁移完成！")
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
