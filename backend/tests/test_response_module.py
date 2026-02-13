"""测试响应模块导入"""

# 测试导入重构后的响应模块
print("开始测试响应模块导入...")

try:
    # 测试导入 MessageHandler
    from app.utils.message_handler import MessageHandler
    print("✓ 成功导入 MessageHandler")
    
    # 测试导入 StreamUtils
    from app.utils.response_strategy.stream import StreamUtils
    print("✓ 成功导入 StreamUtils")
    
    # 测试导入 AgentProcessor
    from app.utils.response_strategy.agent import AgentProcessor
    print("✓ 成功导入 AgentProcessor")
    
    # 测试导入工具类
    from app.utils.response_strategy.message_utils import ResponseMessageUtils
    print("✓ 成功导入 ResponseMessageUtils")
    
    from app.utils.response_strategy.agent_utils import AgentUtils
    print("✓ 成功导入 AgentUtils")
    
    from app.utils.response_strategy.streaming_utils import StreamingUtils
    print("✓ 成功导入 StreamingUtils")
    
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
    print("1. 基础策略类: ResponseStrategy, BaseResponseStrategyImpl")
    print("2. 具体策略: RegularResponseStrategy, StreamingResponseStrategy, AgentResponseStrategy")
    print("3. 工具类: ResponseMessageUtils, AgentUtils, StreamingUtils")
    print("4. 处理器: ResponseHandler")
    
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
