from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_admin
from app.schemas.model import ModelItem, ModelSelectRequest, ModelStatusResponse
from app.services.model_engine import model_engine

router = APIRouter(prefix="/model", tags=["Model Engine"], dependencies=[Depends(get_current_admin)])

@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status():
    """Returns runtime state of decision model engine, current active model, and available models."""
    return model_engine.get_status()

@router.get("/list", response_model=list[ModelItem])
async def list_available_models():
    """Returns all supported decision models (Liquid AI d1-omni-600M, MiniCPM5-2B-Jev, EdgeJev)."""
    return model_engine.get_available_models()

@router.post("/select", response_model=ModelStatusResponse)
async def switch_active_model(payload: ModelSelectRequest):
    """Switches the platform's active default decision model."""
    try:
        return model_engine.switch_model(payload.model_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/load")
async def load_model_weights(
    force: bool = False,
    model_id: Optional[str] = Query(None, description="Optional target model ID to load"),
):
    """Triggers loading real model weights from Hugging Face into memory."""
    result = await model_engine.load_real_model(force=force, model_id=model_id)
    return result

@router.post("/unload")
async def unload_model_weights():
    """Unloads model weights from memory to save resources."""
    model_engine.unload_model()
    return {"status": "unloaded", "mode": "simulation", "model_id": model_engine.model_id}
