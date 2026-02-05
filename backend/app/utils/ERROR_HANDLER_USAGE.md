# 统一错误处理模块使用说明

## 1. 模块介绍

`ErrorHandler` 是一个统一的错误处理模块，整合了装饰器形式的错误处理和 HTTP 错误响应功能，提供了一致、灵活的错误处理机制。

### 1.1 主要功能

- **装饰器形式的错误处理**：统一处理函数异常，支持自定义默认返回值和日志级别
- **HTTP 错误响应**：处理异常并返回标准的 HTTP 错误响应格式
- **支持多种错误类型**：服务器错误、验证错误、资源未找到错误、未授权访问错误、禁止访问错误
- **灵活的配置选项**：支持重新抛出异常、自定义日志级别等

### 1.2 优势

- **统一接口**：所有错误处理功能都通过 `ErrorHandler` 类和相关装饰器提供
- **灵活配置**：支持多种错误处理策略，适应不同场景
- **标准响应格式**：返回标准的 HTTP 错误响应格式，便于前端处理
- **完善的日志记录**：自动记录错误信息，便于排查问题
- **向后兼容**：保持了对旧装饰器函数的支持

## 2. 快速开始

### 2.1 基本导入

```python
from app.utils import ErrorHandler, handle_errors, handle_api_errors
```

### 2.2 装饰器使用示例

#### 2.2.1 基本错误处理

```python
from app.utils import handle_errors

@handle_errors(default_return="操作失败")
def risky_operation():
    # 可能会抛出异常的操作
    if some_condition:
        raise ValueError("操作失败的原因")
    return "操作成功"

# 使用
try:
    result = risky_operation()
    print(f"操作结果: {result}")
except Exception as e:
    print(f"捕获到异常: {e}")
```

#### 2.2.2 重新抛出异常

```python
from app.utils import handle_errors

@handle_errors(re_raise=True)
def operation_needs_exception():
    # 需要将异常传递给上层的操作
    raise ValueError("需要上层处理的错误")

# 使用
try:
    operation_needs_exception()
except ValueError as e:
    print(f"上层捕获到异常: {e}")
    # 处理异常
```

#### 2.2.3 API 错误处理

```python
from app.utils import handle_api_errors

@handle_api_errors(default_return={"error": "API 操作失败"})
def api_operation():
    # API 操作
    raise ValueError("API 错误")

# 使用
result = api_operation()
if "error" in result:
    print(f"API 错误: {result['error']}")
else:
    print(f"API 成功: {result}")
```

### 2.3 HTTP 错误响应使用示例

#### 2.3.1 处理服务器错误

```python
from app.utils import ErrorHandler

try:
    # 可能会抛出异常的操作
    raise Exception("服务器内部错误")
except Exception as e:
    # 处理异常并返回 HTTP 错误响应
    error_response, status_code = ErrorHandler.handle_exception(e, "服务器内部错误")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    # 返回给客户端
    # return error_response, status_code
```

#### 2.3.2 处理验证错误

```python
from app.utils import ErrorHandler

try:
    # 验证操作
    raise ValueError("参数格式不正确")
except ValueError as e:
    # 处理验证错误
    error_response, status_code = ErrorHandler.handle_validation_error(e, "请求参数验证失败")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    # return error_response, status_code
```

#### 2.3.3 处理资源未找到错误

```python
from app.utils import ErrorHandler

# 检查资源是否存在
resource_id = "123"
resource_exists = False  # 假设资源不存在

if not resource_exists:
    # 处理资源未找到错误
    error_response, status_code = ErrorHandler.handle_not_found_error("用户", resource_id)
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    # return error_response, status_code
```

#### 2.3.4 处理未授权访问错误

```python
from app.utils import ErrorHandler

# 检查用户是否登录
user_logged_in = False  # 假设用户未登录

if not user_logged_in:
    # 处理未授权访问错误
    error_response, status_code = ErrorHandler.handle_unauthorized_error("您需要登录才能访问此资源")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    # return error_response, status_code
```

#### 2.3.5 处理禁止访问错误

