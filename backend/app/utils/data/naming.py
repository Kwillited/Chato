"""命名转换工具类，提供统一的命名格式转换功能"""
import re

class NamingUtils:
    """命名转换工具类，封装所有命名格式转换方法"""
    
    @staticmethod
    def camel_to_snake(camel_str):
        """
        将驼峰命名转换为蛇形命名
        
        参数:
            camel_str: 驼峰命名字符串
            
        返回:
            蛇形命名字符串
        """
        # 转换驼峰命名为蛇形命名
        snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake_str
    
    @staticmethod
    def snake_to_camel(snake_str):
        """
        将蛇形命名转换为驼峰命名
        
        参数:
            snake_str: 蛇形命名字符串
            
        返回:
            驼峰命名字符串
        """
        # 转换蛇形命名为驼峰命名
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def convert_dict_keys(data_dict, convert_func=camel_to_snake):
        """
        将字典的所有键从一种命名格式转换为另一种命名格式
        
        参数:
            data_dict: 包含原命名格式键的字典
            convert_func: 转换函数，默认为camel_to_snake
            
        返回:
            包含新命名格式键的字典
        """
        return {
            convert_func(key): value 
            for key, value in data_dict.items()
        }
    
    @staticmethod
    def convert_dict_keys_recursive(data, convert_func=camel_to_snake):
        """
        递归地将字典的所有键从一种命名格式转换为另一种命名格式
        
        参数:
            data: 包含原命名格式键的字典或列表
            convert_func: 转换函数，默认为camel_to_snake
            
        返回:
            包含新命名格式键的字典或列表
        """
        if isinstance(data, dict):
            return {
                convert_func(key): NamingUtils.convert_dict_keys_recursive(value, convert_func)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                NamingUtils.convert_dict_keys_recursive(item, convert_func)
                for item in data
            ]
        else:
            return data
