import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncIterator

from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage, 
    ToolMessage
)
from app.models.base_model import BaseModel
from app.utils.stream_utils import StreamUtils
from app.utils.mcp.mcp_adapter import mcp_adapter
from app.core.logging_config import logger

class AgentWrapper:
    def __init__(self, base_model: BaseModel):
        if not hasattr(base_model, 'llm'):
            raise ValueError("base_model 必须有 'llm' 属性")
        self.base_model = base_model
        self.llm = base_model.llm
        self.llm_with_tools = None
        self.is_initialized = False
        logger.info(f"✅ AgentWrapper 初始化完成: {type(self.base_model).__name__}")

    async def initialize(self, mcp_config: Optional[Dict] = None):
        if self.is_initialized:
            return
        
        logger.info("🔄 [初始化] 开始智能体工具绑定")
        await mcp_adapter.initialize(mcp_config)
        tools = mcp_adapter.get_tools()
        
        if tools:
            try:
                # 绑定工具到 LLM
                self.llm_with_tools = self.llm.bind_tools(tools)
                logger.info(f"✅ [初始化] 成功绑定 {len(tools)} 个工具")
            except Exception as e:
                logger.error(f"❌ [初始化] 工具绑定失败: {str(e)}")
                self.llm_with_tools = self.llm
        else:
            self.llm_with_tools = self.llm
        
        self.is_initialized = True

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float, use_agent: bool = True) -> AsyncIterator[str]:
        if not use_agent:
            async for chunk in self.base_model.chat_stream(messages, temperature):
                yield chunk
            return

        if not self.is_initialized:
            await self.initialize()

        logger.info("🌊 [Stream] 进入智能体执行流程")
        
        try:
            # 1. 准备初始消息
            input_messages = self._prepare_messages(messages)
            
            # 2. 第一次调用：判断是否需要工具
            logger.info("🤖 [Step 1] 正在请求模型进行决策...")
            # 注意：这里使用 ainvoke 获取完整决策
            ai_msg = await self.llm_with_tools.ainvoke(input_messages)
            
            # 检查是否有工具调用
            tool_calls = getattr(ai_msg, 'tool_calls', [])
            
            if not tool_calls:
                logger.info("📝 [Step 1] 模型决定直接回答，无需工具")
                if ai_msg.content:
                    yield StreamUtils.format_stream_chunk(ai_msg.content, agent=True)
                yield StreamUtils.format_stream_done(agent=True)
                return

            # 3. 执行工具调用逻辑
            logger.info(f"🛠️ [Step 2] 模型请求调用工具: {[tc['name'] for tc in tool_calls]}")
            
            # 将模型的工具调用意图放入消息历史
            input_messages.append(ai_msg)
            
            for tool_call in tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                tool_id = tool_call.get('id')

                yield StreamUtils.format_stream_chunk(f"\n> 🛠️ **正在执行工具: {tool_name}** (参数: {json.dumps(tool_args, ensure_ascii=False)})\n", agent=True)
                
                try:
                    logger.info(f"🔧 正在执行: {tool_name}, 参数: {tool_args}")
                    # 从适配器获取工具实例
                    tools_map = {tool.name: tool for tool in mcp_adapter.get_tools()}
                    
                    if tool_name in tools_map:
                        tool_instance = tools_map[tool_name]
                        # 执行工具
                        result = await tool_instance.ainvoke(tool_args)
                        result_str = str(result)
                        logger.info(f"✨ 工具执行成功，结果长度: {len(result_str)}")
                        
                        yield StreamUtils.format_stream_chunk(f"\n> ✅ **执行成功**\n\n", agent=True)
                        
                        # 重要：将工具结果封装为 ToolMessage 放入历史
                        input_messages.append(ToolMessage(content=result_str, tool_call_id=tool_id))
                    else:
                        error_msg = f"未找到工具: {tool_name}"
                        logger.error(f"❌ {error_msg}")
                        input_messages.append(ToolMessage(content=error_msg, tool_call_id=tool_id))
                        yield StreamUtils.format_stream_chunk(f"\n> ❌ **错误: {error_msg}**\n\n", agent=True)

                except Exception as e:
                    error_msg = f"工具执行异常: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    input_messages.append(ToolMessage(content=error_msg, tool_call_id=tool_id))
                    yield StreamUtils.format_stream_chunk(f"\n> ❌ **工具运行失败**\n\n", agent=True)

            # 4. 第二次调用：根据工具结果生成流式总结
            logger.info("🤖 [Step 3] 正在根据工具结果生成总结...")
            yield StreamUtils.format_stream_chunk("\n> 🔍 **正在分析处理结果...**\n\n", agent=True)

            # 使用 astream 实现流式输出总结，提升用户体验
            async for chunk in self.llm.astream(input_messages):
                if chunk.content:
                    yield StreamUtils.format_stream_chunk(chunk.content, agent=True)

            yield StreamUtils.format_stream_chunk("\n\n> 🏁 **任务处理完成**\n", agent=True)
            yield StreamUtils.format_stream_done(agent=True)
            logger.info("🏁 [Stream] 智能体响应全流程结束")

        except asyncio.CancelledError:
            logger.warning("⚠️ [Stream] 客户端断开连接，任务取消")
            raise
        except Exception as e:
            logger.error(f"❌ [Stream] 智能体模式崩溃: {str(e)}", exc_info=True)
            yield StreamUtils.format_stream_chunk(f"\n\n⚠️ 处理出错: {str(e)}，正在切换回普通模式...\n\n", agent=True)
            # 异常回退逻辑
            async for chunk in self.base_model.chat_stream(messages, temperature):
                yield chunk

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将 API 消息转换为 LangChain 消息对象"""
        formatted = []
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'user':
                formatted.append(HumanMessage(content=content))
            elif role == 'assistant':
                formatted.append(AIMessage(content=content))
            elif role == 'system':
                formatted.append(SystemMessage(content=content))
        return formatted

    def __getattr__(self, name):
        return getattr(self.base_model, name)