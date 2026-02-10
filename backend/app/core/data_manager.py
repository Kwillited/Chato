"""数据管理模块"""
import json
import os
from datetime import datetime
from app.core.config import config_manager
from app.utils.data_utils import build_message_list

# 1. 初始化内存数据库（全局唯一）
db = {
    'chats': [],  # 存储所有对话
    'models': [],  # 存储所有模型信息，后续从SQLite加载
    'settings': {},
    'agent_sessions': []  # 存储所有智能体会话
}

# 脏标记，用于跟踪哪些数据需要保存
dirty_flags = {
    'chats': False,
    'models': False,
    'settings': False,
    'agent_sessions': False
}

# 自动保存定时器
import threading
import time
AUTO_SAVE_INTERVAL = 5  # 自动保存间隔（秒）
auto_save_timer = None

# 事务锁，确保数据一致性
transaction_lock = threading.Lock()

# 加载默认设置
for key, value in config_manager._config.items():
    db['settings'][key] = value

# --------------------------
# 2. 数据目录管理（确保data目录存在）
# --------------------------
def ensure_data_dir():
    """确保数据目录存在"""
    user_data_dir = config_manager.get_user_data_dir()
    return user_data_dir

# --------------------------
# 3. SQLite数据库初始化
# --------------------------
def init_db():
    """初始化SQLite数据库，创建表结构"""
    user_data_dir = ensure_data_dir()
    # 将数据库文件名从neovai.db改为chato.db
    db_path = os.path.join(user_data_dir, 'config', 'chato.db')
    
    # 确保config目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 使用SQLAlchemy的自动创建表功能，不再需要手动执行SQL语句
    # 表结构将由SQLAlchemy的模型定义自动创建
    from app.core.database import engine, Base
    from app.models import Model, ModelVersion, Chat, Message, AgentSession, VectorSetting, NotificationSetting, AppSetting, SystemSetting, Folder, Document, DocumentChunk
    from app.models import MCPConfig, MCPTool, MCPServer
    
    # 删除所有表并重新创建，以确保表结构与模型定义一致
    Base.metadata.drop_all(bind=engine)
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    from app.core.logging_config import logger
    logger.info(f"SQLite数据库初始化成功，数据库文件: {db_path}")

# --------------------------
# 4. 事务管理
# --------------------------
def begin_transaction():
    """开始事务，获取锁"""
    transaction_lock.acquire()
    from app.core.logging_config import logger
    logger.debug("事务开始")


def commit_transaction():
    """提交事务，释放锁并保存数据"""
    try:
        save_data()
        from app.core.logging_config import logger
        logger.debug("事务提交")
    finally:
        transaction_lock.release()


def rollback_transaction():
    """回滚事务，释放锁"""
    transaction_lock.release()
    from app.core.logging_config import logger
    logger.debug("事务回滚")

# --------------------------
# 5. 自动保存功能
# --------------------------
def auto_save_task():
    """自动保存任务，定期检查脏标记并保存数据"""
    while True:
        time.sleep(AUTO_SAVE_INTERVAL)
        with transaction_lock:
            # 检查是否有脏数据需要保存
            if any(dirty_flags.values()):
                from app.core.logging_config import logger
                logger.info(f"自动保存触发: 脏标记={dirty_flags}")
                save_data()
                logger.info("自动保存完成")


def start_auto_save():
    """启动自动保存功能"""
    global auto_save_timer
    if auto_save_timer is None or not auto_save_timer.is_alive():
        auto_save_timer = threading.Thread(target=auto_save_task, daemon=True)
        auto_save_timer.start()
        from app.core.logging_config import logger
        logger.info(f"自动保存功能已启动，间隔: {AUTO_SAVE_INTERVAL}秒")


def stop_auto_save():
    """停止自动保存功能"""
    global auto_save_timer
    if auto_save_timer is not None:
        # 由于使用了daemon=True，线程会在主程序结束时自动退出
        auto_save_timer = None
        from app.core.logging_config import logger
        logger.info("自动保存功能已停止")

