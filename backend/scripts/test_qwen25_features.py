#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Qwen2.5:7b 模型的功能支持情况
特别是测试 stream 功能和其他参数支持
"""
import asyncio
import json
import sys
import os

# 添加backend目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm.vendors.ollama_model import OllamaModel

async def test_ollama_streaming():
    """测试 Ollama 模型的流式输出功能"""
    print("=== 测试 Qwen2.5:7b 模型功能 ===")
    
    # 配置 Qwen2.5:7b 模型
    model_config = {}
    version_config = {
        'name': 'qwen2.5:7b',
        'base_url': 'http://localhost:11434'
    }
    
    try:
        # 初始化模型
        print("1. 初始化 Ollama 模型...")
        model = OllamaModel(model_config, version_config)
        print("✓ 模型初始化成功")
        
        # 测试消息
        test_messages = [
            {"role": "user", "content": "请简单介绍一下你自己，使用中文回答"}
        ]
        
        # 测试1: 非流式调用
        print("\n2. 测试非流式调用...")
        non_stream_params = {
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        }
        
        response = model.chat(test_messages, non_stream_params)
        print(f"✓ 非流式调用成功")
        print(f"  响应内容: {response['content'][:100]}...")
        
        # 测试2: 流式调用
        print("\n3. 测试流式调用...")
        stream_params = {
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": True
        }
        
        print("  流式输出:")
        full_content = ""
        async for chunk in model.chat_stream(test_messages, stream_params):
            if 'content' in chunk and chunk['content']:
                print(chunk['content'], end="", flush=True)
                full_content += chunk['content']
            elif 'done' in chunk and chunk['done']:
                print("\n✓ 流式调用完成")
            elif 'error' in chunk:
                print(f"\n✗ 流式调用错误: {chunk['error']}")
                break
        
        # 测试3: 测试不同参数组合
        print("\n4. 测试不同参数组合...")
        test_params = [
            {"temperature": 0.1, "max_tokens": 200, "top_p": 0.9},
            {"temperature": 1.0, "max_tokens": 300, "top_k": 50},
            {"temperature": 0.5, "max_tokens": 400, "repeat_penalty": 1.1}
        ]
        
        for i, params in enumerate(test_params, 1):
            print(f"  测试参数组合 {i}: {params}")
            try:
                response = model.chat(test_messages, params)
                print(f"    ✓ 调用成功")
                print(f"    响应长度: {len(response['content'])} 字符")
            except Exception as e:
                print(f"    ✗ 调用失败: {e}")
        
        # 测试4: 测试 deepThinking 功能
        print("\n5. 测试 deepThinking 功能...")
        thinking_params = {
            "temperature": 0.7,
            "max_tokens": 500,
            "deepThinking": True
        }
        
        response = model.chat(test_messages, thinking_params)
        print(f"✓ deepThinking 调用成功")
        print(f"  响应内容: {response['content'][:100]}...")
        if response.get('reasoning_content'):
            print(f"  推理内容: {response['reasoning_content'][:100]}...")
        else:
            print(f"  未返回推理内容")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama_streaming())
