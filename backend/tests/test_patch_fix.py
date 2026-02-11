"""测试PATCH方法修复是否正确"""
import requests
import json

# 测试URL
url = "http://localhost:5000/api/settings/system"
headers = {"Content-Type": "application/json"}

print("=== 测试PATCH方法修复 ===")

# 1. 首先获取当前系统设置
print("\n1. 获取当前系统设置...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
current_settings = response.json()
print(f"当前设置: {json.dumps(current_settings, indent=2, ensure_ascii=False)}")

# 2. 只修改sound字段为true
print("\n2. 只修改sound字段为true...")
patch_data = {"sound": True}
response = requests.patch(url, headers=headers, data=json.dumps(patch_data))
print(f"状态码: {response.status_code}")
print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# 3. 再次获取系统设置，检查是否只有sound字段被修改
print("\n3. 再次获取系统设置，检查是否只有sound字段被修改...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
updated_settings = response.json()
print(f"更新后设置: {json.dumps(updated_settings, indent=2, ensure_ascii=False)}")

# 4. 检查其他字段是否保持不变
print("\n4. 检查其他字段是否保持不变...")
unchanged_fields = ["dark_mode", "chat_style", "view_mode", "newMessage", "system", "displayTime"]
all_unchanged = True

for field in unchanged_fields:
    if field in current_settings and field in updated_settings:
        if current_settings[field] == updated_settings[field]:
            print(f"✅ {field}: 保持不变 ({current_settings[field]})")
        else:
            print(f"❌ {field}: 被修改了 ({current_settings[field]} → {updated_settings[field]})")
            all_unchanged = False

if all_unchanged:
    print("\n🎉 测试通过! 只有sound字段被修改，其他字段保持不变")
else:
    print("\n❌ 测试失败! 其他字段也被修改了")

# 5. 测试只修改dark_mode字段
print("\n5. 测试只修改dark_mode字段...")
patch_data = {"dark_mode": True}
response = requests.patch(url, headers=headers, data=json.dumps(patch_data))
print(f"状态码: {response.status_code}")

# 6. 再次获取系统设置，检查是否只有dark_mode字段被修改
print("\n6. 再次获取系统设置，检查是否只有dark_mode字段被修改...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
final_settings = response.json()
print(f"最终设置: {json.dumps(final_settings, indent=2, ensure_ascii=False)}")

# 7. 检查sound字段是否保持不变
print("\n7. 检查sound字段是否保持不变...")
if final_settings.get("sound") == True:
    print("✅ sound: 保持不变 (True)")
else:
    print(f"❌ sound: 被修改了 (True → {final_settings.get('sound')})")

print("\n=== 测试完成 ===")
