"""SQLAlchemy数据库配置和连接管理"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sqlite3
from app.core.config import config_manager
import os

# 获取数据库路径
def get_db_path():
    """获取SQLite数据库文件路径"""
    user_data_dir = config_manager.get_user_data_dir()
    return os.path.join(user_data_dir, 'config', 'chato.db')

# 创建SQLAlchemy引擎
DATABASE_URL = f"sqlite:///{get_db_path()}"

# 创建SQLAlchemy引擎，支持线程安全和外键约束
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # SQLite线程安全配置
        "uri": True,  # 启用URI模式
    },
    poolclass=StaticPool,  # 使用静态连接池
    pool_pre_ping=True,  # 连接前检查连接是否有效
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于定义模型
Base = declarative_base()

# 依赖注入函数，用于获取数据库会话
def get_db():
    """获取数据库会话，用于FastAPI依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库，创建所有表
def init_alembic_db():
    """初始化数据库，创建所有表"""
    # 导入所有模型，确保Base.metadata包含所有表定义
    from app.models import models
    # 创建所有表
    Base.metadata.create_all(bind=engine)