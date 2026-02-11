import os

# 模拟 mcp_adapter.py 中的路径计算（修复后）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 模拟 mcp_adapter.py 所在目录
mcp_adapter_dir = os.path.join(current_dir, '..', 'app', 'utils', 'mcp')
config_path = os.path.join(mcp_adapter_dir, '..', '..', '..', 'config', 'mcp_config.json')
resolved_path = os.path.abspath(config_path)

print(f"Current directory: {current_dir}")
print(f"Calculated config path: {config_path}")
print(f"Resolved config path: {resolved_path}")
print(f"File exists: {os.path.exists(resolved_path)}")

# 正确的配置文件路径
correct_path = os.path.join(current_dir, 'config', 'mcp_config.json')
print(f"\nCorrect config path: {correct_path}")
print(f"File exists: {os.path.exists(correct_path)}")
