"""参数验证工具函数"""
import os
import re


def validate_string_parameter(param_name, param_value, min_length=0, max_length=None, allow_empty=False):
    """
    验证字符串参数
    
    Args:
        param_name: 参数名称（用于错误消息）
        param_value: 参数值
        min_length: 最小长度
        max_length: 最大长度
        allow_empty: 是否允许空值
    
    Returns:
        str: 验证后的字符串
    
    Raises:
        ValueError: 参数验证失败时抛出
    """
    if not allow_empty and param_value is None:
        raise ValueError(f'{param_name}不能为空')
    
    if param_value is not None:
        if not isinstance(param_value, str):
            raise ValueError(f'{param_name}必须是字符串类型')
        
        if not allow_empty and not param_value.strip():
            raise ValueError(f'{param_name}不能为空字符串')
        
        if len(param_value) < min_length:
            raise ValueError(f'{param_name}长度不能小于{min_length}')
        
        if max_length is not None and len(param_value) > max_length:
            raise ValueError(f'{param_name}长度不能大于{max_length}')
    
    return param_value



def validate_file_exists(file_path, param_name='文件'):
    """
    验证文件是否存在
    
    Args:
        file_path: 文件路径
        param_name: 参数名称（用于错误消息）
    
    Returns:
        str: 验证后的文件路径
    
    Raises:
        ValueError: 文件不存在时抛出
    """
    if not file_path:
        raise ValueError(f'{param_name}路径不能为空')
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise ValueError(f'{param_name}不存在: {file_path}')
    
    return file_path


def validate_directory_exists(directory_path, param_name='目录'):
    """
    验证目录是否存在
    
    Args:
        directory_path: 目录路径
        param_name: 参数名称（用于错误消息）
    
    Returns:
        str: 验证后的目录路径
    
    Raises:
        ValueError: 目录不存在时抛出
    """
    if not directory_path:
        raise ValueError(f'{param_name}路径不能为空')
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise ValueError(f'{param_name}不存在: {directory_path}')
    
    return directory_path


def validate_file_extension(filename, allowed_extensions, param_name='文件'):
    """
    验证文件扩展名
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表，例如 ['.txt', '.pdf']
        param_name: 参数名称（用于错误消息）
    
    Returns:
        str: 验证后的文件名
    
    Raises:
        ValueError: 扩展名不允许时抛出
    """
    if not filename:
        raise ValueError(f'{param_name}名称不能为空')
    
    if not allowed_extensions:
        return filename
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        allowed_str = ', '.join(allowed_extensions)
        raise ValueError(f'{param_name}类型不允许。允许的类型: {allowed_str}')
    
    return filename


def validate_positive_number(value, param_name='值', allow_zero=False):
    """
    验证正数
    
    Args:
        value: 要验证的值
        param_name: 参数名称（用于错误消息）
        allow_zero: 是否允许为零
    
    Returns:
        float/int: 验证后的数值
    
    Raises:
        ValueError: 数值无效时抛出
    """
    if value is None:
        raise ValueError(f'{param_name}不能为空')
    
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{param_name}必须是有效的数字')
    
    if allow_zero:
        if num_value < 0:
            raise ValueError(f'{param_name}不能为负数')
    else:
        if num_value <= 0:
            raise ValueError(f'{param_name}必须大于零')
    
    return num_value


def validate_array_parameter(param_name, param_value, min_items=0, max_items=None, item_type=None):
    """
    验证数组参数
    
    Args:
        param_name: 参数名称（用于错误消息）
        param_value: 参数值
        min_items: 最小元素数量
        max_items: 最大元素数量
        item_type: 元素类型验证（如果指定）
    
    Returns:
        list: 验证后的数组
    
    Raises:
        ValueError: 数组验证失败时抛出
    """
    if param_value is None:
        raise ValueError(f'{param_name}不能为空')
    
    if not isinstance(param_value, (list, tuple)):
        raise ValueError(f'{param_name}必须是数组类型')
    
    if len(param_value) < min_items:
        raise ValueError(f'{param_name}元素数量不能小于{min_items}')
    
    if max_items is not None and len(param_value) > max_items:
        raise ValueError(f'{param_name}元素数量不能大于{max_items}')
    
    if item_type is not None:
        for i, item in enumerate(param_value):
            if not isinstance(item, item_type):
                raise ValueError(f'{param_name}[{i}]必须是{item_type.__name__}类型')
    
    return list(param_value)


def validate_dict_parameter(param_name, param_value, required_keys=None, optional_keys=None):
    """
    验证字典参数
    
    Args:
        param_name: 参数名称（用于错误消息）
        param_value: 参数值
        required_keys: 必需的键列表
        optional_keys: 可选的键列表
    
    Returns:
        dict: 验证后的字典
    
    Raises:
        ValueError: 字典验证失败时抛出
    """
    if param_value is None:
        raise ValueError(f'{param_name}不能为空')
    
    if not isinstance(param_value, dict):
        raise ValueError(f'{param_name}必须是字典类型')
    
    # 验证必需键
    if required_keys:
        for key in required_keys:
            if key not in param_value:
                raise ValueError(f'{param_name}缺少必需的键: {key}')
    
    # 验证可选键（如果指定了，则不允许其他键）
    if optional_keys is not None:
        all_allowed_keys = set(required_keys or []) | set(optional_keys)
        for key in param_value:
            if key not in all_allowed_keys:
                raise ValueError(f'{param_name}包含不允许的键: {key}')
    
    return param_value


def validate_pattern_match(param_name, param_value, pattern, error_message=None):
    """
    验证参数是否匹配正则表达式模式
    
    Args:
        param_name: 参数名称（用于错误消息）
        param_value: 参数值
        pattern: 正则表达式模式
        error_message: 自定义错误消息
    
    Returns:
        str: 验证后的字符串
    
    Raises:
        ValueError: 不匹配模式时抛出
    """
    if param_value is None:
        raise ValueError(f'{param_name}不能为空')
    
    if not isinstance(param_value, str):
        raise ValueError(f'{param_name}必须是字符串类型')
    
    if not re.match(pattern, param_value):
        if error_message:
            raise ValueError(error_message)
        else:
            raise ValueError(f'{param_name}不匹配要求的格式: {pattern}')
    
    return param_value