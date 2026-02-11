"""智能体响应策略"""
import json
from app.utils.response_strategy.strategy.base import ResponseStrategy
from app.services.base_service import BaseService
from app.utils.message_handler import MessageHandler
from app.utils.response_strategy.agent import AgentProcessor


class AgentResponseStrategy(ResponseStrategy):
    """智能体响应处理策略（使用 AStream 实现）"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        # 检查是否为流式调用
        is_streaming = model_params.get('stream', False)
        
        if is_streaming:
            # 现有的流式处理逻辑
            async def generate():
                try:
                    messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                    
                    # 创建智能体会话
                    agent_session = chat_service.create_agent_session(chat['id'], graph_state={}, current_node="")
                    agent_session_id = agent_session['id'] if agent_session else None
                    print(f"[AgentResponseStrategy] 创建智能体会话: session_id={agent_session_id}")
                    
                    # 累积每个节点的响应
                    node_content = {}
                    node_reasoning = {}  # 新增：存储每个节点的思考内容
                    node_metadata = {}
                    current_node = None
                    current_step = 0
                    responses = []
                    
                    # 智能体状态信息
                    agent_state = {
                        "messages": [],
                        "loop_count": 0,
                        "current_node": "",
                        "steps": []
                    }
                    
                    # 工具执行信息存储，按 tool_index 有序
                    node_tool_info = {}
                    
                    # ！！！关键：使用 async for 遍历异步生成器（AStream 实现）
                    print(f"[AgentResponseStrategy] 开始接收智能体流式响应")
                    async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, model_params, use_agent):
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
                            
                            # 当节点变化时，将前一个节点的响应添加到待保存列表
                            if current_node and node != current_node:
                                # 确保推理节点被保存，即使内容为空
                                if current_node == 'reasoning' or (current_node in node_content and node_content[current_node].strip()):
                                    # 如果推理节点内容为空，生成默认内容
                                    if current_node == 'reasoning' and (current_node not in node_content or not node_content[current_node].strip()):
                                        content = "[推理节点] 生成工具调用计划"
                                    else:
                                        content = node_content.get(current_node, "")
                                    
                                    metadata = node_metadata.get(current_node, {})
                                    print(f"[AgentResponseStrategy] 准备节点消息: node={current_node}, content={content[:50]}...")
                                    # 获取节点的思考内容
                                    node_reasoning_content = node_reasoning.get(current_node, None)
                                    # 使用AgentProcessor格式化智能体消息
                                    ai_message = AgentProcessor.format_agent_message(
                                        content, now, model_display_name, 
                                        session_id=agent_session_id, 
                                        node=current_node, 
                                        step=current_step,
                                        full_reasoning=node_reasoning_content
                                    )
                                    print(f"[AgentResponseStrategy] 准备智能体消息: message_id={ai_message['id']}, session_id={agent_session_id}, node={current_node}, step={current_step}")
                                    
                                    responses.append(ai_message)
                                    print(f"[AgentResponseStrategy] 智能体消息已添加到待保存列表: message_id={ai_message['id']}, node={current_node}")
                                    
                                    # 清空已处理节点的内容
                                    if current_node in node_content:
                                        del node_content[current_node]
                                    if current_node in node_metadata:
                                        del node_metadata[current_node]
                            
                            # 确保节点内容字典存在
                            if node not in node_content:
                                node_content[node] = ''
                            if node not in node_metadata:
                                node_metadata[node] = {}
                            
                            # 更新当前节点信息
                            current_node = node
                            current_step = step  # 使用从事件中获取的 agent_step
                            
                            # 更新智能体会话状态
                            if agent_session_id:
                                print(f"[AgentResponseStrategy] 更新智能体会话状态: session_id={agent_session_id}, node={current_node}, step={current_step}")
                                chat_service.update_agent_session(
                                    session_id=agent_session_id,
                                    current_node=current_node,
                                    step_count=current_step,
                                    graph_state=agent_state
                                )
                            
                            # 累积当前节点的内容
                            if chunk.get('event') == 'on_chat_model_stream':
                                # 修复内容提取逻辑，适配 agent_wrapper.py 的响应格式
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
                                # 存储工具调用计划
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
                                # 存储工具开始执行的信息
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
                                
                                # 累积节点内容（临时，最终会按顺序重新生成）
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
                                # 存储工具执行结果
                                tool_name = chunk.get('name', 'unknown')
                                tool_index = chunk.get('tool_index', 0)
                                tool_output = chunk.get('data', {}).get('output', {})
                                
                                # 更新工具执行状态
                                if node in node_tool_info and tool_index in node_tool_info[node]:
                                    node_tool_info[node][tool_index]['status'] = 'completed'
                                    node_tool_info[node][tool_index]['output'] = tool_output
                                
                                # 累积节点内容（临时，最终会按顺序重新生成）
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
                        else:
                            print(f"[AgentResponseStrategy] 接收到非字典响应: {str(chunk)[:50]}...")
                            # 添加 agent 标记
                            yield f"data: {json.dumps({'chunk': str(chunk), 'agent': True}, ensure_ascii=False)}\n\n"
                    
                    # 保存当前节点的响应
                    print(f"[AgentResponseStrategy] 开始保存当前节点的响应")
                    # 确保推理节点被保存，即使内容为空
                    if current_node and (current_node == 'reasoning' or (current_node in node_content and node_content[current_node].strip())):
                        # 如果推理节点内容为空，生成默认内容
                        if current_node == 'reasoning' and (current_node not in node_content or not node_content[current_node].strip()):
                            content = "[推理节点] 生成工具调用计划"
                        else:
                            content = node_content.get(current_node, "")
                        
                        # 如果有工具执行信息，按顺序添加
                        if current_node in node_tool_info:
                            # 按 tool_index 排序
                            sorted_tools = sorted(node_tool_info[current_node].items(), key=lambda x: x[0])
                            if sorted_tools:
                                # 清空临时内容，重新按顺序生成
                                content = ""
                                for tool_index, tool_info in sorted_tools:
                                    tool_name = tool_info['name']
                                    tool_input = tool_info['input']
                                    tool_output = tool_info.get('output', None)
                                    
                                    # 添加工具开始信息
                                    content += f"\n[工具 {tool_index} 开始] 工具: {tool_name}, 输入: {str(tool_input)}"
                                    
                                    # 添加工具结束信息
                                    if tool_output is not None:
                                        content += f"\n[工具 {tool_index} 完成] 工具: {tool_name}, 输出: {str(tool_output)}"
                        
                        metadata = node_metadata.get(current_node, {})
                        print(f"[AgentResponseStrategy] 准备节点消息: node={current_node}, content={content[:50]}...")
                        # 获取节点的思考内容
                        node_reasoning_content = node_reasoning.get(current_node, None)
                        # 使用AgentProcessor格式化智能体消息
                        ai_message = AgentProcessor.format_agent_message(
                            content, now, model_display_name, 
                            session_id=agent_session_id, 
                            node=current_node, 
                            step=current_step,
                            full_reasoning=node_reasoning_content
                        )
                        print(f"[AgentResponseStrategy] 准备智能体消息: message_id={ai_message['id']}, session_id={agent_session_id}, node={current_node}, step={current_step}")
                        
                        responses.append(ai_message)
                        print(f"[AgentResponseStrategy] 智能体消息已添加到待保存列表: message_id={ai_message['id']}, node={current_node}")
                        
                        # 更新智能体会话状态
                        if agent_session_id:
                            print(f"[AgentResponseStrategy] 更新智能体会话状态: session_id={agent_session_id}, node={current_node}, step={current_step}")
                            chat_service.update_agent_session(
                                session_id=agent_session_id,
                                current_node=current_node,
                                step_count=current_step,
                                graph_state=agent_state
                            )
                    
                    # 模型响应成功，一次性保存所有消息
                    print(f"[AgentResponseStrategy] 智能体流程完成，开始保存所有消息")
                    # 将用户消息添加到对话中
                    chat['messages'].append(user_message)
                    # 保存所有AI消息
                    for ai_message in responses:
                        chat['messages'].append(ai_message)
                    # 一次性保存整个对话
                    chat_service.update_chat_and_save(chat, message_text, user_message, responses[-1] if responses else None, now)
                    print(f"[AgentResponseStrategy] 所有消息保存完成")
                    
                    # 发送完成信号
                    yield f'data: {json.dumps({"agent": True, "done": True, "saved_messages": responses}, ensure_ascii=False)}\n\n'
                except Exception as e:
                    BaseService.log_error(f'智能体处理失败: {str(e)}')
                    # 模型调用失败，不保存任何消息
                    yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
            return generate
        else:
            # 新增的非流式处理逻辑
            try:
                # 创建智能体会话
                agent_session = chat_service.create_agent_session(chat['id'], graph_state={}, current_node="")
                agent_session_id = agent_session['id'] if agent_session else None
                print(f"[AgentResponseStrategy] 创建智能体会话: session_id={agent_session_id}")
                
                # 准备消息
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                
                # 调用智能体（非流式）
                from app.llm.agent_wrapper import AgentWrapper
                from app.llm.managers.model_manager import ModelManager
                
                # 获取基础模型驱动
                model = chat_service.validate_model(parsed_model_name)[0]
                version_config = chat_service.get_version_config(model, parsed_version_name)
                base_driver = ModelManager.get_model_driver(parsed_model_name, model, version_config)
                
                # 创建并初始化智能体
                agent_wrapper = AgentWrapper(base_driver)
                await agent_wrapper.initialize()
                
                # 智能体状态信息
                agent_state = {
                    "messages": [],
                    "loop_count": 0,
                    "current_node": "",
                    "steps": []
                }
                
                # 非流式调用智能体
                print(f"[AgentResponseStrategy] 开始非流式智能体调用")
                response = await agent_wrapper.chat(messages, model_params)
                
                # 处理智能体响应
                print(f"[AgentResponseStrategy] 智能体响应完成: {type(response)}")
                
                # 准备智能体消息
                ai_message = AgentProcessor.format_agent_message(
                    response, now, model_display_name, 
                    session_id=agent_session_id, 
                    node="final", 
                    step=0
                )
                
                # 保存消息
                print(f"[AgentResponseStrategy] 智能体流程完成，开始保存消息")
                # 将用户消息添加到对话中
                chat['messages'].append(user_message)
                # 保存AI消息
                chat['messages'].append(ai_message)
                # 一次性保存整个对话
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                print(f"[AgentResponseStrategy] 消息保存完成")
                
                return {
                    'success': True,
                    'chat': chat
                }, 201
            except Exception as e:
                BaseService.log_error(f'智能体处理失败: {str(e)}')
                return {'error': f'智能体处理失败: {str(e)}'}, 500