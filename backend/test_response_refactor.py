"""测试重构后的响应模块"""

# 测试导入重构后的响应模块
print("开始测试重构后的响应模块...")

try:
    # 先导入基础策略类
    from app.utils.response.strategy.base import ResponseStrategy
    print("✓ 成功导入 ResponseStrategy")
    
    # 测试导入策略类
    from app.utils.response.strategy.regular import RegularResponseStrategy
    print("✓ 成功导入 RegularResponseStrategy")
    
    from app.utils.response.strategy.streaming import StreamingResponseStrategy
    print("✓ 成功导入 StreamingResponseStrategy")
    
    from app.utils.response.strategy.agent import AgentResponseStrategy
    print("✓ 成功导入 AgentResponseStrategy")
    
    # 最后导入 ResponseHandler
    from app.utils.response.handler import ResponseHandler
    print("✓ 成功导入 ResponseHandler")
    
    # 测试策略类初始化
    regular_strategy = RegularResponseStrategy()
    print("✓ 成功初始化 RegularResponseStrategy")
    
    streaming_strategy = StreamingResponseStrategy()
    print("✓ 成功初始化 StreamingResponseStrategy")
    
    agent_strategy = AgentResponseStrategy()
    print("✓ 成功初始化 AgentResponseStrategy")
    
    print("\n所有模块导入和初始化成功！重构后的响应模块工作正常。")
    print("\n重构完成后的对话模式分类：")
    print("1. 普通对话：非流式、非智能体 → 使用 RegularResponseStrategy")
    print("2. 流式对话：流式、非智能体 → 使用 StreamingResponseStrategy (AStream 实现)")
    print("3. 智能体对话（非流式）：非流式、智能体 → 使用 RegularResponseStrategy")
    print("4. 智能体对话（流式）：流式、智能体 → 使用 AgentResponseStrategy (AStream 实现)")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
