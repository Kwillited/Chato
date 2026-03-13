"""智能体消息处理模块"""
import json
from app.utils.logging_utils import LoggingUtils
from app.utils.stream import StreamSystem
from app.utils.message.base import MessageSystem


class AgentSystem:
    """智能体处理系统，包含智能体响应处理和会话管理功能"""
    
    # 智能体响应处理相关方法
    @staticmethod
    def process_agent_stream_chunk(chunk, full_reply):
        """处理智能体事件流响应块

        Args:
            chunk: 智能体事件流响应块
            full_reply: 当前累积的完整回复

        Returns:
            (formatted_chunk, updated_full_reply): 格式化后的响应块和更新后的完整回复
        """
        try:
            # 检查是否已经是SSE格式
            if isinstance(chunk, str) and chunk.startswith('data: '):
                chunk_str = chunk[6:].strip()
                try:
                    chunk_data = json.loads(chunk_str)
                    # 检查是否是智能体响应
                    if chunk_data.get('agent', False):
                        # 累积完整回复
                        if 'chunk' in chunk_data:
                            full_reply += chunk_data['chunk']
                        elif 'content' in chunk_data:
                            full_reply += chunk_data['content']
                    return chunk, full_reply
                except:
                    # 如果解析失败，直接返回原chunk
                    return chunk, full_reply
            else:
                # 如果不是SSE格式，包装成SSE格式
                try:
                    # 尝试解析chunk，看是否是JSON格式
                    chunk_data = json.loads(chunk)
                    # 添加agent标记
                    chunk_data['agent'] = True
                    # 包装成SSE格式
                    formatted_chunk = StreamSystem.format_stream_chunk(chunk_data.get('chunk', chunk_data.get('content', str(chunk))), agent=True)
                    # 累积完整回复
                    if 'chunk' in chunk_data:
                        full_reply += chunk_data['chunk']
                    elif 'content' in chunk_data:
                        full_reply += chunk_data['content']
                    return formatted_chunk, full_reply
                except:
                    # 如果不是JSON格式，直接作为内容包装
                    formatted_chunk = StreamSystem.format_stream_chunk(chunk, agent=True)
                    full_reply += chunk
                    return formatted_chunk, full_reply
        except Exception as e:
            LoggingUtils.log_error(f"处理智能体事件流响应块失败: {e}")
            # 尝试作为直接内容处理
            full_reply += str(chunk)
            formatted_chunk = StreamSystem.format_stream_chunk(str(chunk), agent=True)
            return formatted_chunk, full_reply
    

    
    # 智能体会话管理相关方法（已简化，不再使用独立的AgentSession表）
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
    
    # 智能体工具和节点相关方法
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
