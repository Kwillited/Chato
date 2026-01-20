from langchain_mcp_adapters import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 1. 配置并连接MCP服务器
async with MultiServerMCPClient({
    "math_server": {
        "command": "python",
        "args": ["/path/to/your_math_mcp_server.py"],
        "transport": "stdio",  # 本地进程通信
    }
}) as client:
    
    # 2. 加载MCP工具
    tools = await client.get_tools()
    
    # 3. 创建LangGraph智能体
    model = ChatOpenAI(model="gpt-4o")
    agent = create_react_agent(model, tools)
    
    # 4. 运行智能体
    result = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    print(result["messages"][-1].content)