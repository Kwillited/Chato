"""Chato 工具函数模块"""

# 参数验证工具
from .validation_utils import (
    validate_string_parameter,
    validate_file_exists,
    validate_directory_exists,
    validate_file_extension,
    validate_positive_number,
    validate_array_parameter,
    validate_dict_parameter,
    validate_pattern_match
)

# 数据处理工具
from .data_utils import (
    generate_unique_id,
    format_timestamp,
    serialize_to_json,
    deserialize_from_json,
    normalize_path,
    format_bytes,
    flatten_dict,
    merge_dicts,
    sanitize_filename,
    create_pagination_metadata,
    paginate_list
)

# 错误处理工具
from .error_handler import (
    handle_errors,
    handle_api_errors,
    handle_db_errors,
    handle_vector_errors
)

__all__ = [
    # validation_utils
    'validate_string_parameter',
    'validate_file_exists',
    'validate_directory_exists',
    'validate_file_extension',
    'validate_positive_number',
    'validate_array_parameter',
    'validate_dict_parameter',
    'validate_pattern_match',
    
    # data_utils
    'generate_unique_id',
    'format_timestamp',
    'serialize_to_json',
    'deserialize_from_json',
    'normalize_path',
    'format_bytes',
    'flatten_dict',
    'merge_dicts',
    'sanitize_filename',
    'create_pagination_metadata',
    'paginate_list',
    
    # error_handler
    'handle_errors',
    'handle_api_errors',
    'handle_db_errors',
    'handle_vector_errors'
]