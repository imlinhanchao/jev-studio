from typing import Any, Literal
from pydantic import BaseModel, Field

QuestionType = Literal["choice", "noul", "score"]

class QuestionDefinition(BaseModel):
    type: QuestionType = Field(
        ...,
        description="Type of decision question: 'choice' (unordered classes), 'noul' (binary yes/no), or 'score' (ordered rubric)"
    )
    instructions: str = Field(
        ...,
        description="Prompt instructions describing the decision criteria"
    )
    criteria: dict[str, str] | str | None = Field(
        default=None,
        description="For choice: dict mapping category keys to definitions; For noul/score: rubric description"
    )
    scale: int | None = Field(
        default=5,
        description="For score questions: maximum scale (e.g. 5, 10)"
    )

class DecisionRequest(BaseModel):
    input: str = Field(
        default="",
        description="Text content or structured input for the decision model to evaluate"
    )
    image: str | None = Field(
        default=None,
        description="Optional image URL or base64 data string for multimodal evaluation (supported by d1-omni-600M)"
    )
    questions: dict[str, QuestionDefinition] = Field(
        ...,
        description="Dictionary mapping question keys to question definitions"
    )
    model: str | None = Field(
        default=None,
        description="Optional decision model identifier (e.g. 'LiquidAI/d1-omni-600M', 'MiniCPM5-2B-Jev', or 'EdgeJev')"
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional tracking or user metadata"
    )

class UsageInfo(BaseModel):
    prompt_tokens: int
    decision_tokens: int
    total_tokens: int

class ChoiceAnswer(BaseModel):
    choice: str
    probabilities: dict[str, float]
    confidence: float

class NoulAnswer(BaseModel):
    decision: bool
    probability: float

class ScoreAnswer(BaseModel):
    score: int
    scale: int
    confidence: float

class DecisionResponse(BaseModel):
    id: str
    model: str
    engine: str  # "liquid-ai-d1-omni-600M" or "liquid-ai-calibrated-simulation"
    answers: dict[str, Any]
    usage: UsageInfo
    latency_ms: float
    created_at: str

class DecisionTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: str
    sample_input: str
    sample_image: str | None = None
    questions: dict[str, QuestionDefinition]
