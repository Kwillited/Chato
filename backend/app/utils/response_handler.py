"""响应处理器工具类"""
import json
import asyncio
from typing import Dict, Any, Generator, Callable

from app.utils.response_formatter import ResponseFormatter
from app.services.base_service import BaseService


class ResponseStrategy:
    """响应处理策略接口"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        """处理响应 - 改为异步"""
        raise NotImplementedError


class RegularResponseStrategy(ResponseStrategy):
    """普通非流式响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        """处理普通响应"""
        try:
            # 验证模型
            model, error_response, error_code = chat_service.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
            temperature = model_params.get('temperature', 0.7)
            version_config = chat_service.get_version_config(model, parsed_version_name)

            chat_service.log_info("使用普通对话模式")
            
            from app.models.model_manager import ModelManager
            # 即使是非流式调用，在异步链中也建议封装为异步执行
            response = ModelManager.chat(parsed_model_name, model, version_config, messages, temperature)
        
            if isinstance(response, dict) and 'content' in response:
                ai_reply = response['content']
            else:
                ai_reply = response
        except Exception as e:
            BaseService.log_error(f'调用模型失败: {str(e)}')
            return {'error': f'调用模型失败: {str(e)}'}, 500

        ai_message = ResponseFormatter.process_full_reply(ai_reply, now, model_display_name)
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat,
            'user_message': user_message,
            'ai_message': ai_message
        }, 201