# --------------------------
# 6. 数据加载（从SQLite数据库到内存DB）
# --------------------------
def load_chats_from_db():
    """从SQLite数据库加载对话数据"""
    global db
    
    try:
        # 使用Repository层加载对话数据
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.core.database import get_db
        from app.utils.data_utils import build_message_list, build_chat_dict
        
        # 获取数据库会话
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        message_repo = MessageRepository(db_session)
        
        # 清空内存中的对话数据
        db['chats'] = []
        
        # 获取所有对话
        chats = chat_repo.get_all_chats()
        
        for chat in chats:
            # 获取对话的所有消息
            messages = message_repo.get_messages_by_chat_id(chat.id)
            
            # 使用公共函数构建消息列表
            formatted_messages = build_message_list(messages)
            
            # 使用公共函数构建对话字典
            chat_dict = build_chat_dict(chat, formatted_messages)
            
            # 添加对话到内存数据库
            db['chats'].append(chat_dict)
        
        from app.core.logging_config import logger
        logger.info(f"从SQLite数据库加载了 {len(db['chats'])} 个对话")
        return len(db['chats']) > 0
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"从SQLite数据库加载对话数据失败: {str(e)}")
        return False




def load_data():
    """加载数据"""
    global db
    user_data_dir = ensure_data_dir()  # 先确保目录存在
    
    try:
        # 初始化数据库
        init_db()
        
        # 使用Repository层检查模型表是否为空
        from app.repositories.model_repository import ModelRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 检查模型表是否为空
        if model_repo.is_model_table_empty():
            # 数据库为空，插入默认模型数据
            insert_default_models()
        else:
            # 从SQLite加载模型数据
            load_models_from_db()
        
        # 从SQLite加载对话数据
        load_chats_from_db()
        
        # 从SQLite加载设置数据
        load_settings_from_db()
        
        # 启动自动保存功能
        start_auto_save()
        
        from app.core.logging_config import logger
        logger.info("所有数据加载成功")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"加载数据时出错: {str(e)}")

# 插入默认模型数据

def insert_default_models():
    """插入默认模型数据到SQLite数据库"""
    from app.core.logging_config import logger
    logger.info("正在插入默认模型数据...")
    
    # 默认模型列表
    default_models = [
        {
            'name': 'OpenAI',
            'description': 'OpenAI的AI模型，性价比高',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-o',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-500',
            'icon_url': '/api/models/icons/OpenAI.png',
            'versions': []
        },
        {
            'name': 'Anthropic',
            'description': 'Anthropic的Claude模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comments',
            'icon_bg': 'bg-purple-100',
            'icon_color': 'text-purple-600',
            'icon_url': '/api/models/icons/Anthropic.png',
            'versions': []
        },
        {
            'name': 'Ollama',
            'description': '本地运行的Ollama模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-server',
            'icon_bg': 'bg-green-100',
            'icon_color': 'text-green-600',
            'icon_url': '/api/models/icons/Ollama.png',
            'versions': []
        },
        {
            'name': 'GitHubModel',
            'description': 'GitHub的AI模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-github',
            'icon_bg': 'bg-gray-100',
            'icon_color': 'text-gray-600',
            'icon_url': '/api/models/icons/GitHubModel.png',
            'versions': []
        },
        {
            'name': 'DeepSeek',
            'description': '深度求索的Deepseek模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-code',
            'icon_bg': 'bg-orange-100',
            'icon_color': 'text-orange-600',
            'icon_url': '/api/models/icons/Deepseek.png',
            'versions': []
        },
        {
            'name': 'Doubao',
            'description': '字节跳动的豆包模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-robot',
            'icon_bg': 'bg-red-100',
            'icon_color': 'text-red-600',
            'icon_url': '/api/models/icons/Doubao.png',
            'versions': []
        },
        {
            'name': 'GoogleAI',
            'description': 'Google的AI模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-google',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-600',
            'icon_url': '/api/models/icons/GoogleAI.png',
            'versions': []
        },
        {
            'name': 'Huggingface',
            'description': 'Hugging Face的开源模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-hug',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-600',
            'icon_url': '/api/models/icons/Huggingface.png',
            'versions': []
        },
        {
            'name': 'Qwen',
            'description': '阿里巴巴的通义千问模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-alt',
            'icon_bg': 'bg-orange-100',
            'icon_color': 'text-orange-600',
            'icon_url': '/api/models/icons/Qwen.png',
            'versions': []
        },
        {
            'name': '文心一言',
            'description': '百度的文心一言模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-dots',
            'icon_bg': 'bg-red-100',
            'icon_color': 'text-red-600',
            'icon_url': '/api/models/icons/文心一言.png',
            'versions': []
        }
    ]
    
    try:
        # 使用Repository层插入默认模型数据
        from app.repositories.model_repository import ModelRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 将模型数据插入到数据库
        for model in default_models:
            # 创建或更新模型
            model_obj = model_repo.create_or_update_model(
                name=model['name'],
                description=model['description'],
                configured=model['configured'],
                enabled=model['enabled'],
                icon_class=model['icon_class'],
                icon_bg=model['icon_bg'],
                icon_color=model['icon_color'],
                icon_url=model.get('icon_url', ''),
                icon_blob=model.get('icon_blob', None)
            )
            
            # 获取模型ID
            model_id = model_obj.id
            
            # 插入模型版本
            def process_version(version_data):
                """处理单个模型版本的创建或更新"""
                model_repo.create_or_update_model_version(
                    model_id=model_id,
                    version_name=version_data['version_name'],
                    custom_name=version_data.get('custom_name', ''),
                    api_key=version_data.get('api_key', ''),
                    api_base_url=version_data.get('api_base_url', ''),
                    streaming_config=version_data.get('streaming_config', False)
                )
            
            for version in model.get('versions', []):
                process_version(version)
        
        logger.info("默认模型数据插入完成")
        
        # 从数据库加载数据到内存
        load_models_from_db()
    except Exception as e:
        logger.error(f"插入默认模型数据失败: {str(e)}")
        raise

