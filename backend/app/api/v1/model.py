from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_admin
from app.schemas.model import (
    CacheModeRequest,
    ModelItem,
    ModelProgress,
    ModelSelectRequest,
    ModelStatusResponse,
)
from app.services.model_engine import model_engine

router = APIRouter(prefix="/model", tags=["Model Engine"], dependencies=[Depends(get_current_admin)])

@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status():
    """Returns runtime state of decision model engine, current active model, and available models."""
    return model_engine.get_status()

@router.get("/progress", response_model=ModelProgress)
async def get_model_progress():
    """Returns the current model loading progress (state, percent, message)."""
    return model_engine.get_progress()

@router.get("/list", response_model=list[ModelItem])
async def list_available_models():
    """Returns all supported decision models (Liquid AI d1-omni-600M, ytbai/MiniCPM5-2B-Jev, EdgeJev)."""
    return model_engine.get_available_models()

@router.post("/select", response_model=ModelStatusResponse)
async def switch_active_model(payload: ModelSelectRequest):
    """Switches the platform's active default decision model."""
    try:
        return await model_engine.switch_model(payload.model_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/cache-mode", response_model=ModelStatusResponse)
async def set_cache_mode(payload: CacheModeRequest):
    """Enables/disables simple caching. Disabling unloads every non-active cached model."""
    return await model_engine.set_cache_mode(payload.enabled)

@router.post("/load")
async def load_model_weights(
    force: bool = False,
    model_id: Optional[str] = Query(None, description="Optional target model ID to load"),
):
    """Triggers loading real model weights into memory."""
    result = await model_engine.load_real_model(force=force, model_id=model_id)
    return result

@router.post("/unload")
async def unload_model_weights(
    model_id: Optional[str] = Query(None, description="Optional cached model ID to unload; omit to unload all"),
):
    """Unloads a cached model's weights (or all models) from memory to save resources."""
    if model_id:
        await model_engine.unload_cached_model(model_id)
    else:
        model_engine.unload_model()
    return {
        "status": "unloaded",
        "mode": model_engine.mode,
        "model_id": model_engine.model_id,
        "loaded_models": list(model_engine.loaded_models.keys()),
    }
