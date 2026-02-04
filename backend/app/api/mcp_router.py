"""MCP工具相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入服务类
from app.services.settings.setting_service import SettingService
from app.services.mcp.mcp_service import MCPService
from app.utils.decorators import handle_exception
from app.dependencies import get_setting_service
from app.models.pydantic_models import MCPSettings

# 创建MCP API路由（前缀统一为 /api/mcp）
router = APIRouter(prefix='/api/mcp')

# 获取MCP设置
@router.get('')
@handle_exception
def get_mcp_settings(setting_service: SettingService = Depends(get_setting_service)):
    return setting_service.get_mcp_settings()

# 保存MCP设置
@router.post('')
@handle_exception
def save_mcp_settings(mcp_settings: MCPSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    settings = setting_service.save_mcp_settings(mcp_settings.model_dump())
    return {
        'message': 'MCP设置已保存',
        'settings': settings
    }

# 获取MCP工具列表
@router.get('/tools')
@handle_exception
def get_mcp_tools():
    mcp_service = MCPService()
    return mcp_service.get_mcp_tools()

# 获取MCP服务器列表
@router.get('/servers')
@handle_exception
def get_mcp_servers():
    mcp_service = MCPService()
    return mcp_service.get_mcp_servers()

# 获取MCP配置文件
@router.get('/config')
@handle_exception
def get_mcp_config():
    import json
    import os
    from app.core.logging_config import logger
    
    # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mcp_config.json')
    
    try:
        # 读取配置文件
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            # 如果配置文件不存在，返回空对象
            return {}
    except Exception as e:
        logger.error(f"获取MCP配置失败: {str(e)}")
        raise Exception(f"获取MCP配置失败: {str(e)}")

# 保存MCP配置文件
@router.post('/config')
@handle_exception
def save_mcp_config(config: dict = Body(...)):
    import json
    import os
    from app.core.logging_config import logger
    
    # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mcp_config.json')
    
    try:
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"MCP配置已保存到文件: {config_path}")
        
        return {
            'message': 'MCP配置已保存',
            'config': config
        }
    except Exception as e:
        logger.error(f"保存MCP配置失败: {str(e)}")
        raise Exception(f"保存MCP配置失败: {str(e)}")

