from pydantic import BaseModel, Field


class ModelItem(BaseModel):
    id: str
    name: str
    provider: str
    architecture: str
    parameters: str
    description: str
    tags: list[str] = []
    recommended_for: str
    typical_latency_ms: str
    supports_vision: bool = False
    is_active: bool = False
    is_loaded: bool = False


class ModelSelectRequest(BaseModel):
    model_id: str = Field(..., description="目标模型标识，如 'LiquidAI/d1-omni-600M'、'ytbai/MiniCPM5-2B-Jev' 或 'EdgeJev'")


class CacheModeRequest(BaseModel):
    enabled: bool = Field(..., description="是否启用简单缓存（保留已加载模型权重，切换时不再重复载入）")


class ModelProgress(BaseModel):
    model_id: str
    state: str  # idle | preparing | downloading | loading | ready | error
    percent: float
    message: str = ""
    updated_at: float = 0.0


class ModelStatusResponse(BaseModel):
    model_id: str
    name: str
    architecture: str
    mode: str
    is_loaded: bool
    is_loading: bool
    device: str
    memory_mb: float
    load_error: str | None = None
    cache_enabled: bool = False
    loaded_models: list[str] = []
    progress: ModelProgress
    supports_modalities: list[str]
    decision_primitives: list[str]
    available_models: list[ModelItem]
