"""健康检查API路由"""
from fastapi import APIRouter
from app.models.pydantic_models import BaseResponse

# 创建健康检查API路由
router = APIRouter(prefix='/api')

# 健康检查端点
@router.get('/health', response_model=BaseResponse[dict])
def health_check():
    """健康检查端点"""
    return BaseResponse(
        data={"status": "ok"},
        message="服务健康"
    )
