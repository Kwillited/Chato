"""智能体处理工具类"""


class AgentUtils:
    """智能体处理工具"""
    
    @staticmethod
    def create_agent_session(chat_service, chat_id):
        """创建智能体会话
        
        Args:
            chat_service: 聊天服务实例
            chat_id: 聊天ID
            
        Returns:
            智能体会话ID，如果创建失败则返回None
        """
        agent_session = chat_service.create_agent_session(chat_id, graph_state={}, current_node="")
        return agent_session['id'] if agent_session else None
    
    @staticmethod
    def create_agent_state():
        """创建智能体状态
        
        Returns:
            初始化的智能体状态
        """
        return {
            "messages": [],
            "loop_count": 0,
            "current_node": "",
            "steps": []
        }
    
    @staticmethod
    def update_agent_session(chat_service, session_id, current_node, step_count, graph_state):
        """更新智能体会话状态
        
        Args:
            chat_service: 聊天服务实例
            session_id: 智能体会话ID
            current_node: 当前节点
            step_count: 步骤计数
            graph_state: 图状态
        """
        if session_id:
            chat_service.update_agent_session(
                session_id=session_id,
                current_node=current_node,
                step_count=step_count,
                graph_state=graph_state
            )
    
    @staticmethod
    def process_tool_info(node_tool_info, current_node):
        """处理工具信息，按顺序生成内容
        
        Args:
            node_tool_info: 节点工具信息字典
            current_node: 当前节点
            
        Returns:
            格式化的工具信息内容，如果没有工具信息则返回None
        """
        if current_node in node_tool_info:
            sorted_tools = sorted(node_tool_info[current_node].items(), key=lambda x: x[0])
            if sorted_tools:
                content = ""
                for tool_index, tool_info in sorted_tools:
                    tool_name = tool_info['name']
                    tool_input = tool_info['input']
                    tool_output = tool_info.get('output', None)
                    
                    content += f"\n[工具 {tool_index} 开始] 工具: {tool_name}, 输入: {str(tool_input)}"
                    if tool_output is not None:
                        content += f"\n[工具 {tool_index} 完成] 工具: {tool_name}, 输出: {str(tool_output)}"
                return content
        return None
    
    @staticmethod
    def get_node_content(node_content, node, default_content=""):
        """获取节点内容，如果节点不存在则返回默认内容
        
        Args:
            node_content: 节点内容字典
            node: 节点名称
            default_content: 默认内容
            
        Returns:
            节点内容
        """
        if node == 'reasoning' and (node not in node_content or not node_content[node].strip()):
            return "[推理节点] 生成工具调用计划"
        return node_content.get(node, default_content)
