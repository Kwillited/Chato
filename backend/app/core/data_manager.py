"""数据管理模块"""
import json
import os
import threading
import time
from datetime import datetime
from app.core.config import config_manager
from app.repositories.cache_repository import CacheRepository
from app.core.database import get_db, init_alembic_db
from app.core.logger import logger

# 创建全局 Repository 实例
cache_repo = CacheRepository()

# 自动保存定时器
AUTO_SAVE_INTERVAL = 5  # 自动保存间隔（秒）
auto_save_timer = None

# 事务锁，确保数据一致性
transaction_lock = threading.Lock()

# --------------------------
# 1. 数据目录管理
# --------------------------
def ensure_data_dir():
    """确保数据目录存在"""
    user_data_dir = config_manager.get_user_data_dir()
    return user_data_dir

# --------------------------
# 2. 数据库初始化
# --------------------------
def init_db():
    """初始化SQLite数据库，创建表结构"""
    user_data_dir = ensure_data_dir()
    db_path = os.path.join(user_data_dir, 'config', 'chato.db')
    
    # 确保config目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 使用SQLAlchemy的自动创建表功能
    init_alembic_db()
    logger.info(f"SQLite数据库初始化成功，数据库文件: {db_path}")

# --------------------------
# 3. 事务管理
# --------------------------
def begin_transaction():
    """开始事务，获取锁"""
    transaction_lock.acquire()
    logger.debug("事务开始")


def commit_transaction():
    """提交事务，释放锁并保存数据"""
    try:
        save_data()
        logger.debug("事务提交")
    finally:
        transaction_lock.release()


def rollback_transaction():
    """回滚事务，释放锁"""
    transaction_lock.release()
    logger.debug("事务回滚")

# --------------------------
# 4. 自动保存功能
# --------------------------
def auto_save_task():
    """自动保存任务，定期检查脏标记并保存数据"""
    while True:
        time.sleep(AUTO_SAVE_INTERVAL)
        with transaction_lock:
            # 检查是否有脏数据需要保存
            dirty_keys = []
            for key in ['chats', 'models', 'embedding_models', 'settings']:
                if cache_repo.is_dirty(key):
                    dirty_keys.append(key)
            if dirty_keys:
                logger.info(f"自动保存触发: 脏标记={dirty_keys}")
                save_data()
                logger.info("自动保存完成")


def start_auto_save():
    """启动自动保存功能"""
    global auto_save_timer
    if auto_save_timer is None or not auto_save_timer.is_alive():
        auto_save_timer = threading.Thread(target=auto_save_task, daemon=True)
        auto_save_timer.start()
        logger.info(f"自动保存功能已启动，间隔: {AUTO_SAVE_INTERVAL}秒")


def stop_auto_save():
    """停止自动保存功能"""
    global auto_save_timer
    if auto_save_timer is not None:
        # 由于使用了daemon=True，线程会在主程序结束时自动退出
        auto_save_timer = None
        logger.info("自动保存功能已停止")

# --------------------------
# 5. 数据加载（从SQLite数据库到内存缓存）
# --------------------------
def load_chats_from_db():
    """从SQLite数据库加载对话数据"""
    try:
        # 使用Repository层加载对话数据
        from app.repositories.chat_repository import ChatRepository
        from app.models.database.models import Chat
        
        # 获取数据库会话
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        
        # 清空内存中的对话数据
        cache_repo.set('chats', {})
        
        # 获取所有对话，加载必要的字段
        chats = db_session.query(Chat.id, Chat.title, Chat.created_at, Chat.updated_at, Chat.pinned).order_by(Chat.updated_at.desc()).all()
        
        chat_dict = {}
        for chat_id, title, created_at, updated_at, pinned in chats:
            # 构建对话字典，包含必要的字段
            chat_data = {
                'id': chat_id,
                'title': title,
                'createdAt': created_at,
                'updatedAt': updated_at,
                'pinned': bool(pinned),
                'messages': []
            }
            # 添加对话到字典
            chat_dict[chat_id] = chat_data
        
        # 更新缓存
        cache_repo.set('chats', chat_dict)
        # 清除所有对话脏标记
        cache_repo.clear_dirty_flag('chats')
        
        logger.info(f"从SQLite数据库加载了 {len(chat_dict)} 个对话")
        return len(chat_dict) > 0
    except Exception as e:
        logger.error(f"从SQLite数据库加载对话数据失败: {str(e)}")
        return False


