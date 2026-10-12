from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.decision import router as decision_router
from app.api.v1.keys import router as keys_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.model import router as model_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(decision_router)
api_v1_router.include_router(keys_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(model_router)
