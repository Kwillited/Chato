"""测试API接口"""
import requests
import json

# 测试POST /api/settings/system接口
url = "http://localhost:5000/api/settings/system"
headers = {"Content-Type": "application/json"}
data = {
    "dark_mode": False,
    "streaming_enabled": True,
    "chat_style": "bubble",
    "view_mode": "grid",
    "default_model": "",
    "newMessage": True,
    "sound": False,
    "system": True,
    "displayTime": "5秒"
}

print("测试PATCH /api/settings/system接口...")
response = requests.patch(url, headers=headers, data=json.dumps(data))
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")
print()

# 测试GET /api/settings/system接口
print("测试GET /api/settings/system接口...")
response = requests.get(url)
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")
print()

print("测试完成！")