def load_models_from_db():
    """从SQLite数据库加载模型数据到内存"""
    try:
        # 使用Repository层加载模型数据
        from app.repositories.model_repository import ModelRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 获取所有模型
        models = model_repo.get_all_models()
        
        model_list = []
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
            
            # 添加模型到列表
            model_list.append({
                'name': model.name,
                'description': model.description,
                'configured': bool(model.configured),
                'enabled': bool(model.enabled),
                'icon_url': model.icon_url,
                'icon_blob': model.icon_blob,
                'versions': version_list
            })
        
        # 更新缓存
        cache_repo.set('models', model_list)
        # 清除脏标记
        cache_repo.clear_dirty_flag('models')
        
        logger.info(f"从SQLite数据库加载了 {len(model_list)} 个模型")
    except Exception as e:
        logger.error(f"从SQLite数据库加载模型数据失败: {str(e)}")


def load_embedding_models_from_db():
    """从SQLite数据库加载嵌入模型数据到内存"""
    try:
        # 使用Repository层加载嵌入模型数据
        from app.repositories.embedding_model_repository import EmbeddingModelRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        embedding_model_repo = EmbeddingModelRepository(db_session)
        
        # 获取所有嵌入模型
        models = embedding_model_repo.get_all_models()
        
        model_list = []
        for model in models:
            # 获取模型的所有版本
            versions = embedding_model_repo.get_model_versions(model.id)
            
            # 构建版本列表
            version_list = []
            for version in versions:
                version_list.append({
                    'version_name': version.version_name,
                    'custom_name': version.custom_name,
                    'api_key': version.api_key,
                    'api_base_url': version.api_base_url,
                    'model_path': version.model_path,
                    'dimension': version.dimension
                })
            
            # 添加模型到列表
            model_list.append({
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'type': model.type,
                'configured': bool(model.configured),
                'enabled': bool(model.enabled),
                'icon_url': model.icon_url,
                'versions': version_list
            })
        
        # 更新缓存
        cache_repo.set('embedding_models', model_list)
        # 清除脏标记
        cache_repo.clear_dirty_flag('embedding_models')
        
        logger.info(f"从SQLite数据库加载了 {len(model_list)} 个嵌入模型")
    except Exception as e:
        logger.error(f"从SQLite数据库加载嵌入模型数据失败: {str(e)}")


def load_settings_from_db():
    """从SQLite数据库加载设置数据到内存"""
    try:
        # 使用Repository层加载设置数据
        from app.repositories.setting_repository import SettingRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        setting_repo = SettingRepository(db_session)
        
        # 加载系统设置（包含通知设置和向量相关设置）
        system_setting = setting_repo.get_system_setting()
        if system_setting:
            settings = cache_repo.get('settings') or {}
            
            # 系统设置 - 统一使用驼峰命名存储在内存中
            settings['system'] = {
                'darkMode': system_setting.dark_mode,
                'streamingEnabled': system_setting.streaming_enabled,
                'chatStyle': system_setting.chat_style,
                'viewMode': system_setting.view_mode,
                'defaultModel': system_setting.default_model,
                'vector_db_path': system_setting.vector_db_path,
                'default_top_k': system_setting.default_top_k,
                'default_score_threshold': system_setting.default_score_threshold,
                # 通知相关字段
                'newMessage': system_setting.new_message,
                'sound': system_setting.sound,
                'system': system_setting.system,
                'displayTime': system_setting.display_time
            }
            
            cache_repo.set('settings', settings)
        
        # 清除脏标记
        cache_repo.clear_dirty_flag('settings')
        
        logger.info("从SQLite数据库加载了设置数据")
    except Exception as e:
        logger.error(f"从SQLite数据库加载设置数据失败: {str(e)}")







