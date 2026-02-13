"""智能体响应策略"""
import json
from app.utils.response_strategy.strategy.base import BaseResponseStrategyImpl
from app.utils.response_strategy.message_utils import ResponseMessageUtils
from app.utils.response_strategy.agent_utils import AgentUtils
from app.utils.response_strategy.streaming_utils import StreamingUtils


class AgentResponseStrategy(BaseResponseStrategyImpl):
    """智能体响应处理策略（使用 AStream 实现）"""
    
    async def _handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理智能体响应"""
        is_streaming = model_params.get('stream', False)
        
        if is_streaming:
            return await self._handle_streaming_agent_response(
                chat, message_text, user_message, now, model_messages, 
                parsed_model_name, parsed_version_name, model_params, 
                model_display_name, model, chat_service
            )
        else:
            return await self._handle_regular_agent_response(
                chat, message_text, user_message, now, model_messages, 
                parsed_model_name, parsed_version_name, model_params, 
                model_display_name, model, chat_service
            )
    
    async def _handle_streaming_agent_response(self, chat, message_text, user_message, now, 
                                            model_messages, parsed_model_name, 
                                            parsed_version_name, model_params, 
                                            model_display_name, model, chat_service):
        """处理流式智能体响应"""
        async def generate():
            try:
                # 使用工具类创建智能体会话
                agent_session_id = AgentUtils.create_agent_session(chat_service, chat['id'])
                print(f"[AgentResponseStrategy] 创建智能体会话: session_id={agent_session_id}")
                
                # 累积每个节点的响应
                node_content = {}
                node_reasoning = {}  # 存储每个节点的思考内容
                node_metadata = {}
                current_node = None
                current_step = 0
                responses = []
                
                # 使用工具类创建智能体状态
                agent_state = AgentUtils.create_agent_state()
                
                # 工具执行信息存储
                node_tool_info = {}
                
                # 处理流式响应
                print(f"[AgentResponseStrategy] 开始接收智能体流式响应")
                async for chunk in StreamingUtils.handle_streaming_response(
                    chat_service, parsed_model_name, model_messages, 
                    parsed_version_name, model_params, True, model
                ):
                    if isinstance(chunk, dict):
                        print(f"[AgentResponseStrategy] 接收到智能体响应块: event={chunk.get('event')}, node={chunk.get('node')}, step={chunk.get('agent_step')}, tool_index={chunk.get('tool_index')}")
                        # 添加 agent 标记
                        chunk['agent'] = True
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        
                        # 获取节点信息
                        node = chunk.get('node', 'unknown')
                        step = chunk.get('agent_step', 0)  # 使用 agent_step 字段
                        
                        # 更新智能体状态
                        agent_state["current_node"] = node
                        agent_state["loop_count"] = step
                        
                        # 记录步骤信息
                        step_info = {
                            "node": node,
                            "agent_step": step,
                            "event": chunk.get('event'),
                            "timestamp": now
                        }
                        agent_state["steps"].append(step_info)
                        
                        # 当节点变化时，保存前一个节点的响应
                        if current_node and node != current_node:
                            await self._save_agent_node_response(
                                current_node, node_content, node_reasoning, node_metadata,
                                current_step, agent_session_id, now, model_display_name,
                                responses, chat_service, agent_state
                            )
                        
                        # 确保节点内容字典存在
                        if node not in node_content:
                            node_content[node] = ''
                        if node not in node_metadata:
                            node_metadata[node] = {}
                        
                        # 更新当前节点信息
                        current_node = node
                        current_step = step
                        
                        # 更新智能体会话状态
                        AgentUtils.update_agent_session(
                            chat_service, agent_session_id, current_node, current_step, agent_state
                        )
                        
                        # 处理不同类型的事件
                        await self._process_agent_event(
                            chunk, node, step, node_content, node_reasoning, 
                            node_metadata, node_tool_info, agent_state
                        )
                    else:
                        print(f"[AgentResponseStrategy] 接收到非字典响应: {str(chunk)[:50]}...")
                        # 添加 agent 标记
                        yield f"data: {json.dumps({'chunk': str(chunk), 'agent': True}, ensure_ascii=False)}\n\n"
                
                # 保存当前节点的响应
                print(f"[AgentResponseStrategy] 开始保存当前节点的响应")
                if current_node:
                    # 处理工具信息
                    tool_content = AgentUtils.process_tool_info(node_tool_info, current_node)
                    if tool_content:
                        node_content[current_node] = tool_content
                    
                    # 保存当前节点
                    await self._save_agent_node_response(
                        current_node, node_content, node_reasoning, node_metadata,
                        current_step, agent_session_id, now, model_display_name,
                        responses, chat_service, agent_state
                    )
                
                # 保存所有消息
                print(f"[AgentResponseStrategy] 智能体流程完成，开始保存所有消息")
                for ai_message in responses:
                    chat['messages'].append(ai_message)
                chat_service.update_chat_and_save(chat, message_text, user_message, 
                                               responses[-1] if responses else None, now)
                print(f"[AgentResponseStrategy] 所有消息保存完成")
                
                # 发送完成信号
                yield f'data: {json.dumps({"agent": True, "done": True, "saved_messages": responses}, ensure_ascii=False)}\n\n'
            except Exception as e:
                error_msg = f'智能体处理失败: {str(e)}'
                from app.services.base_service import BaseService
                BaseService.log_error(error_msg)
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate
    
    async def _handle_regular_agent_response(self, chat, message_text, user_message, now, 
                                           model_messages, parsed_model_name, 
                                           parsed_version_name, model_params, 
                                           model_display_name, model, chat_service):
        """处理非流式智能体响应"""
        # 使用工具类创建智能体会话
        agent_session_id = AgentUtils.create_agent_session(chat_service, chat['id'])
        print(f"[AgentResponseStrategy] 创建智能体会话: session_id={agent_session_id}")
        
        # 调用智能体
        from app.llm.agent_wrapper import AgentWrapper
        from app.llm.managers.model_manager import ModelManager
        
        # 获取基础模型驱动
        version_config = chat_service.get_version_config(model, parsed_version_name)
        base_driver = ModelManager.get_model_driver(parsed_model_name, model, version_config)
        
        # 创建并初始化智能体
        agent_wrapper = AgentWrapper(base_driver)
        await agent_wrapper.initialize()
        
        # 使用工具类创建智能体状态
        agent_state = AgentUtils.create_agent_state()
        
        # 非流式调用智能体
        print(f"[AgentResponseStrategy] 开始非流式智能体调用")
        response = await agent_wrapper.chat(model_messages, model_params)
        
        # 处理智能体响应
        print(f"[AgentResponseStrategy] 智能体响应完成: {type(response)}")
        
        # 提取内容
        content = response.get('content', response) if isinstance(response, dict) else response
        reasoning_content = response.get('reasoning_content') if isinstance(response, dict) else None
        
        # 创建智能体消息
        ai_message = ResponseMessageUtils.create_agent_message(
            content, now, model_display_name, 
            session_id=agent_session_id, 
            node="final", 
            step=0,
            reasoning_content=reasoning_content
        )
        
        # 保存消息
        print(f"[AgentResponseStrategy] 智能体流程完成，开始保存消息")
        chat['messages'].append(ai_message)
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        print(f"[AgentResponseStrategy] 消息保存完成")
        
        return {
            'success': True,
            'chat': chat
        }, 201
    
    async def _save_agent_node_response(self, node, node_content, node_reasoning, node_metadata, 
                                      step, agent_session_id, now, model_display_name, 
                                      responses, chat_service, agent_state):
        """保存智能体节点响应"""
        # 确保推理节点被保存
        if node == 'reasoning' or (node in node_content and node_content[node].strip()):
            # 使用工具类获取节点内容
            content = AgentUtils.get_node_content(node_content, node)
            
            metadata = node_metadata.get(node, {})
            print(f"[AgentResponseStrategy] 准备节点消息: node={node}, content={content[:50]}...")
            
            # 获取节点的思考内容
            node_reasoning_content = node_reasoning.get(node, None)
            
            # 创建智能体消息
            ai_message = ResponseMessageUtils.create_agent_message(
                content, now, model_display_name, 
                session_id=agent_session_id, 
                node=node, 
                step=step,
                reasoning_content=node_reasoning_content
            )
            
            print(f"[AgentResponseStrategy] 准备智能体消息: message_id={ai_message['id']}, session_id={agent_session_id}, node={node}, step={step}")
            
            responses.append(ai_message)
            print(f"[AgentResponseStrategy] 智能体消息已添加到待保存列表: message_id={ai_message['id']}, node={node}")
            
            # 清空已处理节点的内容
            if node in node_content:
                del node_content[node]
            if node in node_metadata:
                del node_metadata[node]
    
    async def _process_agent_event(self, chunk, node, step, node_content, node_reasoning, 
                                 node_metadata, node_tool_info, agent_state):
        """处理智能体事件"""
        if chunk.get('event') == 'on_chat_model_stream':
            # 处理聊天模型流
            content = chunk.get('data', {}).get('content', '')
            reasoning_content = chunk.get('data', {}).get('reasoning_content', None)
            print(f"[AgentResponseStrategy] 提取到内容: {content[:50]}..., 思考内容: {reasoning_content[:50]}..." if reasoning_content else f"[AgentResponseStrategy] 提取到内容: {content[:50]}...")
            
            # 累积内容
            if content:
                if node not in node_content:
                    node_content[node] = ''
                node_content[node] += content
                print(f"[AgentResponseStrategy] 累积节点内容: node={node}, length={len(node_content[node])}")
                # 更新智能体状态中的消息
                agent_state["messages"].append({
                    "role": "assistant",
                    "content": content,
                    "reasoning_content": reasoning_content,
                    "node": node,
                    "agent_step": step
                })
            # 处理 reasoning_content
            if reasoning_content is not None:
                if node not in node_reasoning:
                    node_reasoning[node] = ''
                node_reasoning[node] += reasoning_content
                print(f"[AgentResponseStrategy] 累积节点思考内容: node={node}, length={len(node_reasoning[node])}")
                # 如果没有 content，也更新智能体状态中的消息
                if not content:
                    agent_state["messages"].append({
                        "role": "assistant",
                        "content": "",
                        "reasoning_content": reasoning_content,
                        "node": node,
                        "agent_step": step
                    })
        elif chunk.get('event') == 'on_tool_call_stream':
            # 处理工具调用计划
            tool_calls = chunk.get('data', {}).get('tool_calls', [])
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    tool_args = tool_call.get('args', {})
                    if node not in node_content:
                        node_content[node] = ''
                    # 添加工具调用计划到节点内容
                    node_content[node] += f"\n[工具调用计划] 工具: {tool_name}, 参数: {str(tool_args)}"
                    print(f"[AgentResponseStrategy] 累积工具调用计划: node={node}, tool={tool_name}")
                    # 更新智能体状态中的消息
                    agent_state["messages"].append({
                        "role": "assistant",
                        "content": f"计划调用工具: {tool_name}",
                        "node": node,
                        "agent_step": step,
                        "tool_name": tool_name,
                        "tool_args": tool_args
                    })
        elif chunk.get('event') == 'on_tool_start':
            # 处理工具开始执行
            tool_name = chunk.get('name', 'unknown')
            tool_index = chunk.get('tool_index', 0)
            tool_input = chunk.get('data', {}).get('input', {})
            
            # 确保节点工具信息存储存在
            if node not in node_tool_info:
                node_tool_info[node] = {}
            
            # 按 tool_index 存储工具开始信息
            node_tool_info[node][tool_index] = {
                'name': tool_name,
                'input': tool_input,
                'status': 'started',
                'output': None
            }
            
            # 累积节点内容
            if node not in node_content:
                node_content[node] = ''
            node_content[node] += f"\n[工具 {tool_index} 开始] 工具: {tool_name}, 输入: {str(tool_input)}"
            
            if node not in node_metadata:
                node_metadata[node] = {}
            if 'tools' not in node_metadata[node]:
                node_metadata[node]['tools'] = {}
            node_metadata[node]['tools'][tool_index] = {'name': tool_name, 'input': tool_input}
            
            # 更新智能体状态中的消息
            agent_state["messages"].append({
                "role": "tool",
                "content": f"开始执行工具: {tool_name}",
                "node": node,
                "agent_step": step,
                "tool_name": tool_name,
                "tool_index": tool_index,
                "tool_input": tool_input
            })
        elif chunk.get('event') == 'on_tool_end':
            # 处理工具执行完成
            tool_name = chunk.get('name', 'unknown')
            tool_index = chunk.get('tool_index', 0)
            tool_output = chunk.get('data', {}).get('output', {})
            
            # 更新工具执行状态
            if node in node_tool_info and tool_index in node_tool_info[node]:
                node_tool_info[node][tool_index]['status'] = 'completed'
                node_tool_info[node][tool_index]['output'] = tool_output
            
            # 累积节点内容
            if node not in node_content:
                node_content[node] = ''
            node_content[node] += f"\n[工具 {tool_index} 完成] 工具: {tool_name}, 输出: {str(tool_output)}"
            
            if node in node_metadata and 'tools' in node_metadata[node] and tool_index in node_metadata[node]['tools']:
                node_metadata[node]['tools'][tool_index]['output'] = tool_output
                node_metadata[node]['tools'][tool_index]['status'] = 'completed'
            
            # 更新智能体状态中的消息
            agent_state["messages"].append({
                "role": "tool",
                "content": f"工具执行完成: {tool_name}",
                "node": node,
                "agent_step": step,
                "tool_name": tool_name,
                "tool_index": tool_index,
                "tool_output": tool_output
            })
    
    def _get_error_message(self, e):
        """获取错误消息"""
        return f'智能体处理失败: {str(e)}'
    
    def _handle_error(self, e):
        """处理错误，返回流式错误响应"""
        async def generate_error():
            yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate_error