"""测试统一错误处理模块"""
from app.utils import ErrorHandler, handle_errors, handle_api_errors


# 测试装饰器功能
def test_decorator_with_default_return():
    """测试装饰器，使用默认返回值"""
    print("\n=== 测试装饰器，使用默认返回值 ===")
    
    @handle_errors(default_return="错误发生，返回默认值")
    def func_with_error():
        raise ValueError("测试错误")
    
    result = func_with_error()
    print(f"函数执行结果: {result}")
    assert result == "错误发生，返回默认值"
    print("✅ 测试通过: 装饰器正确返回默认值")


def test_decorator_with_re_raise():
    """测试装饰器，重新抛出异常"""
    print("\n=== 测试装饰器，重新抛出异常 ===")
    
    @handle_errors(re_raise=True)
    def func_with_error_re_raise():
        raise ValueError("测试错误，需要重新抛出")
    
    try:
        func_with_error_re_raise()
        print("❌ 测试失败: 异常应该被重新抛出")
        assert False
    except ValueError as e:
        print(f"✅ 测试通过: 异常被正确重新抛出: {e}")


def test_api_decorator():
    """测试API错误处理装饰器"""
    print("\n=== 测试API错误处理装饰器 ===")
    
    @handle_api_errors(default_return={"error": "API错误"})
    def api_func_with_error():
        raise ValueError("API测试错误")
    
    result = api_func_with_error()
    print(f"API函数执行结果: {result}")
    assert result == {"error": "API错误"}
    print("✅ 测试通过: API装饰器正确返回默认值")


# 测试HTTP错误响应功能
def test_handle_exception():
    """测试处理异常并返回HTTP响应"""
    print("\n=== 测试处理异常并返回HTTP响应 ===")
    
    try:
        raise ValueError("测试服务器错误")
    except Exception as e:
        error_response, status_code = ErrorHandler.handle_exception(e, "服务器内部错误")
        print(f"错误响应: {error_response}")
        print(f"状态码: {status_code}")
        assert status_code == 500
        assert error_response['error'] == "服务器内部错误"
        assert error_response['error_type'] == "server"
        print("✅ 测试通过: 正确处理服务器错误")


def test_handle_validation_error():
    """测试处理验证异常"""
    print("\n=== 测试处理验证异常 ===")
    
    try:
        raise ValueError("参数格式不正确")
    except Exception as e:
        error_response, status_code = ErrorHandler.handle_validation_error(e, "请求参数验证失败")
        print(f"错误响应: {error_response}")
        print(f"状态码: {status_code}")
        assert status_code == 400
        assert error_response['error'] == "请求参数验证失败"
        assert error_response['error_type'] == "validation"
        print("✅ 测试通过: 正确处理验证错误")


def test_handle_not_found_error():
    """测试处理资源未找到异常"""
    print("\n=== 测试处理资源未找到异常 ===")
    
    error_response, status_code = ErrorHandler.handle_not_found_error("用户", "123")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    assert status_code == 404
    assert error_response['error'] == "用户 不存在: 123"
    assert error_response['error_type'] == "not_found"
    assert error_response['resource'] == "用户"
    assert error_response['identifier'] == "123"
    print("✅ 测试通过: 正确处理资源未找到错误")


def test_handle_unauthorized_error():
    """测试处理未授权访问错误"""
    print("\n=== 测试处理未授权访问错误 ===")
    
    error_response, status_code = ErrorHandler.handle_unauthorized_error("您没有登录")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    assert status_code == 401
    assert error_response['error'] == "您没有登录"
    assert error_response['error_type'] == "unauthorized"
    print("✅ 测试通过: 正确处理未授权访问错误")


def test_handle_forbidden_error():
    """测试处理禁止访问错误"""
    print("\n=== 测试处理禁止访问错误 ===")
    
    error_response, status_code = ErrorHandler.handle_forbidden_error("您没有权限访问此资源")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    assert status_code == 403
    assert error_response['error'] == "您没有权限访问此资源"
    assert error_response['error_type'] == "forbidden"
    print("✅ 测试通过: 正确处理禁止访问错误")


if __name__ == "__main__":
    print("开始测试统一错误处理模块...")
    
    # 运行所有测试
    test_decorator_with_default_return()
    test_decorator_with_re_raise()
    test_api_decorator()
    test_handle_exception()
    test_handle_validation_error()
    test_handle_not_found_error()
    test_handle_unauthorized_error()
    test_handle_forbidden_error()
    
    print("\n所有测试通过！统一错误处理模块工作正常。")