# 插入默认模型数据
def insert_default_embedding_models():
    """插入默认嵌入模型数据到SQLite数据库"""
    logger.info("正在插入默认嵌入模型数据...")
    
    # 读取图标文件
    import os
    import base64
    icon_dir = r'h:\ChaTo\icon'
    
    def get_icon_blob(icon_name):
        """获取图标文件的内容"""
        # 尝试不同的文件名格式
        possible_filenames = [
            f'{icon_name}.svg',
            f'{icon_name.lower()}.svg',
            f'{icon_name.capitalize()}.svg'
        ]
        
        for filename in possible_filenames:
            icon_path = os.path.join(icon_dir, filename)
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
    
    default_embedding_providers = [
        {
            'name': 'HuggingFace',
            'description': 'Hugging Face的开源嵌入模型',
            'type': 'huggingface',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Huggingface.svg',
            'icon_blob': get_icon_blob('Huggingface'),
            'versions': []
        },
        {
            'name': 'OpenAI',
            'description': 'OpenAI的嵌入模型',
            'type': 'openai',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/OpenAI.svg',
            'icon_blob': get_icon_blob('OpenAI'),
            'versions': []
        },
        {
            'name': 'Ollama',
            'description': '本地运行的Ollama嵌入模型',
            'type': 'ollama',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Ollama.svg',
            'icon_blob': get_icon_blob('Ollama'),
            'versions': []
        }
    ]
    
    try:
        # 使用Repository层插入默认嵌入模型数据
        from app.repositories.embedding_model_repository import EmbeddingModelRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        embedding_model_repo = EmbeddingModelRepository(db_session)
        
        # 将模型数据插入到数据库
        for provider in default_embedding_providers:
            # 创建或更新模型
            model_data = {
                'name': provider['name'],
                'description': provider['description'],
                'type': provider['type'],
                'configured': provider['configured'],
                'enabled': provider['enabled'],
                'icon_url': provider.get('icon_url', '')
            }
            
            model_obj = embedding_model_repo.create_model(model_data)
            
            # 获取模型ID
            model_id = model_obj.id
            
            # 插入模型版本
            for version in provider.get('versions', []):
                version_data = {
                    'model_id': model_id,
                    'version_name': version['version_name'],
                    'custom_name': version.get('custom_name', ''),
                    'api_key': version.get('api_key', ''),
                    'api_base_url': version.get('api_base_url', ''),
                    'model_path': version.get('model_path', ''),
                    'dimension': version.get('dimension', 0)
                }
                embedding_model_repo.create_model_version(version_data)
        
        logger.info("默认嵌入模型数据插入完成")
        
        # 从数据库加载数据到内存
        load_embedding_models_from_db()
    except Exception as e:
        logger.error(f"插入默认嵌入模型数据失败: {str(e)}")
        raise


def insert_default_models():
    """插入默认模型数据到SQLite数据库"""
    logger.info("正在插入默认模型数据...")
    
    # 读取图标文件
    import os
    import base64
    icon_dir = r'h:\ChaTo\icon'
    
    def get_icon_blob(icon_name):
        """获取图标文件的内容"""
        # 映射模型名称到图标文件名
        icon_name_mapping = {
            'Anthropic': 'claude',
            'GitHubModel': 'github',
            'DeepSeek': 'deepseek',
            'Doubao': 'doubao',
            'GoogleAI': 'gemini',
            'Huggingface': 'huggingface',
            'Qwen': 'qwen',
            '文心一言': '文心一言'
        }
        
        # 获取实际的图标文件名
        actual_icon_name = icon_name_mapping.get(icon_name, icon_name)
        
        # 尝试不同的文件名格式
        possible_filenames = [
            f'{actual_icon_name}.svg',
            f'{actual_icon_name.lower()}.svg',
            f'{actual_icon_name.capitalize()}.svg'
        ]
        
        for filename in possible_filenames:
            icon_path = os.path.join(icon_dir, filename)
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
    
    # 默认模型列表
    default_models = [
        {
            'name': 'OpenAI',
            'description': 'OpenAI的AI模型，性价比高',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/OpenAI.svg',
            'icon_blob': get_icon_blob('OpenAI'),
            'versions': []
        },
        {
            'name': 'Anthropic',
            'description': 'Anthropic的Claude模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Anthropic.svg',
            'icon_blob': get_icon_blob('Anthropic'),
            'versions': []
        },
        {
            'name': 'Ollama',
            'description': '本地运行的Ollama模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Ollama.svg',
            'icon_blob': get_icon_blob('Ollama'),
            'versions': []
        },
        {
            'name': 'GitHubModel',
            'description': 'GitHub的AI模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/GitHubModel.svg',
            'icon_blob': get_icon_blob('GitHubModel'),
            'versions': []
        },
        {
            'name': 'DeepSeek',
            'description': '深度求索的Deepseek模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/DeepSeek.svg',
            'icon_blob': get_icon_blob('DeepSeek'),
            'versions': []
        },
        {
            'name': 'Doubao',
            'description': '字节跳动的豆包模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Doubao.svg',
            'icon_blob': get_icon_blob('Doubao'),
            'versions': []
        },
        {
            'name': 'GoogleAI',
            'description': 'Google的AI模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/GoogleAI.svg',
            'icon_blob': get_icon_blob('GoogleAI'),
            'versions': []
        },
        {
            'name': 'Huggingface',
            'description': 'Hugging Face的开源模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Huggingface.svg',
            'icon_blob': get_icon_blob('Huggingface'),
            'versions': []
        },
        {
            'name': 'Qwen',
            'description': '阿里巴巴的通义千问模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/Qwen.svg',
            'icon_blob': get_icon_blob('Qwen'),
            'versions': []
        },
        {
            'name': '文心一言',
            'description': '百度的文心一言模型',
            'configured': False,
            'enabled': False,
            'icon_url': '/api/models/icons/文心一言.svg',
            'icon_blob': get_icon_blob('文心一言'),
            'versions': []
        }
    ]
    
    try:
        # 使用Repository层插入默认模型数据
        from app.repositories.model_repository import ModelRepository
        
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

