"""检查数据库表结构"""
import os
import json
from app.core.config import config_manager
from app.core.database import get_db
from sqlalchemy import inspect

# 获取数据库路径
user_data_dir = config_manager.get_user_data_dir()
db_path = os.path.join(user_data_dir, 'config', 'chato.db')
print(f"数据库路径: {db_path}")
print(f"数据库文件存在: {os.path.exists(db_path)}")

# 获取数据库会话
db_session = next(get_db())
try:
    # 使用inspect检查数据库结构
    inspector = inspect(db_session.bind)
    
    # 获取所有表
    tables = inspector.get_table_names()
    print(f"\n数据库中的表: {tables}")
    
    # 检查document_chunks表结构
    if 'document_chunks' in tables:
        print("\ndocument_chunks表结构:")
        columns = inspector.get_columns('document_chunks')
        for column in columns:
            print(f"  {column['name']}: {column['type']}")
    else:
        print("\ndocument_chunks表不存在！")
    
    # 检查documents表是否有数据
    print("\ndocuments表数据:")
    from app.models.database.models import Document
    documents = db_session.query(Document).all()
    print(f"  文档数量: {len(documents)}")
    for doc in documents[:3]:  # 只显示前3个
        print(f"  - {doc.name} (ID: {doc.id})")
    
    # 检查document_chunks表是否有数据
    print("\ndocument_chunks表数据:")
    from app.models.database.models import DocumentChunk
    chunks = db_session.query(DocumentChunk).all()
    print(f"  分块数量: {len(chunks)}")
    for chunk in chunks[:3]:  # 只显示前3个
        print(f"  - 分块 {chunk.chunk_index} (文档ID: {chunk.document_id})")
finally:
    db_session.close()