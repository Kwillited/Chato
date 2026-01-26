#!/usr/bin/env python3
"""
上传模型图标到数据库的脚本
"""
import os
import sqlite3
from app.core.config import config_manager

# 获取数据库路径
def get_db_path():
    """获取数据库路径"""
    user_data_dir = config_manager.get_user_data_dir()
    return os.path.join(user_data_dir, 'config', 'chato.db')

# 上传图标到数据库
def upload_icon(model_name, icon_path):
    """
    上传图标到数据库
    
    参数:
        model_name: 模型名称，如 'Ollama'
        icon_path: 图标文件路径
    """
    # 检查图标文件是否存在
    if not os.path.exists(icon_path):
        print(f"❌ 图标文件不存在: {icon_path}")
        return False
    
    # 读取图标文件
    print(f"🔄 读取图标文件: {icon_path}")
    with open(icon_path, 'rb') as f:
        icon_blob = f.read()
    
    # 获取数据库连接
    db_path = get_db_path()
    print(f"📦 连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # 更新模型的图标
        cursor.execute(
            "UPDATE models SET icon_blob = ? WHERE name = ?",
            (icon_blob, model_name)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ 成功将图标上传到数据库: {model_name}")
        return True
    except Exception as e:
        print(f"❌ 上传图标失败: {str(e)}")
        return False

# 主函数
if __name__ == "__main__":
    # 测试上传Ollama图标
    ollama_icon_path = "C:\\Users\\Admin\\Downloads\\Ollama.png"
    upload_icon("Ollama", ollama_icon_path)
    
    # 可以继续上传其他模型图标
    # upload_icon("OpenAI", "C:\\path\\to\\OpenAI.png")
    # upload_icon("Anthropic", "C:\\path\\to\\Anthropic.png")
    # ...