# --------------------------
# 6. 数据保存（从内存缓存到SQLite数据库）
# --------------------------
def save_chats_to_db():
    """将对话数据保存到SQLite数据库（增量更新）"""
    try:
        # 直接操作SQLite数据库，避免使用Repository层导致的会话冲突
        from app.models.database.models import Chat, Message
        
        # 获取数据库会话
        db_session = next(get_db())
        
        # 获取内存中的对话数据
        chats = cache_repo.get('chats') or {}
        
        # 获取所有脏对话ID
        dirty_chat_ids = cache_repo.get_dirty_chats()
        
        if not dirty_chat_ids:
            logger.info("没有脏对话需要保存")
            return True
        
        # 获取数据库中的所有对话
        db_chats = db_session.query(Chat).all()
        db_chat_dict = {chat.id: chat for chat in db_chats}
        
        # 处理对话的增量更新
        added_chats = 0
        updated_chats = 0
        deleted_chats = 0
        
        for chat_id in dirty_chat_ids:
            # 检查对话是否在内存中存在
            if chat_id in chats:
                chat = chats[chat_id]
                # 检查对话是否已存在
                if chat_id in db_chat_dict:
                    # 更新现有对话
                    db_chat = db_chat_dict[chat_id]
                    db_chat.title = chat['title']
                    db_chat.preview = chat.get('preview', '')
                    db_chat.updated_at = chat['updatedAt']
                    db_chat.pinned = chat.get('pinned', 0)
                    updated_chats += 1
                else:
                    # 添加新对话
                    new_chat = Chat(
                        id=chat_id,
                        title=chat['title'],
                        preview=chat.get('preview', ''),
                        created_at=chat['createdAt'],
                        updated_at=chat['updatedAt'],
                        pinned=chat.get('pinned', 0)
                    )
                    db_session.add(new_chat)
                    added_chats += 1
                
                # 处理消息的增量更新
                messages = chat.get('messages', [])
                
                for msg in messages:
                    msg_id = msg['id']
                    
                    # 检查消息是否已存在
                    existing_msg = db_session.query(Message).filter(
                        Message.chat_id == chat_id,
                        Message.id == msg_id
                    ).first()
                    
                    if existing_msg:
                        # 更新现有消息
                        existing_msg.role = msg['role']
                        existing_msg.content = msg['content']
                        existing_msg.reasoning_content = msg.get('reasoning_content', None)
                        existing_msg.created_at = msg.get('createdAt') or datetime.now().isoformat()
                        existing_msg.model = msg.get('model', None)
                        existing_msg.files = json.dumps(msg.get('files', []))
                        existing_msg.agent_node = msg.get('agent_node')
                        existing_msg.agent_step = msg.get('agent_step')
                        existing_msg.agent_metadata = msg.get('agent_metadata')
                    else:
                        # 添加新消息
                        new_message = Message(
                            id=msg_id,
                            chat_id=chat_id,
                            role=msg['role'],
                            content=msg['content'],
                            reasoning_content=msg.get('reasoning_content', None),
                            created_at=msg.get('createdAt') or datetime.now().isoformat(),
                            model=msg.get('model', None),
                            files=json.dumps(msg.get('files', [])),
                            agent_node=msg.get('agent_node'),
                            agent_step=msg.get('agent_step'),
                            agent_metadata=msg.get('agent_metadata')
                        )
                        db_session.add(new_message)
            else:
                # 处理删除操作：对话在脏标记中但不在内存中
                if chat_id in db_chat_dict:
                    # 删除相关的消息
                    db_session.query(Message).filter(Message.chat_id == chat_id).delete()
                    # 删除对话
                    db_session.delete(db_chat_dict[chat_id])
                    deleted_chats += 1
        
        # 提交所有操作
        db_session.commit()
        
        # 清除脏标记
        for chat_id in dirty_chat_ids:
            cache_repo.clear_chat_dirty_flag(chat_id)
        
        logger.info(f"对话数据已保存到SQLite数据库: 添加{added_chats}个对话, 更新{updated_chats}个对话, 删除{deleted_chats}个对话")
        return True
    except Exception as e:
        logger.error(f"保存对话数据到SQLite失败: {str(e)}")
        # 回滚事务
        try:
            db_session.rollback()
        except:
            pass
        return False

