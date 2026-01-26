"""健康检查API路由"""
from fastapi import APIRouter

# 创建健康检查API路由
router = APIRouter(prefix='/api')

# 健康检查端点
@router.get('/health')
def health_check():
    """健康检查端点"""
    return {"status": "ok"}
