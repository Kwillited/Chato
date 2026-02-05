"""MCP 数据访问层 - 处理 MCP 相关的数据库操作"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.mcp_models import MCPConfig, MCPTool, MCPServer
import json


class MCPRepository:
    """MCP 仓库类"""
    
    def __init__(self, db: Session = None):
        """初始化 MCP 仓库
        
        Args:
            db: 数据库会话
        """
        self.db = db or next(get_db())
    
    def get_config(self, name: str) -> Optional[MCPConfig]:
        """获取 MCP 配置
        
        Args:
            name: 配置名称
            
        Returns:
            Optional[MCPConfig]: 配置对象
        """
        return self.db.query(MCPConfig).filter(
            MCPConfig.name == name,
            MCPConfig.enabled == True
        ).first()
    
    def get_all_configs(self) -> List[MCPConfig]:
        """获取所有 MCP 配置
        
        Returns:
            List[MCPConfig]: 配置列表
        """
        return self.db.query(MCPConfig).filter(MCPConfig.enabled == True).all()
    
    def create_config(self, name: str, config: Dict[str, Any]) -> MCPConfig:
        """创建 MCP 配置
        
        Args:
            name: 配置名称
            config: 配置内容
            
        Returns:
            MCPConfig: 创建的配置对象
        """
        # 检查是否已存在
        existing = self.get_config(name)
        if existing:
            # 更新现有配置
            existing.config = json.dumps(config)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # 创建新配置
        new_config = MCPConfig(
            name=name,
            config=json.dumps(config)
        )
        self.db.add(new_config)
        self.db.commit()
        self.db.refresh(new_config)
        return new_config
    
    def update_config(self, name: str, config: Dict[str, Any]) -> Optional[MCPConfig]:
        """更新 MCP 配置
        
        Args:
            name: 配置名称
            config: 配置内容
            
        Returns:
            Optional[MCPConfig]: 更新后的配置对象
        """
        existing = self.get_config(name)
        if existing:
            existing.config = json.dumps(config)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return None
    
    def delete_config(self, name: str) -> bool:
        """删除 MCP 配置
        
        Args:
            name: 配置名称
            
        Returns:
            bool: 是否删除成功
        """
        existing = self.get_config(name)
        if existing:
            existing.enabled = False
            self.db.commit()
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取 MCP 工具
        
        Args:
            name: 工具名称
            
        Returns:
            Optional[MCPTool]: 工具对象
        """
        return self.db.query(MCPTool).filter(
            MCPTool.name == name,
            MCPTool.enabled == True
        ).first()
    
    def get_all_tools(self) -> List[MCPTool]:
        """获取所有 MCP 工具
        
        Returns:
            List[MCPTool]: 工具列表
        """
        return self.db.query(MCPTool).filter(MCPTool.enabled == True).all()
    
    def create_tool(self, name: str, description: str, tool_type: str) -> MCPTool:
        """创建 MCP 工具
        
        Args:
            name: 工具名称
            description: 工具描述
            tool_type: 工具类型
            
        Returns:
            MCPTool: 创建的工具对象
        """
        # 检查是否已存在
        existing = self.get_tool(name)
        if existing:
            # 更新现有工具
            existing.description = description
            existing.type = tool_type
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # 创建新工具
        new_tool = MCPTool(
            name=name,
            description=description,
            type=tool_type
        )
        self.db.add(new_tool)
        self.db.commit()
        self.db.refresh(new_tool)
        return new_tool
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """获取 MCP 服务器
        
        Args:
            name: 服务器名称
            
        Returns:
            Optional[MCPServer]: 服务器对象
        """
        return self.db.query(MCPServer).filter(
            MCPServer.name == name,
            MCPServer.enabled == True
        ).first()
    
    def get_all_servers(self) -> List[MCPServer]:
        """获取所有 MCP 服务器
        
        Returns:
            List[MCPServer]: 服务器列表
        """
        return self.db.query(MCPServer).filter(MCPServer.enabled == True).all()
    
    def create_server(self, name: str, description: str, server_type: str, config: Dict[str, Any]) -> MCPServer:
        """创建 MCP 服务器
        
        Args:
            name: 服务器名称
            description: 服务器描述
            server_type: 服务器类型
            config: 服务器配置
            
        Returns:
            MCPServer: 创建的服务器对象
        """
        # 检查是否已存在
        existing = self.get_server(name)
        if existing:
            # 更新现有服务器
            existing.description = description
            existing.type = server_type
            existing.config = json.dumps(config)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # 创建新服务器
        new_server = MCPServer(
            name=name,
            description=description,
            type=server_type,
            config=json.dumps(config)
        )
        self.db.add(new_server)
        self.db.commit()
        self.db.refresh(new_server)
        return new_server
