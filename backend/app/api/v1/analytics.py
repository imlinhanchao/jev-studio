from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_admin
from app.schemas.analytics import AnalyticsDashboardData, UsageLogItem
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Token Consumption"], dependencies=[Depends(get_current_admin)])

@router.get("/dashboard", response_model=AnalyticsDashboardData)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Returns token consumption dashboard summary, timeseries, and key rankings."""
    return await AnalyticsService.get_dashboard_data(db)

@router.get("/logs", response_model=list[UsageLogItem])
async def get_usage_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    key_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Returns granular token usage audit logs."""
    return await AnalyticsService.get_logs(db, skip=skip, limit=limit, api_key_id=key_id)
