"""输入验证工具类，提供统一的输入数据验证功能"""

class InputValidator:
    """输入验证工具类，封装所有输入验证方法"""
    
    @staticmethod
    def validate_input(data, required_fields):
        """
        验证输入数据
        
        参数:
            data: 输入数据
            required_fields: 必填字段列表
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        for field in required_fields:
            if field not in data:
                return False, f'缺少必填字段: {field}'
            if not data[field]:
                return False, f'字段 {field} 不能为空'
        return True, None
    
    @staticmethod
    def validate_email(email):
        """
        验证邮箱格式
        
        参数:
            email: 邮箱地址
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            return False, '邮箱不能为空'
        if not re.match(email_pattern, email):
            return False, '邮箱格式不正确'
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        """
        验证手机号格式
        
        参数:
            phone: 手机号
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        import re
        phone_pattern = r'^1[3-9]\d{9}$'
        if not phone:
            return False, '手机号不能为空'
        if not re.match(phone_pattern, phone):
            return False, '手机号格式不正确'
        return True, None
    
    @staticmethod
    def validate_uuid(uuid_str):
        """
        验证UUID格式
        
        参数:
            uuid_str: UUID字符串
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not uuid_str:
            return False, 'UUID不能为空'
        if not re.match(uuid_pattern, uuid_str, re.IGNORECASE):
            return False, 'UUID格式不正确'
        return True, None
    
    @staticmethod
    def validate_number(value, min_value=None, max_value=None):
        """
        验证数字范围
        
        参数:
            value: 数字值
            min_value: 最小值
            max_value: 最大值
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return False, '值必须是数字'
        
        if min_value is not None and value < min_value:
            return False, f'值不能小于 {min_value}'
        if max_value is not None and value > max_value:
            return False, f'值不能大于 {max_value}'
        
        return True, None