```python
from app.utils import ErrorHandler

# 检查用户权限
user_has_permission = False  # 假设用户没有权限

if not user_has_permission:
    # 处理禁止访问错误
    error_response, status_code = ErrorHandler.handle_forbidden_error("您没有权限执行此操作")
    print(f"错误响应: {error_response}")
    print(f"状态码: {status_code}")
    # return error_response, status_code
```

## 3. 详细使用指南

### 3.1 装饰器参数说明

#### 3.1.1 `handle_errors` 装饰器

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `default_return` | `Any` | `None` | 发生异常时的默认返回值 |
| `log_error` | `bool` | `True` | 是否记录错误日志 |
| `log_level` | `str` | `"error"` | 日志级别，可选值：debug, info, warning, error, critical |
| `re_raise` | `bool` | `False` | 是否重新抛出异常 |

#### 3.1.2 特定场景装饰器

- `handle_api_errors`：API 错误处理装饰器，专为 API 接口设计
- `handle_db_errors`：数据库错误处理装饰器，专为数据库操作设计
- `handle_vector_errors`：向量操作错误处理装饰器，专为向量存储操作设计

这些装饰器都支持 `default_return` 和 `re_raise` 参数。

### 3.2 HTTP 错误响应方法

#### 3.2.1 `handle_exception` 方法

```python
@staticmethod
def handle_exception(exception: Exception, message: str = "操作失败", error_type: str = "server") -> Tuple[dict, int]:
    """
    统一处理异常，返回 HTTP 错误响应
    
    Args:
        exception: 捕获的异常
        message: 返回给客户端的错误信息
        error_type: 错误类型，可选值：validation, not_found, unauthorized, forbidden, server
        
    Returns:
        Tuple[dict, int]: (错误响应字典, HTTP 状态码)
    """
```

#### 3.2.2 特定错误类型方法

- `handle_validation_error`：处理验证异常，返回 400 状态码
- `handle_not_found_error`：处理资源未找到异常，返回 404 状态码
- `handle_unauthorized_error`：处理未授权访问错误，返回 401 状态码
- `handle_forbidden_error`：处理禁止访问错误，返回 403 状态码

### 3.3 错误响应格式

#### 3.3.1 标准错误响应格式

```json
{
    "error": "错误消息",
    "details": "错误详细信息",
    "error_type": "错误类型"
}
```

#### 3.3.2 资源未找到错误响应格式

```json
{
    "error": "资源不存在: 标识符",
    "error_type": "not_found",
    "resource": "资源名称",
    "identifier": "资源标识符"
}
```

## 4. 最佳实践

### 4.1 装饰器使用场景

#### 4.1.1 普通函数

对于普通函数，使用 `handle_errors` 装饰器，设置合适的默认返回值：

```python
@handle_errors(default_return=False)
def check_resource_exists(resource_id):
    # 检查资源是否存在
    # ...
```

#### 4.1.2 API 接口

对于 API 接口，使用 `handle_api_errors` 装饰器，返回标准的错误响应：

```python
@handle_api_errors(default_return={"error": "API 操作失败", "code": 500})
def api_endpoint():
    # API 操作
    # ...
```

#### 4.1.3 需要异常冒泡的场景

对于需要将异常传递给上层的场景，使用 `re_raise=True`：

```python
@handle_errors(re_raise=True)
def operation_needs_outer_handling():
    # 需要上层处理异常的操作
    # ...
```

### 4.2 HTTP 错误响应使用场景

#### 4.2.1 全局异常处理器

在 FastAPI 等框架中，可以使用 `ErrorHandler` 处理全局异常：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils import ErrorHandler

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_response, status_code = ErrorHandler.handle_exception(exc, "服务器内部错误")
    return JSONResponse(status_code=status_code, content=error_response)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    error_response, status_code = ErrorHandler.handle_validation_error(exc, "请求参数错误")
    return JSONResponse(status_code=status_code, content=error_response)
```

#### 4.2.2 服务层错误处理

在服务层中，可以使用 `ErrorHandler` 处理业务逻辑错误：

```python
from app.utils import ErrorHandler

