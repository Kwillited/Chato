"""统一验证工具模块，提供所有验证功能"""
import os
import re
from app.utils.file_utils import FileUtils


class ValidationUtils:
    """验证工具类，封装所有验证方法"""
    
    # 正则表达式模式
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^1[3-9]\d{9}$'
    UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    @staticmethod
    def validate_input(data, required_fields):
        """
        验证输入数据的必填字段
        
        Args:
            data: 输入数据字典
            required_fields: 必填字段列表
            
        Returns:
            dict: 验证通过的输入数据
            
        Raises:
            ValueError: 缺少必填字段或字段为空时抛出
        """
        if not isinstance(data, dict):
            raise ValueError("输入数据必须是字典类型")
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f'缺少必填字段: {field}')
            if not data[field]:
                raise ValueError(f'字段 {field} 不能为空')
        
        return data
    
    @staticmethod
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
    
    @staticmethod
    def validate_email(email, param_name='邮箱'):
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            param_name: 参数名称（用于错误消息）
            
        Returns:
            str: 验证后的邮箱地址
            
        Raises:
            ValueError: 邮箱格式不正确时抛出
        """
        if not email:
            raise ValueError(f'{param_name}不能为空')
        
        if not re.match(ValidationUtils.EMAIL_PATTERN, email):
            raise ValueError(f'{param_name}格式不正确')
        
        return email
    
    @staticmethod
    def validate_phone(phone, param_name='手机号'):
        """
        验证手机号格式
        
        Args:
            phone: 手机号
            param_name: 参数名称（用于错误消息）
            
        Returns:
            str: 验证后的手机号
            
        Raises:
            ValueError: 手机号格式不正确时抛出
        """
        if not phone:
            raise ValueError(f'{param_name}不能为空')
        
        if not re.match(ValidationUtils.PHONE_PATTERN, phone):
            raise ValueError(f'{param_name}格式不正确')
        
        return phone
    
    @staticmethod
    def validate_uuid(uuid_str, param_name='UUID'):
        """
        验证UUID格式
        
        Args:
            uuid_str: UUID字符串
            param_name: 参数名称（用于错误消息）
            
        Returns:
            str: 验证后的UUID字符串
            
        Raises:
            ValueError: UUID格式不正确时抛出
        """
        if not uuid_str:
            raise ValueError(f'{param_name}不能为空')
        
        if not re.match(ValidationUtils.UUID_PATTERN, uuid_str, re.IGNORECASE):
            raise ValueError(f'{param_name}格式不正确')
        
        return uuid_str
    
    @staticmethod
    def validate_number(value, param_name='值', min_value=None, max_value=None, allow_zero=True):
        """
        验证数字范围
        
        Args:
            value: 数字值
            param_name: 参数名称（用于错误消息）
            min_value: 最小值
            max_value: 最大值
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
        
        if min_value is not None and num_value < min_value:
            raise ValueError(f'{param_name}不能小于 {min_value}')
        
        if max_value is not None and num_value > max_value:
            raise ValueError(f'{param_name}不能大于 {max_value}')
        
        if not allow_zero and num_value == 0:
            raise ValueError(f'{param_name}不能为零')
        
        return num_value
    
    @staticmethod
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
        return ValidationUtils.validate_number(
            value, 
            param_name=param_name, 
            min_value=0 if allow_zero else 0.0000001, 
            allow_zero=allow_zero
        )
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
    def validate_file_extension(file_name, allowed_extensions, param_name='文件'):
        """
        验证文件扩展名
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表，例如 ['.txt', '.pdf']
            param_name: 参数名称（用于错误消息）
            
        返回:
            str: 验证后的文件名
            
        异常:
            ValueError: 扩展名不允许时抛出
        """
        return FileUtils.validate_file_extension(file_name, allowed_extensions, param_name)
    
    @staticmethod
    def validate_file_type(file_name, allowed_extensions, param_name='文件'):
        """
        验证文件类型
        
        参数:
            file_name: 文件名
            allowed_extensions: 允许的扩展名列表，例如 ['.txt', '.pdf']
            param_name: 参数名称（用于错误消息）
            
        返回:
            str: 验证后的文件名
            
        异常:
            ValueError: 类型不允许时抛出
        """
        return FileUtils.validate_file_type(file_name, allowed_extensions, param_name)
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
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
    

