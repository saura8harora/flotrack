from fastapi import APIRouter, Depends

from app.services.analytics_service import get_analytics
from app.utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
async def analytics(user_id: str = Depends(get_current_user_id)):
    return await get_analytics(user_id)
