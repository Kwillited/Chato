"""测试default_model字段是否能正确更新"""
import requests
import json

# 测试URL
url = "http://localhost:5000/api/settings/system"
headers = {"Content-Type": "application/json"}

print("=== 测试default_model字段更新 ===")

# 1. 首先获取当前系统设置
print("\n1. 获取当前系统设置...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
current_settings = response.json()
print(f"当前设置: {json.dumps(current_settings, indent=2, ensure_ascii=False)}")

# 2. 只修改default_model字段
print("\n2. 只修改default_model字段...")
test_model = "GPT-4"
patch_data = {"default_model": test_model}
response = requests.patch(url, headers=headers, data=json.dumps(patch_data))
print(f"状态码: {response.status_code}")
print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# 3. 再次获取系统设置，检查default_model字段是否被修改
print("\n3. 再次获取系统设置，检查default_model字段是否被修改...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
updated_settings = response.json()
print(f"更新后设置: {json.dumps(updated_settings, indent=2, ensure_ascii=False)}")

# 4. 检查其他字段是否保持不变
print("\n4. 检查其他字段是否保持不变...")
unchanged_fields = ["dark_mode", "streaming_enabled", "chat_style", "view_mode", "newMessage", "sound", "system", "displayTime"]
all_unchanged = True

for field in unchanged_fields:
    if field in current_settings and field in updated_settings:
        if current_settings[field] == updated_settings[field]:
            print(f"✅ {field}: 保持不变 ({current_settings[field]})")
        else:
            print(f"❌ {field}: 被修改了 ({current_settings[field]} → {updated_settings[field]})")
            all_unchanged = False

# 5. 检查default_model字段是否被正确修改
print("\n5. 检查default_model字段是否被正确修改...")
if "default_model" in updated_settings and updated_settings["default_model"] == test_model:
    print(f"✅ default_model: 已成功修改为 {test_model}")
    default_model_updated = True
else:
    print(f"❌ default_model: 未被正确修改，当前值: {updated_settings.get('default_model')}")
    default_model_updated = False

if default_model_updated and all_unchanged:
    print("\n🎉 测试通过! default_model字段已成功修改，其他字段保持不变")
else:
    print("\n❌ 测试失败! default_model字段未被正确修改或其他字段被意外修改")

print("\n=== 测试完成 ===")
