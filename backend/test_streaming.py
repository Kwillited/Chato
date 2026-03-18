from langchain_ollama import ChatOllama 
 
# 初始化模型 
llm = ChatOllama( 
    model="qwen2.5:7b", 
    temperature=0.7 
) 

# 使用 astream_events 进行流式输出 
async def stream_response():
    print("=== 开始测试事件流输出 ===")
    async for event in llm.astream_events("用一句话解释什么是人工智能？", version="v1"):
        # 获取事件类型
        event_type = event["event"]
        
        # 打印所有事件类型
                # 直接打印完整的原始事件
        print(event)
        print()

# 运行异步函数 
import asyncio 
if __name__ == "__main__":
    asyncio.run(stream_response())