class UserService:
    def get_user(self, user_id):
        user = self.db.find_user(user_id)
        if not user:
            return ErrorHandler.handle_not_found_error("用户", user_id)
        return user

# 使用
try:
    user = user_service.get_user("123")
    if isinstance(user, tuple):
        # 处理错误响应
        error_response, status_code = user
        return JSONResponse(status_code=status_code, content=error_response)
    # 处理成功情况
    return user
except Exception as e:
    error_response, status_code = ErrorHandler.handle_exception(e, "获取用户失败")
    return JSONResponse(status_code=status_code, content=error_response)
```

### 4.3 日志记录最佳实践

- **错误级别选择**：根据错误的严重程度选择合适的日志级别
- **详细的错误信息**：在异常处理中提供详细的错误信息，便于排查问题
- **上下文信息**：在日志中包含必要的上下文信息，如操作类型、用户ID等

## 5. 示例代码

### 5.1 完整的 API 接口示例

```python
from fastapi import FastAPI, HTTPException
from app.utils import ErrorHandler, handle_api_errors

app = FastAPI()

@handle_api_errors(default_return={"error": "获取用户失败"})
async def get_user_internal(user_id):
    """内部获取用户的函数"""
    # 模拟数据库操作
    if user_id == "123":
        return {"id": "123", "name": "张三", "email": "zhangsan@example.com"}
    elif user_id == "456":
        raise ValueError("用户数据错误")
    else:
        # 返回错误响应
        error_response, status_code = ErrorHandler.handle_not_found_error("用户", user_id)
        raise HTTPException(status_code=status_code, detail=error_response)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    try:
        user = await get_user_internal(user_id)
        return user
    except HTTPException:
        raise
    except Exception as e:
        error_response, status_code = ErrorHandler.handle_exception(e, "服务器内部错误")
        raise HTTPException(status_code=status_code, detail=error_response)
```

### 5.2 数据库操作示例

```python
from app.utils import handle_db_errors, ErrorHandler

class DatabaseService:
    @handle_db_errors(default_return=None)
    def execute_query(self, query, params=None):
        """执行数据库查询"""
        # 执行数据库操作
        try:
            # 模拟数据库操作
            if some_error_condition:
                raise Exception("数据库操作失败")
            return "查询结果"
        except Exception as e:
            # 处理数据库错误
            error_response, status_code = ErrorHandler.handle_exception(e, "数据库操作失败")
            print(f"数据库错误: {error_response}")
            raise

    @handle_db_errors(default_return=[])
    def get_all_users(self):
        """获取所有用户"""
        # 执行查询
        return self.execute_query("SELECT * FROM users")
```

## 6. 常见问题

### 6.1 装饰器不生效

**问题**：装饰器没有捕获到异常

**解决方案**：
- 确保装饰器应用在正确的函数上
- 检查函数是否是异步函数，如果是，需要使用 `async` 装饰器
- 检查是否在函数内部使用了 `try-except` 块，捕获了异常

### 6.2 错误响应格式不符合预期

**问题**：返回的错误响应格式不符合预期

**解决方案**：
- 检查使用的错误处理方法是否正确
- 检查错误类型参数是否正确
- 检查异常对象是否包含必要的信息

### 6.3 日志记录不完整

**问题**：错误日志记录不完整

**解决方案**：
- 确保 `log_error` 参数设置为 `True`
- 检查日志级别设置是否正确
- 确保异常对象包含足够的信息

## 7. 总结

`ErrorHandler` 模块提供了一套统一、灵活的错误处理机制，适用于各种场景的错误处理需求。通过使用装饰器和 HTTP 错误响应方法，可以：

1. **统一错误处理逻辑**：减少重复的 `try-except` 代码
2. **提高代码可读性**：错误处理逻辑清晰明了
3. **便于维护**：集中管理错误处理策略
4. **标准化错误响应**：返回标准的 HTTP 错误响应格式
5. **完善的日志记录**：自动记录错误信息，便于排查问题

建议在项目中广泛使用 `ErrorHandler` 模块，以提高代码质量和可维护性。
