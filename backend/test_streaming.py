from langchain_ollama import ChatOllama

# 启用 reasoning 模式
model = ChatOllama(
    model="qwen3:0.6b",  # 使用支持推理的模型
    reasoning=True,           # 启用推理模式
    temperature=0.7
)

response = model.invoke("strawberry 这个词里有多少个字母 r？")

# 推理过程会单独存放在 additional_kwargs 中
print("推理过程:", response.additional_kwargs.get("reasoning_content"))
print("最终答案:", response.content)