# 从SQLite数据库加载模型数据到内存

def load_models_from_db():
    """从SQLite数据库加载模型数据到内存"""
    global db
    
    try:
        # 使用Repository层加载模型数据
        from app.repositories.model_repository import ModelRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 清空内存中的模型数据
        db['models'] = []
        
        # 获取所有模型
        models = model_repo.get_all_models()
        
        for model in models:
            # 获取模型的所有版本
            versions = model_repo.get_model_versions(model.id)
            
            # 构建版本列表
            version_list = []
            for version in versions:
                version_list.append({
                    'version_name': version.version_name,
                    'custom_name': version.custom_name,
                    'api_key': version.api_key,
                    'api_base_url': version.api_base_url,
                    'streaming_config': version.streaming_config
                })
            
            # 添加模型到内存数据库
            db['models'].append({
                'name': model.name,
                'description': model.description,
                'configured': bool(model.configured),
                'enabled': bool(model.enabled),
                'icon_class': model.icon_class,
                'icon_bg': model.icon_bg,
                'icon_color': model.icon_color,
                'icon_url': model.icon_url,
                'icon_blob': model.icon_blob,
                'versions': version_list
            })
        
        from app.core.logging_config import logger
        logger.info(f"从SQLite数据库加载了 {len(db['models'])} 个模型")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"从SQLite数据库加载模型数据失败: {str(e)}")

# 从SQLite数据库加载设置数据到内存

def load_settings_from_db():
    """从SQLite数据库加载设置数据到内存"""
    global db
    
    try:
        # 使用Repository层加载设置数据
        from app.repositories.setting_repository import SettingRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        setting_repo = SettingRepository(db_session)
        
        # 从新的独立设置表加载数据
        # 加载向量设置
        vector_setting = setting_repo.get_vector_setting()
        if vector_setting:
            db['settings']['vector'] = {
                'retrieval_mode': vector_setting.retrieval_mode,
                'top_k': vector_setting.top_k,
                'score_threshold': vector_setting.score_threshold,
                'vector_db_path': vector_setting.vector_db_path,
                'embedder_model': vector_setting.embedder_model,
                'chunk_size': vector_setting.chunk_size,
                'chunk_overlap': vector_setting.chunk_overlap
            }
        

        
        # 加载应用设置
        app_setting = setting_repo.get_app_setting()
        if app_setting:
            db['settings']['app'] = {
                'debug': app_setting.debug,
                'host': app_setting.host,
                'port': app_setting.port
            }
        
        # 加载系统设置（包含通知设置）
        system_setting = setting_repo.get_system_setting()
        if system_setting:
            db['settings']['system'] = {
                'dark_mode': system_setting.dark_mode,
                'font_size': system_setting.font_size,
                'font_family': system_setting.font_family,
                'language': system_setting.language,
                'auto_scroll': system_setting.auto_scroll,
                'show_timestamps': system_setting.show_timestamps,
                'confirm_delete': system_setting.confirm_delete,
                'streaming_enabled': system_setting.streaming_enabled,
                'chat_style_document': system_setting.chat_style_document,
                'view_mode': system_setting.view_mode,
                'default_model': system_setting.default_model,
                'rag_view_mode': system_setting.rag_view_mode
            }
            
            # 加载通知设置（从系统设置中获取）
            db['settings']['notification'] = {
                'enabled': system_setting.enabled,
                'newMessage': system_setting.new_message,
                'sound': system_setting.sound,
                'system': system_setting.system,
                'displayTime': system_setting.display_time
            }
        
        from app.core.logging_config import logger
        logger.info("从SQLite数据库加载了设置数据")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"从SQLite数据库加载设置数据失败: {str(e)}")
        # 保持现有设置不变

