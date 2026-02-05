"""测试统一验证模块"""
from app.utils import ValidationUtils


def test_validate_input():
    """测试输入验证"""
    print("\n=== 测试输入验证 ===")
    
    # 测试通过的情况
    try:
        data = {"name": "测试", "age": 18}
        result = ValidationUtils.validate_input(data, ["name", "age"])
        print(f"✅ 输入验证通过: {result}")
    except Exception as e:
        print(f"❌ 输入验证失败: {e}")
    
    # 测试缺少字段的情况
    try:
        data = {"name": "测试"}
        result = ValidationUtils.validate_input(data, ["name", "age"])
        print(f"❌ 输入验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 输入验证正确捕获缺少字段: {e}")
    
    # 测试字段为空的情况
    try:
        data = {"name": "", "age": 18}
        result = ValidationUtils.validate_input(data, ["name", "age"])
        print(f"❌ 输入验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 输入验证正确捕获空字段: {e}")


def test_validate_string():
    """测试字符串验证"""
    print("\n=== 测试字符串验证 ===")
    
    # 测试通过的情况
    try:
        result = ValidationUtils.validate_string_parameter("用户名", "test_user", min_length=3, max_length=20)
        print(f"✅ 字符串验证通过: {result}")
    except Exception as e:
        print(f"❌ 字符串验证失败: {e}")
    
    # 测试长度不足的情况
    try:
        result = ValidationUtils.validate_string_parameter("用户名", "te", min_length=3)
        print(f"❌ 字符串验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 字符串验证正确捕获长度不足: {e}")


def test_validate_email():
    """测试邮箱验证"""
    print("\n=== 测试邮箱验证 ===")
    
    # 测试通过的情况
    try:
        result = ValidationUtils.validate_email("test@example.com")
        print(f"✅ 邮箱验证通过: {result}")
    except Exception as e:
        print(f"❌ 邮箱验证失败: {e}")
    
    # 测试格式错误的情况
    try:
        result = ValidationUtils.validate_email("invalid-email")
        print(f"❌ 邮箱验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 邮箱验证正确捕获格式错误: {e}")


def test_validate_phone():
    """测试手机号验证"""
    print("\n=== 测试手机号验证 ===")
    
    # 测试通过的情况
    try:
        result = ValidationUtils.validate_phone("13812345678")
        print(f"✅ 手机号验证通过: {result}")
    except Exception as e:
        print(f"❌ 手机号验证失败: {e}")
    
    # 测试格式错误的情况
    try:
        result = ValidationUtils.validate_phone("1234567890")
        print(f"❌ 手机号验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 手机号验证正确捕获格式错误: {e}")


def test_validate_number():
    """测试数字验证"""
    print("\n=== 测试数字验证 ===")
    
    # 测试通过的情况
    try:
        result = ValidationUtils.validate_number("100", min_value=0, max_value=200)
        print(f"✅ 数字验证通过: {result}")
    except Exception as e:
        print(f"❌ 数字验证失败: {e}")
    
    # 测试超出范围的情况
    try:
        result = ValidationUtils.validate_number("250", max_value=200)
        print(f"❌ 数字验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 数字验证正确捕获超出范围: {e}")


def test_validate_array():
    """测试数组验证"""
    print("\n=== 测试数组验证 ===")
    
    # 测试通过的情况
    try:
        result = ValidationUtils.validate_array_parameter("用户列表", ["user1", "user2", "user3"], min_items=2, max_items=5)
        print(f"✅ 数组验证通过: {result}")
    except Exception as e:
        print(f"❌ 数组验证失败: {e}")
    
    # 测试元素数量不足的情况
    try:
        result = ValidationUtils.validate_array_parameter("用户列表", ["user1"], min_items=2)
        print(f"❌ 数组验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 数组验证正确捕获元素数量不足: {e}")


def test_validate_dict():
    """测试字典验证"""
    print("\n=== 测试字典验证 ===")
    
    # 测试通过的情况
    try:
        data = {"name": "测试", "age": 18}
        result = ValidationUtils.validate_dict_parameter("用户信息", data, required_keys=["name", "age"])
        print(f"✅ 字典验证通过: {result}")
    except Exception as e:
        print(f"❌ 字典验证失败: {e}")
    
    # 测试缺少必需键的情况
    try:
        data = {"name": "测试"}
        result = ValidationUtils.validate_dict_parameter("用户信息", data, required_keys=["name", "age"])
        print(f"❌ 字典验证应该失败，但通过了: {result}")
    except ValueError as e:
        print(f"✅ 字典验证正确捕获缺少必需键: {e}")


def test_file_functions():
    """测试文件相关函数"""
    print("\n=== 测试文件相关函数 ===")
    
    # 测试文件扩展名判断
    test_file = "test.txt"
    is_text = ValidationUtils.is_text_file(test_file)
    print(f"文件 {test_file} 是文本文件: {is_text}")
    
    test_file = "test.pdf"
    is_pdf = ValidationUtils.is_pdf_file(test_file)
    print(f"文件 {test_file} 是PDF文件: {is_pdf}")
    
    test_file = "test.docx"
    is_word = ValidationUtils.is_word_file(test_file)
    print(f"文件 {test_file} 是Word文件: {is_word}")


if __name__ == "__main__":
    print("开始测试统一验证模块...")
    
    # 运行所有测试
    test_validate_input()
    test_validate_string()
    test_validate_email()
    test_validate_phone()
    test_validate_number()
    test_validate_array()
    test_validate_dict()
    test_file_functions()
    
    print("\n测试完成！")
