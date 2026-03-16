"""测试脚本：查看LanceDB表内容"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import lancedb

def inspect_lancedb_table():
    """查看LanceDB表内容"""
    
    # 指定表路径
    table_path = r"C:\Users\admin\AppData\Local\Chato\Retrieval-Augmented Generation\vector_db\9ac33f41.lance"
    
    print(f"=" * 80)
    print(f"正在检查 LanceDB 表: {table_path}")
    print(f"=" * 80)
    
    try:
        # 连接到表
        db = lancedb.connect(os.path.dirname(table_path))
        table_name = os.path.basename(table_path).replace('.lance', '')
        
        # 打开表
        table = db.open_table(table_name)
        
        print(f"\n✅ 成功打开表: {table_name}")
        
        # 获取表信息
        print(f"\n表信息:")
        print(f"  - 行数: {table.count_rows()}")
        
        # 获取schema
        print(f"\nSchema:")
        schema = table.schema
        field_names = []
        for field in schema:
            print(f"  - {field.name}: {field.type}")
            field_names.append(field.name)
        
        # 获取所有数据
        print(f"\n" + "=" * 80)
        print(f"详细数据:")
        print(f"=" * 80)
        
        # 使用 to_pandas() 或者直接读取
        try:
            # 尝试使用 to_arrow() 方法
            arrow_table = table.to_arrow()
            records = arrow_table.to_pylist()
        except:
            try:
                # 尝试使用 to_pandas() 方法（如果可用）
                try:
                    import pandas as pd
                    df = table.to_pandas()
                    records = df.to_dict('records')
                except ImportError:
                    # 手动获取数据
                    records = []
                    # 使用查询获取所有数据
                    batch = table.to_batches(limit=1000)
                    for b in batch:
                        for i in range(len(b)):
                            record = {}
                            for j, field in enumerate(schema):
                                record[field.name] = b[field.name][i].as_py()
                            records.append(record)
            except Exception as e2:
                print(f"无法获取记录: {e2}")
                records = []
        
        # 打印详细信息
        for idx, record in enumerate(records):
            print(f"\n--- 记录 {idx + 1} ---")
            for key, value in record.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} (长度: {len(value)})")
                    if key == 'vector':
                        print(f"  {key} (前10个元素): {value[:10] if len(value) > 10 else value}")
                    else:
                        print(f"  {key}: {value}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}... (长度: {len(value)})")
                else:
                    print(f"  {key}: {value}")
        
        print(f"\n" + "=" * 80)
        print(f"✅ 检查完成")
        print(f"=" * 80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_lancedb_table()