# 将设置数据保存到SQLite数据库

def save_settings_to_db(conn=None):
    """将设置数据保存到SQLite数据库"""
    global db
    
    try:
        # 使用Repository层保存设置数据
        from app.repositories.setting_repository import SettingRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        setting_repo = SettingRepository(db_session)
        
        # 将设置保存到新的独立设置表中
        # 保存向量设置
        if 'vector' in db['settings']:
            vector_data = db['settings']['vector']
            setting_repo.create_or_update_vector_setting(vector_data)
        

        
        # 保存通知设置
        if 'notification' in db['settings']:
            notification_data = db['settings']['notification']
            # 转换为数据库字段名（驼峰命名转换为下划线命名）
            notification_db_data = {
                'enabled': notification_data.get('enabled', True),
                'new_message': notification_data.get('newMessage', True),
                'sound': notification_data.get('sound', False),
                'system': notification_data.get('system', True),
                'display_time': notification_data.get('displayTime', '5秒')
            }
            setting_repo.create_or_update_notification_setting(notification_db_data)
        
        # 保存应用设置
        if 'app' in db['settings']:
            app_data = db['settings']['app']
            setting_repo.create_or_update_app_setting(app_data)
        
        # 保存系统设置
        if 'system' in db['settings']:
            system_data = db['settings']['system']
            # 转换为数据库字段名（驼峰命名转换为下划线命名）
            system_db_data = {
                'dark_mode': system_data.get('dark_mode', False),
                'font_size': system_data.get('font_size', 16),
                'font_family': system_data.get('font_family', 'Inter, system-ui, sans-serif'),
                'language': system_data.get('language', 'zh-CN'),
                'auto_scroll': system_data.get('auto_scroll', True),
                'show_timestamps': system_data.get('show_timestamps', True),
                'confirm_delete': system_data.get('confirm_delete', True),
                'streaming_enabled': system_data.get('streaming_enabled', True),
                'chat_style_document': system_data.get('chat_style_document', False),
                'view_mode': system_data.get('view_mode', 'grid'),
                'default_model': system_data.get('default_model', ''),
                'rag_view_mode': system_data.get('rag_view_mode', True)
            }
            setting_repo.create_or_update_system_setting(system_db_data)
        
        from app.core.logging_config import logger
        logger.info("设置数据已保存到SQLite数据库")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"保存设置数据到SQLite失败: {str(e)}")
        raise

