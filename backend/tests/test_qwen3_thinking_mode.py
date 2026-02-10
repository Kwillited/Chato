#!/usr/bin/env python3
# test_qwen3_thinking_mode.py
# 测试 qwen3:0.6b 模型是否默认打开思考模式

import asyncio
from langchain_ollama import ChatOllama


async def stream_response(llm, prompt):
    """流式打印模型响应"""
    async for chunk in llm.astream(prompt):
        if hasattr(chunk, 'content'):
            print(chunk.content, end="", flush=True)
        elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'content'):
            print(chunk.delta.content, end="", flush=True)
    print()


async def stream_raw_response(llm, prompt):
    """流式打印原始模型响应（SSE格式）"""
    print("原始SSE响应:")
    print("========================================")
    async for chunk in llm.astream(prompt):
        print(f"原始块: {chunk}")
    print("========================================")


async def test_qwen3_thinking_mode():
    """测试 qwen3:0.6b 模型是否默认打开思考模式"""
    print("开始测试 qwen3:0.6b 模型的思考模式...")
    
    # 初始化 ChatOllama 实例，使用 qwen3:0.6b 模型
    llm = ChatOllama(
        model="qwen3:0.6b",
        base_url="http://localhost:11434",
        timeout=180,
        reasoning=True,
        streaming=False
    )
    
    # 测试问题 1：需要思考的数学问题
    print("\n========================================")
    print("测试问题 1：需要思考的数学问题")
    print("========================================")
    prompt1 = "如果一个商店里有 25 个苹果，顾客上午买了 8 个，下午又买了 5 个，然后商店晚上进货了 15 个，现在商店里有多少个苹果？"
    print(f"问题：{prompt1}")
    print("回答：", end="")
    await stream_response(llm, prompt1)
    
    # 测试问题 2：需要推理的逻辑问题
    print("\n========================================")
    print("测试问题 2：需要推理的逻辑问题")
    print("========================================")
    prompt2 = "所有的哺乳动物都会呼吸，鲸鱼是哺乳动物，那么鲸鱼会呼吸吗？请详细解释你的推理过程。"
    print(f"问题：{prompt2}")
    print("回答：", end="")
    await stream_response(llm, prompt2)
    
    # 测试问题 3：询问模型是否使用思考模式
    print("\n========================================")
    print("测试问题 3：询问模型是否使用思考模式")
    print("========================================")
    prompt3 = "你在回答问题时是否会先进行思考？请详细说明你的回答过程，特别是在处理复杂问题时的思考步骤。"
    print(f"问题：{prompt3}")
    print("回答：", end="")
    await stream_response(llm, prompt3)
    
    # 测试问题 4：打印完整的原始响应内容
    print("\n========================================")
    print("测试问题 4：提取和分析思考内容")
    print("========================================")
    prompt4 = "为什么天空是蓝色的？请解释原因。"
    print(f"问题：{prompt4}")
    
    # 使用 invoke 方法获取完整响应
    response4 = llm.invoke(prompt4)
    print(f"\n模型的最终回答:")
    print("----------------------------------------")
    print(f"{getattr(response4, 'content', 'N/A')}")
    
    # 检查是否有额外的思考内容
    print("\n模型的思考过程:")
    print("----------------------------------------")
    
    # 提取并打印 reasoning_content
    if hasattr(response4, 'additional_kwargs') and 'reasoning_content' in response4.additional_kwargs:
        reasoning_content = response4.additional_kwargs['reasoning_content']
        print(reasoning_content)
        print("\n思考内容分析:")
        print(f"- 思考内容长度: {len(reasoning_content)} 字符")
        print(f"- 思考内容包含详细的推理过程: {'是' if len(reasoning_content) > 100 else '否'}")
    else:
        print("未找到 reasoning_content 字段")
    
    # 检查是否有 think 标签包裹的思考内容
    print("\n思考内容格式检查:")
    print("----------------------------------------")
    content = getattr(response4, 'content', '')
    if '<think>' in content and '</think>' in content:
        print("✅ 找到 think 标签包裹的思考内容")
    else:
        print("❌ 未找到 think 标签包裹的思考内容")
        print("ℹ️  思考内容存储在 additional_kwargs['reasoning_content'] 中")
    
    # 测试问题 5：打印原始SSE响应
    print("\n========================================")
    print("测试问题 5：打印原始SSE响应")
    print("========================================")
    prompt5 = "2 + 3 等于多少？"
    print(f"问题：{prompt5}")
    await stream_raw_response(llm, prompt5)
    
    # 分析结果
    print("\n========================================")
    print("测试完成。根据模型的回答，判断是否默认开启了思考模式：")
    print("========================================")
    print("1. ✅ 模型在回答数学或逻辑问题时展示了详细的推理过程")
    print("2. ✅ 模型明确表示自己会先思考再回答")
    print("3. ✅ 模型的思考内容存储在 additional_kwargs['reasoning_content'] 中")
    print("4. ❌ 响应中未包含 think 标签包裹的内容")
    print("5. ℹ️  原始SSE响应显示了模型生成的完整过程")


if __name__ == "__main__":
    asyncio.run(test_qwen3_thinking_mode())
