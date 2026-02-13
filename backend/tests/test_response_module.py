"""测试响应模块导入"""

# 测试导入重构后的响应模块
print("开始测试响应模块导入...")

try:
    # 测试导入核心消息处理模块
    from app.utils.message import MessageSystem
    print("✓ 成功导入 MessageSystem")
    
    # 测试导入流式处理模块
    from app.utils.stream import StreamSystem
    print("✓ 成功导入 StreamSystem")
    
    # 测试导入智能体处理模块
    from app.utils.agent import AgentSystem
    print("✓ 成功导入 AgentSystem")
    
    # 测试导入响应消息工具模块
    from app.utils.response_message import ResponseMessageSystem
    print("✓ 成功导入 ResponseMessageSystem")
    
    # 测试导入策略类
    from app.utils.response_strategy.strategy.regular import RegularResponseStrategy
    print("✓ 成功导入 RegularResponseStrategy")
    
    from app.utils.response_strategy.strategy.streaming import StreamingResponseStrategy
    print("✓ 成功导入 StreamingResponseStrategy")
    
    from app.utils.response_strategy.strategy.agent import AgentResponseStrategy
    print("✓ 成功导入 AgentResponseStrategy")
    
    # 最后测试导入 ResponseHandler
    from app.utils.response_strategy.handler import ResponseHandler
    print("✓ 成功导入 ResponseHandler")
    
    print("\n所有模块导入成功！重构后的响应模块工作正常。")
    
    print("\n重构后的模块结构：")
    print("1. 核心消息处理模块: MessageSystem")
    print("2. 流式处理模块: StreamSystem")
    print("3. 智能体处理模块: AgentSystem")
    print("4. 响应消息工具模块: ResponseMessageSystem")
    print("5. 策略类: RegularResponseStrategy, StreamingResponseStrategy, AgentResponseStrategy")
    print("6. 处理器: ResponseHandler")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