# --------------------------
# 5. 数据保存（从内存DB到SQLite和JSON文件）
# --------------------------
def save_chats_to_db(conn=None):
    """将对话数据保存到SQLite数据库"""
    global db
    
    try:
        # 使用Repository层保存对话数据
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        message_repo = MessageRepository(db_session)
        
        # 获取SQLite中所有对话ID
        all_chats = chat_repo.get_all_chats()
        sqlite_chat_ids = {chat.id for chat in all_chats}
        
        # 获取内存中所有对话ID
        memory_chat_ids = {chat['id'] for chat in db['chats']}
        
        # 找出需要删除的对话ID
        chat_ids_to_delete = sqlite_chat_ids - memory_chat_ids
        
        # 删除不再存在于内存中的对话（会级联删除消息）
        if chat_ids_to_delete:
            from app.core.logging_config import logger
            logger.info(f"删除不存在于内存的对话: {len(chat_ids_to_delete)} 个")
            for chat_id in chat_ids_to_delete:
                chat_repo.delete_chat(chat_id)
        
        # 保存所有对话和消息
        for chat in db['chats']:
            chat_id = chat['id']
            title = chat['title']
            preview = chat.get('preview', '')
            created_at = chat['createdAt']
            updated_at = chat['updatedAt']
            pinned = chat.get('pinned', 0)
            
            # 创建或更新对话
            db_chat = chat_repo.get_chat_by_id(chat_id)
            if db_chat:
                # 更新现有对话
                chat_repo.update_chat(chat_id, title, preview, updated_at, pinned)
            else:
                # 创建新对话
                chat_repo.create_chat(chat_id, title, preview, created_at, updated_at)
            
            # 获取SQLite中该对话的所有消息ID
            sqlite_messages = message_repo.get_messages_by_chat_id(chat_id)
            sqlite_msg_ids = {msg.id for msg in sqlite_messages}
            
            # 获取内存中该对话的所有消息ID
            memory_msg_ids = {msg['id'] for msg in chat.get('messages', [])}
            
            # 找出需要删除的消息ID
            msg_ids_to_delete = sqlite_msg_ids - memory_msg_ids
            
            # 删除不再存在于内存中的消息
            if msg_ids_to_delete:
                for msg_id in msg_ids_to_delete:
                    message_repo.delete_message(msg_id)
            
            # 保存对话中的消息
            for msg in chat.get('messages', []):
                msg_id = msg['id']
                role = msg['role']
                content = msg['content']
                reasoning_content = msg.get('reasoning_content', None)
                # 确保createdAt有值，即使键存在但值为None也使用默认值
                msg_created_at = msg.get('createdAt') or datetime.now().isoformat()
                model = msg.get('model', None)
                files = msg.get('files', [])
                
                # 智能体消息相关字段
                message_type = msg.get('message_type', 'normal')
                agent_session_id = msg.get('agent_session_id')
                agent_node = msg.get('agent_node')
                agent_step = msg.get('agent_step')
                agent_metadata = msg.get('agent_metadata')
                
                # 将files列表转换为JSON字符串
                files_json = json.dumps(files)
                
                # 创建或更新消息
                message_repo.create_or_update_message(
                    msg_id, chat_id, role, content, reasoning_content, msg_created_at, model, files_json,
                    message_type, agent_session_id, agent_node, agent_step, agent_metadata
                )
        
        from app.core.logging_config import logger
        logger.info("对话数据已保存到SQLite数据库")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"保存对话数据到SQLite失败: {str(e)}")
        raise

def set_dirty_flag(data_type, is_dirty=True):
    """设置数据脏标记
    
    参数:
        data_type: 数据类型，可选值: 'chats', 'models', 'settings'
        is_dirty: 是否为脏数据，默认为True
    """
    if data_type in dirty_flags:
        dirty_flags[data_type] = is_dirty


def save_data():
    """保存数据到SQLite数据库，只保存有脏标记的数据"""
    try:
        # 记录需要保存的数据类型
        saved_types = []
        
        # 只保存有脏标记的数据
        if dirty_flags['chats']:
            save_chats_to_db()
            saved_types.append('chats')
            dirty_flags['chats'] = False
        
        if dirty_flags['models']:
            save_models_to_db()
            saved_types.append('models')
            dirty_flags['models'] = False
        
        if dirty_flags['settings']:
            save_settings_to_db()
            saved_types.append('settings')
            dirty_flags['settings'] = False
        
        if dirty_flags['agent_sessions']:
            save_agent_sessions_to_db()
            saved_types.append('agent_sessions')
            dirty_flags['agent_sessions'] = False
        
        # 不需要提交事务，Repository层会处理
        
        from app.core.logging_config import logger
        if saved_types:
            logger.info(f"数据已保存到SQLite: {', '.join(saved_types)}")
        else:
            logger.info("没有数据需要保存")
            
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"保存数据时出错: {str(e)}")

# 将智能体会话数据保存到SQLite数据库

