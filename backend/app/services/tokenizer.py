import json
from typing import Any
import tiktoken
from app.schemas.decision import QuestionDefinition

try:
    _encoder = tiktoken.get_encoding("cl100k_base")
except Exception:
    _encoder = None

def count_text_tokens(text: str) -> int:
    """Counts tokens in a string using tiktoken or fallback heuristic."""
    if not text:
        return 0
    if _encoder is not None:
        try:
            return len(_encoder.encode(text))
        except Exception:
            pass
    # Fallback approximation: ~1 token per 3.5 chars for mixed English/Chinese
    return max(1, int(len(text) / 3.5))

def calculate_decision_tokens(
    input_text: str,
    questions: dict[str, QuestionDefinition],
    has_image: bool = False
) -> tuple[int, int, int]:
    """
    Calculates token consumption for a Liquid AI decision model evaluation:
    - prompt_tokens: tokens in the input context + question instructions and criteria + visual tokens
    - decision_tokens: compute cost of evaluating structured decision heads (calibrated classification tokens)
    - total_tokens: sum of prompt and decision tokens
    """
    # 1. Input tokens (text tokens + multimodal vision patch tokens if image is provided)
    prompt_tokens = count_text_tokens(input_text)
    if has_image:
        prompt_tokens += 128
    
    # 2. Schema tokens (instructions, choices, criteria)
    schema_tokens = 0
    decision_tokens = 0
    
    for q_key, q_def in questions.items():
        # Instruction tokens
        schema_tokens += count_text_tokens(q_key)
        schema_tokens += count_text_tokens(q_def.instructions)
        
        # Criteria tokens
        if isinstance(q_def.criteria, dict):
            for opt_key, opt_desc in q_def.criteria.items():
                schema_tokens += count_text_tokens(opt_key) + count_text_tokens(opt_desc)
        elif isinstance(q_def.criteria, str):
            schema_tokens += count_text_tokens(q_def.criteria)
            
        # Decision token allocation per primitive
        if q_def.type == "choice":
            # Choice questions evaluate logits across N options
            num_choices = len(q_def.criteria) if isinstance(q_def.criteria, dict) else 2
            decision_tokens += max(4, num_choices * 2)
        elif q_def.type == "noul":
            # Noul (binary yes/no) evaluation
            decision_tokens += 4
        elif q_def.type == "score":
            # Score rubric projection
            scale = q_def.scale or 5
            decision_tokens += max(4, scale)
            
    total_prompt_tokens = prompt_tokens + schema_tokens
    # Minimum baseline of 1 decision token
    decision_tokens = max(1, decision_tokens)
    total_tokens = total_prompt_tokens + decision_tokens
    
    return total_prompt_tokens, decision_tokens, total_tokens