def save_models_to_db():
    """将模型数据保存到SQLite数据库"""
    try:
        # 使用Repository层保存模型数据
        from app.repositories.model_repository import ModelRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        model_repo = ModelRepository(db_session)
        
        # 获取内存中的模型数据
        models = cache_repo.get('models')
        if not models:
            logger.info("内存中没有模型数据，跳过保存")
            return True
        
        # 获取SQLite中所有模型
        all_models = model_repo.get_all_models()
        sqlite_model_names = {model.name for model in all_models}
        
        # 获取内存中所有模型名称
        memory_model_names = {model['name'] for model in models}
        
        # 找出需要删除的模型名称
        model_names_to_delete = sqlite_model_names - memory_model_names
        
        # 删除不再存在于内存中的模型
        if model_names_to_delete:
            logger.info(f"删除不存在于内存的模型: {len(model_names_to_delete)} 个")
            for model_name in model_names_to_delete:
                # 获取模型并删除
                model = model_repo.get_model_by_name(model_name)
                if model:
                    model_repo.delete(model)
        
        # 保存所有模型及其版本
        for model in models:
            # 更新模型
            model_repo.update_model(
                name=model['name'],
                description=model['description'],
                configured=model['configured'],
                enabled=model['enabled'],
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
        
        logger.info("模型数据已保存到SQLite数据库")
        return True
    except Exception as e:
        logger.error(f"保存模型数据到SQLite失败: {str(e)}")
        # 回滚事务
        try:
            db_session.rollback()
        except:
            pass
        return False

def save_embedding_models_to_db():
    """将嵌入模型数据保存到SQLite数据库"""
    try:
        # 使用Repository层保存嵌入模型数据
        from app.repositories.embedding_model_repository import EmbeddingModelRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        embedding_model_repo = EmbeddingModelRepository(db_session)
        
        # 获取内存中的嵌入模型数据
        models = cache_repo.get('embedding_models')
        if not models:
            logger.info("内存中没有嵌入模型数据，跳过保存")
            return True
        
        # 获取SQLite中所有嵌入模型
        all_models = embedding_model_repo.get_all_models()
        sqlite_model_names = {model.name for model in all_models}
        
        # 获取内存中所有嵌入模型名称
        memory_model_names = {model['name'] for model in models}
        
        # 找出需要删除的模型名称
        model_names_to_delete = sqlite_model_names - memory_model_names
        
        # 删除不再存在于内存中的模型
        if model_names_to_delete:
            logger.info(f"删除不存在于内存的嵌入模型: {len(model_names_to_delete)} 个")
            for model_name in model_names_to_delete:
                model = embedding_model_repo.get_model_by_name(model_name)
                if model:
                    embedding_model_repo.delete_model(model.id)
        
        # 保存所有嵌入模型及其版本
        for model in models:
            # 准备模型数据
            model_data = {
                'name': model['name'],
                'description': model['description'],
                'type': model['type'],
                'configured': model['configured'],
                'enabled': model['enabled'],
                'icon_url': model.get('icon_url', '')
            }
            
            # 获取或创建模型
            existing_model = embedding_model_repo.get_model_by_name(model['name'])
            if existing_model:
                # 更新现有模型
                updated_model = embedding_model_repo.update_model(existing_model.id, model_data)
                model_id = updated_model.id
            else:
                # 创建新模型
                new_model = embedding_model_repo.create_model(model_data)
                model_id = new_model.id
            
            # 获取现有版本名称列表
            existing_versions = embedding_model_repo.get_model_versions(model_id)
            existing_version_names = {version.version_name for version in existing_versions}
            
            # 要保存的版本名称集合
            new_versions = model.get('versions', [])
            new_version_names = {version['version_name'] for version in new_versions}
            
            # 删除不再存在的版本
            versions_to_delete = existing_version_names - new_version_names
            for version_name in versions_to_delete:
                version = embedding_model_repo.get_version_by_name(model_id, version_name)
                if version:
                    embedding_model_repo.delete_model_version(version.id)
            
            # 插入或更新版本
            for version in new_versions:
                version_data = {
                    'model_id': model_id,
                    'version_name': version['version_name'],
                    'custom_name': version.get('custom_name', ''),
                    'api_key': version.get('api_key', ''),
                    'api_base_url': version.get('api_base_url', ''),
                    'model_path': version.get('model_path', ''),
                    'dimension': version.get('dimension', 0)
                }
                
                # 检查版本是否已存在
                existing_version = embedding_model_repo.get_version_by_name(model_id, version['version_name'])
                if existing_version:
                    # 更新现有版本
                    embedding_model_repo.update_model_version(existing_version.id, version_data)
                else:
                    # 创建新版本
                    embedding_model_repo.create_model_version(version_data)
        
        logger.info("嵌入模型数据已保存到SQLite数据库")
        return True
    except Exception as e:
        logger.error(f"保存嵌入模型数据到SQLite失败: {str(e)}")
        # 回滚事务
        try:
            db_session.rollback()
        except:
            pass
        return False

def save_settings_to_db():
    """将设置数据保存到SQLite数据库"""
    try:
        # 使用Repository层保存设置数据
        from app.repositories.setting_repository import SettingRepository
        
        # 获取数据库会话
        db_session = next(get_db())
        setting_repo = SettingRepository(db_session)
        
        # 获取内存中的设置数据
        settings = cache_repo.get('settings')
        if not settings:
            logger.info("内存中没有设置数据，跳过保存")
            return True
        
        # 保存系统设置（包含向量相关设置）
        if 'system' in settings:
            system_data = settings['system']
            # 转换为数据库字段名（从驼峰命名转换为蛇形命名）
            # 内存中存储的是驼峰命名，直接转换为蛇形命名
            system_db_data = {
                'dark_mode': system_data.get('darkMode', False),
                'streaming_enabled': system_data.get('streamingEnabled', True),
                'chat_style': system_data.get('chatStyle', 'bubble'),
                'view_mode': system_data.get('viewMode', 'grid'),
                'default_model': system_data.get('defaultModel', ''),
                # 通知相关字段
                'new_message': system_data.get('newMessage', True),
                'sound': system_data.get('sound', False),
                'system': system_data.get('system', True),
                'display_time': system_data.get('displayTime', '5秒'),
                # 向量相关设置（已经是蛇形命名）
                'vector_db_path': system_data.get('vector_db_path', ''),
                'default_top_k': system_data.get('default_top_k', 3),
                'default_score_threshold': system_data.get('default_score_threshold', 0.7)
            }
            # 记录保存的数据，用于调试
            logger.debug(f"保存设置到数据库: {system_db_data}")
            setting_repo.create_or_update_system_setting(system_db_data)
        

        
        logger.info("设置数据已保存到SQLite数据库")
        return True
    except Exception as e:
        logger.error(f"保存设置数据到SQLite失败: {str(e)}")
        # 回滚事务
        try:
            db_session.rollback()
        except:
            pass
        return False

# --------------------------
# 7. 数据管理接口
# --------------------------
def load_data():
    """加载数据"""
    user_data_dir = ensure_data_dir()  # 先确保目录存在
    
    # 检查数据库文件是否存在
    db_path = os.path.join(user_data_dir, 'config', 'chato.db')
    db_file_exists = os.path.exists(db_path)
    
    try:
        # 初始化数据库
        init_db()
        
        # 如果数据库文件不存在（初次运行），插入默认数据
        if not db_file_exists:
            logger.info("首次运行，插入默认数据...")
            # 插入默认模型数据
            insert_default_models()
            # 插入默认嵌入模型数据
            insert_default_embedding_models()
        else:
            logger.info("数据库文件已存在，使用按需加载模式...")
        
        # 启动自动保存功能
        start_auto_save()
        
        logger.info("必要数据初始化成功")
    except Exception as e:
        logger.error(f"初始化数据时出错: {str(e)}") 

def sync_cache_to_db(key: str, sync_func) -> bool:
    """同步缓存到数据库
    
    Args:
        key: 缓存键
        sync_func: 同步函数，负责将缓存数据写入数据库
        
    Returns:
        bool: 同步是否成功
    """
    if not cache_repo.is_dirty(key):
        return True
    
    try:
        # 执行同步函数
        success = sync_func()
        if success:
            cache_repo.clear_dirty_flag(key)
        return success
    except Exception as e:
        # 记录错误
        logger.error(f"同步缓存到数据库失败: {e}")
        return False


def batch_sync(sync_tasks: list) -> dict:
    """批量同步缓存到数据库
    
    Args:
        sync_tasks: 同步任务列表，每个任务包含 'key' 和 'sync_func'
        
    Returns:
        dict: 每个任务的同步结果
    """
    results = {}
    for task in sync_tasks:
        key = task.get('key')
        sync_func = task.get('sync_func')
        if key and sync_func:
            results[key] = sync_cache_to_db(key, sync_func)
    return results


def save_data():
    """保存数据到SQLite数据库，只保存有脏标记的数据"""
    try:
        # 记录需要保存的数据类型
        saved_types = []
        
        # 只保存有脏标记的数据
        sync_tasks = []
        
        # 检查是否有脏对话
        dirty_chat_ids = cache_repo.get_dirty_chats()
        if dirty_chat_ids:
            sync_tasks.append({'key': 'chats', 'sync_func': save_chats_to_db})
        
        if cache_repo.is_dirty('models'):
            sync_tasks.append({'key': 'models', 'sync_func': save_models_to_db})
        
        if cache_repo.is_dirty('embedding_models'):
            sync_tasks.append({'key': 'embedding_models', 'sync_func': save_embedding_models_to_db})
        
        if cache_repo.is_dirty('settings'):
            sync_tasks.append({'key': 'settings', 'sync_func': save_settings_to_db})
        
        # 执行同步任务
        results = batch_sync(sync_tasks)
        
        # 收集成功保存的数据类型
        for key, success in results.items():
            if success:
                saved_types.append(key)
        
        if saved_types:
            logger.info(f"数据已保存到SQLite: {', '.join(saved_types)}")
        else:
            logger.info("没有数据需要保存")
            
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")

# 向后兼容的脏标记设置函数
def set_dirty_flag(data_type, is_dirty=True):
    """设置数据脏标记
    
    参数:
        data_type: 数据类型，可选值: 'chats', 'models', 'settings'
        is_dirty: 是否为脏数据，默认为True
    """
    cache_repo.set_dirty_flag(data_type, is_dirty)


def get_data(data_type, key=None):
    """
    统一数据访问接口，实现按需加载
    - 先检查内存缓存
    - 如果缓存不存在或为空，从数据库加载并缓存
    - 返回数据
    
    Args:
        data_type: 数据类型，可选值: 'chats', 'models', 'embedding_models', 'settings'
        key: 可选，数据键名，例如对话ID
        
    Returns:
        数据对象，如果不存在返回None
    """
    # 检查内存缓存
    if key:
        if data_type == 'chats':
            data = cache_repo.get_chat(key)
        else:
            # 对于其他数据类型，key参数暂不支持
            data = None
    else:
        data = cache_repo.get(data_type)
    
    # 检查缓存是否存在且非空
    cache_empty = False
    if data_type == 'chats':
        cache_empty = not data if key else len(data or {}) == 0
    elif data_type in ['models', 'embedding_models']:
        cache_empty = len(data or []) == 0
    elif data_type == 'settings':
        cache_empty = len(data or {}) == 0
    
    # 如果缓存不存在或为空，从数据库加载
    if cache_empty:
        if data_type == 'chats':
            if key:
                # 加载单个对话
                load_chats_from_db()
                data = cache_repo.get_chat(key)
            else:
                # 加载所有对话
                load_chats_from_db()
                data = cache_repo.get('chats')
        elif data_type == 'models':
            load_models_from_db()
            data = cache_repo.get('models')
        elif data_type == 'embedding_models':
            load_embedding_models_from_db()
            data = cache_repo.get('embedding_models')
        elif data_type == 'settings':
            load_settings_from_db()
            data = cache_repo.get('settings')
    
    return data