def save_agent_sessions_to_db(conn=None):
    """将智能体会话数据保存到SQLite数据库"""
    try:
        # 使用Repository层保存智能体会话数据
        from app.repositories.agent_session_repository import AgentSessionRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        agent_session_repo = AgentSessionRepository(db_session)
        
        # 获取SQLite中所有智能体会话ID
        all_sessions = agent_session_repo.get_all_sessions()
        sqlite_session_ids = {session.id for session in all_sessions}
        
        # 获取内存中所有智能体会话ID
        memory_session_ids = {session['id'] for session in db['agent_sessions']}
        
        # 找出需要删除的智能体会话ID
        session_ids_to_delete = sqlite_session_ids - memory_session_ids
        
        # 删除不再存在于内存中的智能体会话
        if session_ids_to_delete:
            from app.core.logging_config import logger
            logger.info(f"删除不存在于内存的智能体会话: {len(session_ids_to_delete)} 个")
            for session_id in session_ids_to_delete:
                agent_session_repo.delete_session(session_id)
        
        # 保存所有智能体会话
        for session in db['agent_sessions']:
            # 将graph_state转换为JSON字符串
            graph_state = session.get('graph_state')
            if graph_state is not None and isinstance(graph_state, dict):
                import json
                graph_state = json.dumps(graph_state)
            
            # 创建或更新智能体会话
            agent_session_repo.create_or_update_session(
                session_id=session['id'],
                chat_id=session['chat_id'],
                created_at=session['created_at'],
                updated_at=session['updated_at'],
                graph_state=graph_state,
                current_node=session.get('current_node', ''),
                step_count=session.get('step_count', 0)
            )
        
        from app.core.logging_config import logger
        logger.info("智能体会话数据已保存到SQLite数据库")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"保存智能体会话数据到SQLite失败: {str(e)}")
        raise


# 将模型数据保存到SQLite数据库

def save_models_to_db(conn=None):
    """将模型数据保存到SQLite数据库"""
    try:
        # 使用Repository层保存模型数据
        from app.repositories.model_repository import ModelRepository
        from app.core.database import get_db
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 获取SQLite中所有模型
        all_models = model_repo.get_all_models()
        sqlite_model_names = {model.name for model in all_models}
        
        # 获取内存中所有模型名称
        memory_model_names = {model['name'] for model in db['models']}
        
        # 找出需要删除的模型名称
        model_names_to_delete = sqlite_model_names - memory_model_names
        
        # 删除不再存在于内存中的模型
        if model_names_to_delete:
            from app.core.logging_config import logger
            logger.info(f"删除不存在于内存的模型: {len(model_names_to_delete)} 个")
            for model_name in model_names_to_delete:
                # 获取模型并删除
                model = model_repo.get_model_by_name(model_name)
                if model:
                    model_repo.delete(model)
        
        # 保存所有模型及其版本
        for model in db['models']:
            # 更新模型
            model_repo.update_model(
                name=model['name'],
                description=model['description'],
                configured=model['configured'],
                enabled=model['enabled'],
                icon_class=model['icon_class'],
                icon_bg=model['icon_bg'],
                icon_color=model['icon_color'],
                icon_url=model.get('icon_url', ''),
                icon_blob=model.get('icon_blob', None)
            )
            
            # 获取模型ID
            model_obj = model_repo.get_model_by_name(model['name'])
            model_id = model_obj.id
            
            # 获取现有版本名称列表
            existing_versions = model_repo.get_model_versions(model_id)
            existing_version_names = {version.version_name for version in existing_versions}
            
            # 要保存的版本名称集合
            new_versions = model.get('versions', [])
            new_version_names = {version['version_name'] for version in new_versions}
            
            # 删除不再存在的版本
            versions_to_delete = existing_version_names - new_version_names
            for version_name in versions_to_delete:
                model_repo.delete_model_version(model_id, version_name)
            
            # 插入或更新版本
            def update_version(version_data):
                """处理单个模型版本的更新"""
                model_repo.update_model_version(
                    model_id=model_id,
                    version_name=version_data['version_name'],
                    custom_name=version_data.get('custom_name', ''),
                    api_key=version_data.get('api_key', ''),
                    api_base_url=version_data.get('api_base_url', ''),
                    streaming_config=version_data.get('streaming_config', False)
                )
            
            for version in new_versions:
                update_version(version)
        
        from app.core.logging_config import logger
        logger.info("模型数据已保存到SQLite数据库")
    except Exception as e:
        from app.core.logging_config import logger
        logger.error(f"保存模型数据到SQLite失败: {str(e)}")
        raise