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

class ModelSelectRequest(BaseModel):
    model_id: str = Field(..., description="目标模型标识，如 'LiquidAI/d1-omni-600M'、'MiniCPM5-2B-Jev' 或 'EdgeJev'")

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
    supports_modalities: list[str]
    decision_primitives: list[str]
    available_models: list[ModelItem]
