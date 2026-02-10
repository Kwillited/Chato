"""MCP工具相关API路由"""
from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Any
import os
import json
from app.services.mcp.mcp_service import MCPService
from app.dependencies import get_mcp_service
from app.core.logging_config import logger

# 创建MCP API路由（前缀统一为 /api/mcp）
router = APIRouter(prefix='/api/mcp')

# 获取MCP工具列表
@router.get('/tools', response_model=List[Dict[str, Any]])
def get_mcp_tools(mcp_service: MCPService = Depends(get_mcp_service)):
    return mcp_service.get_mcp_tools()

# 获取MCP服务器列表
@router.get('/servers', response_model=List[Dict[str, Any]])
def get_mcp_servers(mcp_service: MCPService = Depends(get_mcp_service)):
    return mcp_service.get_mcp_servers()

# 获取MCP配置文件
@router.get('/config', response_model=Dict[str, Any])
def get_mcp_config():
    # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mcp_config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            # 返回默认配置
            return {
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"]
                },
                "freesearch": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["freesearch-mcpserver@latest"]
                }
            }
    except Exception as e:
        logger.error(f"获取MCP配置失败: {str(e)}")
        raise Exception(f"获取MCP配置失败: {str(e)}")

# 保存MCP配置文件
@router.post('/config', response_model=Dict[str, str])
def save_mcp_config(config: dict = Body(...)):
    # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mcp_config.json')
    
    try:
        # 确保配置目录存在
        config_dir = os.path.dirname(config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"MCP配置已保存到文件: {config_path}")
        
        return {
            'message': 'MCP配置已保存',
            'path': config_path
        }
    except Exception as e:
        logger.error(f"保存MCP配置失败: {str(e)}")
        raise Exception(f"保存MCP配置失败: {str(e)}")