class StreamingResponseStrategy(ResponseStrategy):
    """标准流式响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        # 必须定义为异步生成器
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                full_reply = ""
                
                # ！！！关键：改用 async for 遍历异步生成器
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    formatted_chunk, full_reply = ResponseFormatter.process_streaming_chunk(chunk, full_reply)
                    yield formatted_chunk
                
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                final_data = {'done': True, 'chat': chat, 'ai_message': ai_message}
                yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                BaseService.log_error(f'流式处理失败: {str(e)}')
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AgentResponseStrategy(ResponseStrategy):
    """智能体响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                
                # 创建智能体会话
                agent_session = chat_service.create_agent_session(chat['id'], graph_state={}, current_node="")
                agent_session_id = agent_session['id'] if agent_session else None
                print(f"[AgentResponseStrategy] 创建智能体会话: session_id={agent_session_id}")
                
                # 累积每个节点的响应
                node_content = {}
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
                
                # ！！！关键：改用 async for
                print(f"[AgentResponseStrategy] 开始接收智能体流式响应")
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, dict):
                        print(f"[AgentResponseStrategy] 接收到智能体响应块: event={chunk.get('event')}, node={chunk.get('node')}, step={chunk.get('agent_step')}, tool_index={chunk.get('tool_index')}")
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
                        
                        # 当节点变化时保存前一个节点的消息
                        if current_node and node != current_node:
                            # 确保推理节点被保存，即使内容为空
                            if current_node == 'reasoning' or (current_node in node_content and node_content[current_node].strip()):
                                # 如果推理节点内容为空，生成默认内容
                                if current_node == 'reasoning' and (current_node not in node_content or not node_content[current_node].strip()):
                                    content = "[推理节点] 生成工具调用计划"
                                else:
                                    content = node_content.get(current_node, "")
                                
                                metadata = node_metadata.get(current_node, {})
                                print(f"[AgentResponseStrategy] 保存节点消息: node={current_node}, content={content[:50]}...")
                                ai_message = ResponseFormatter.process_full_reply(content, now, model_display_name)
                                # 添加智能体消息相关字段
                                ai_message['message_type'] = 'agent'
                                ai_message['agent_session_id'] = agent_session_id
                                ai_message['agent_node'] = current_node
                                ai_message['agent_step'] = current_step
                                ai_message['agent_metadata'] = json.dumps(metadata)
                                print(f"[AgentResponseStrategy] 准备保存智能体消息: message_id={ai_message['id']}, session_id={agent_session_id}, node={current_node}, step={current_step}")
                                
                                # 保存消息
                                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                                responses.append(ai_message)
                                print(f"[AgentResponseStrategy] 智能体消息保存完成: message_id={ai_message['id']}, node={current_node}")
                                
                                # 清空已保存节点的内容
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
                            print(f"[AgentResponseStrategy] 提取到内容: {content[:50]}...")
                            if content:
                                if node not in node_content:
                                    node_content[node] = ''
                                node_content[node] += content
                                print(f"[AgentResponseStrategy] 累积节点内容: node={node}, length={len(node_content[node])}")
                                # 更新智能体状态中的消息
                                agent_state["messages"].append({
                                    "role": "assistant",
                                    "content": content,
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
                    print(f"[AgentResponseStrategy] 保存节点消息: node={current_node}, content={content[:50]}...")
                    ai_message = ResponseFormatter.process_full_reply(content, now, model_display_name)
                    # 添加智能体消息相关字段
                    ai_message['message_type'] = 'agent'
                    ai_message['agent_session_id'] = agent_session_id
                    ai_message['agent_node'] = current_node
                    ai_message['agent_step'] = current_step
                    ai_message['agent_metadata'] = json.dumps(metadata)
                    print(f"[AgentResponseStrategy] 准备保存智能体消息: message_id={ai_message['id']}, session_id={agent_session_id}, node={current_node}, step={current_step}")
                    
                    # 保存消息
                    chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                    responses.append(ai_message)
                    print(f"[AgentResponseStrategy] 智能体消息保存完成: message_id={ai_message['id']}, node={current_node}")
                    
                    # 更新智能体会话状态
                    if agent_session_id:
                        print(f"[AgentResponseStrategy] 更新智能体会话状态: session_id={agent_session_id}, node={current_node}, step={current_step}")
                        chat_service.update_agent_session(
                            session_id=agent_session_id,
                            current_node=current_node,
                            step_count=current_step,
                            graph_state=agent_state
                        )
                
                # 发送完成信号
                yield f'data: {json.dumps({"agent": True, "done": True, "saved_messages": responses}, ensure_ascii=False)}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AStreamResponseStrategy(ResponseStrategy):
    """AStream响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                full_reply = ""
                
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, dict):
                        chunk['astream'] = True
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))
                    else:
                        yield f"data: {json.dumps({'chunk': str(chunk), 'astream': True}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                yield f'data: {json.dumps({"astream": True, "done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AStreamEventsResponseStrategy(ResponseStrategy):
    """异步事件流响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            full_reply = ""
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                
                # ！！！关键：async for
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, str) and chunk.startswith('data: '):
                        yield chunk
                    else:
                        if isinstance(chunk, dict):
                            chunk['astream_events'] = True
                        else:
                            chunk = {'chunk': str(chunk), 'astream_events': True}
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))

                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                yield f"data: {json.dumps({'astream_events': True, 'done': True, 'ai_message': ai_message}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        return generate


class ResponseStrategyContext:
    """响应策略上下文"""
    
    def __init__(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        # 必须 await 策略的异步方法
        return await self._strategy.handle_response(chat, message_text, user_message, now, 
                                             enhanced_question, parsed_model_name, 
                                             parsed_version_name, model_params, 
                                             model_display_name, deep_thinking, 
                                             use_agent, chat_service)


class ResponseHandler:
    """响应处理器，处理不同类型的响应"""
    
    @staticmethod
    async def handle_regular_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        strategy = RegularResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, 
                                 model_params, model_display_name, deep_thinking=False, use_agent=False,
                                 chat_service=None):
        if use_agent:
            strategy = AgentResponseStrategy()
        else:
            strategy = StreamingResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_astream_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        if use_agent:
            # 使用 AgentResponseStrategy 处理智能体响应
            strategy = AgentResponseStrategy()
        else:
            strategy = AStreamResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_astream_events_response(chat, message_text, user_message, now,
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking=False, use_agent=False,
                                      chat_service=None):
        if use_agent:
            # 使用 AgentResponseStrategy 处理智能体响应
            strategy = AgentResponseStrategy()
        else:
            strategy = AStreamEventsResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)