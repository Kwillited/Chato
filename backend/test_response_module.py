"""测试响应模块导入"""

# 测试导入重构后的响应模块
print("开始测试响应模块导入...")

try:
    # 测试导入 ResponseFormatter
    from app.utils.response.formatter import ResponseFormatter
    print("✓ 成功导入 ResponseFormatter")
    
    # 测试导入 StreamUtils
    from app.utils.response.stream import StreamUtils
    print("✓ 成功导入 StreamUtils")
    
    # 测试导入 AgentProcessor
    from app.utils.response.agent import AgentProcessor
    print("✓ 成功导入 AgentProcessor")
    
    # 测试导入策略类
    from app.utils.response.strategy.regular import RegularResponseStrategy
    print("✓ 成功导入 RegularResponseStrategy")
    
    from app.utils.response.strategy.streaming import StreamingResponseStrategy
    print("✓ 成功导入 StreamingResponseStrategy")
    
    from app.utils.response.strategy.agent import AgentResponseStrategy
    print("✓ 成功导入 AgentResponseStrategy")
    
    from app.utils.response.strategy.astream import AStreamResponseStrategy, AStreamEventsResponseStrategy
    print("✓ 成功导入 AStreamResponseStrategy 和 AStreamEventsResponseStrategy")
    
    # 最后测试导入 ResponseHandler
    from app.utils.response.handler import ResponseHandler
    print("✓ 成功导入 ResponseHandler")
    
    print("\n所有模块导入成功！重构后的响应模块工作正常。")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
