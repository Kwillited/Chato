import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncIterator

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
)
from app.models.base_model import BaseModel
from app.utils.mcp.mcp_adapter import mcp_adapter
from app.core.logging_config import logger

class AgentWrapper:
    def __init__(self, base_model: BaseModel):
        self.base_model = base_model
        self.llm = base_model.llm
        self.llm_with_tools = None
        self.is_initialized = False

    async def initialize(self, mcp_config: Optional[Dict] = None):
        if self.is_initialized: return
        await mcp_adapter.initialize(mcp_config)
        tools = mcp_adapter.get_tools()
        if tools:
            self.llm_with_tools = self.llm.bind_tools(tools)
        self.is_initialized = True

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float, use_agent: bool = True) -> AsyncIterator[Dict[str, Any]]:
        if not self.is_initialized:
            await self.initialize()

        input_messages = self._prepare_messages(messages)
        
        try:
            # --- 🚀 关键改进：立即发送一个心跳，防止浏览器超时 ---
            yield {"event": "on_chat_model_stream", "data": {"chunk": {"content": "> 🧠 **正在思考...**\n"}}}

            # --- [Step 1] 决策 ---
            print("[Agent] Step 1: 分析中...")
            ai_msg = await asyncio.wait_for(self.llm_with_tools.ainvoke(input_messages), timeout=60.0)
            
            # 发送心跳：告诉前端我还在
            yield {"event": "on_chat_model_stream", "data": {"chunk": {"content": "> 🔍 **正在检索资料...**\n"}}}

            tool_calls = getattr(ai_msg, 'tool_calls', [])
            
            # --- [Step 2] 工具执行 ---
            if tool_calls:
                input_messages.append(ai_msg)
                tools_map = {t.name: t for t in mcp_adapter.get_tools()}

                for tc in tool_calls:
                    t_name, t_args, t_id = tc['name'], tc['args'], tc['id']
                    print(f"[Agent] Step 2: 执行工具 {t_name}")
                    
                    # 再次发送心跳
                    yield {"event": "on_chat_model_stream", "data": {"chunk": {"content": f"> 🛠️ **正在调用工具 `{t_name}`...**\n"}}}
                    
                    try:
                        if t_name in tools_map:
                            result = await asyncio.wait_for(tools_map[t_name].ainvoke(t_args), timeout=30.0)
                            res_str = str(result)
                            input_messages.append(ToolMessage(content=res_str, tool_call_id=t_id))
                        else:
                            input_messages.append(ToolMessage(content=f"Error: {t_name} not found", tool_call_id=t_id))
                    except Exception as e:
                        input_messages.append(ToolMessage(content=f"Error: {str(e)}", tool_call_id=t_id))

            # --- [Step 3] 总结 ---
            print("[Agent] Step 3: 开始吐流...")
            # 发送最后一次心跳清理行
            yield {"event": "on_chat_model_stream", "data": {"chunk": {"content": "\n"}}}
            
            # 使用最稳健的 astream
            async for chunk in self.llm.astream(input_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    # 强转为字符串，确保 JSON 序列化不崩溃
                    yield {
                        "event": "on_chat_model_stream",
                        "data": {"chunk": {"content": str(chunk.content)}}
                    }

            yield {"event": "on_chat_model_end", "data": {}}

        except (GeneratorExit, asyncio.CancelledError):
            print("[Agent] 通讯管道关闭，清理资源")
            raise
        except Exception as e:
            print(f"[Agent] 异常: {str(e)}")
            yield {"event": "error", "content": str(e)}

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        formatted = []
        for msg in messages:
            role, content = msg.get('role', 'user'), msg.get('content', '')
            if role == 'user': formatted.append(HumanMessage(content=content))
            elif role == 'assistant': formatted.append(AIMessage(content=content))
            elif role == 'system': formatted.append(SystemMessage(content=content))
        return formatted

    def __getattr__(self, name):
        return getattr(self.base_model, name)