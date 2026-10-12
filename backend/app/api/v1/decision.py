import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_api_key
from app.db.models import APIKey
from app.schemas.decision import (
    DecisionRequest,
    DecisionResponse,
    DecisionTemplate,
    UsageInfo,
    QuestionDefinition,
)
from app.services.model_engine import model_engine
from app.services.tokenizer import calculate_decision_tokens
from app.services.key_service import KeyService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/decision", tags=["Decision Model"])

PREDEFINED_TEMPLATES = [
    DecisionTemplate(
        id="support-routing",
        name="智能工单路由与分类",
        category="Customer Support",
        description="基于 Liquid AI 单步前向传播对客服工单进行多维度意图分类、紧急程度判定与复杂度打分",
        sample_input="我们的生产环境集群在刚刚的部署中全部中断了，所有用户无法访问支付接口，请立即协助排查并处理！",
        questions={
            "intent": QuestionDefinition(
                type="choice",
                instructions="判断该工单的主要诉求分类",
                criteria={
                    "infrastructure": "服务器、集群或网络基础设施故障",
                    "billing": "账单、退款或订阅付款问题",
                    "general": "常规咨询、功能建议或使用指导",
                },
            ),
            "is_critical": QuestionDefinition(
                type="noul",
                instructions="该问题是否属于阻断核心业务的严重故障？",
                criteria="系统完全不可用、服务大面积中断或资金安全风险",
            ),
            "urgency_score": QuestionDefinition(
                type="score",
                instructions="评估该事件的紧急响应优先级 (1=低, 5=最高)",
                scale=5,
            ),
        },
    ),
    DecisionTemplate(
        id="content-safety",
        name="内容安全与护栏 (Guardrails)",
        category="Safety & Compliance",
        description="对用户输入或大模型输出进行内容审核、越狱检测及合规风险评级",
        sample_input="请帮我编写一个脚本，用来自动测试我们的防火墙对大量并发探测请求的防护能力。",
        questions={
            "policy_violation": QuestionDefinition(
                type="noul",
                instructions="该输入是否存在明显的恶意攻击、违规或安全政策违例意图？",
                criteria="包含系统破解、恶意渗透或非法数据窃取",
            ),
            "topic_type": QuestionDefinition(
                type="choice",
                instructions="判断主题类别",
                criteria={
                    "security_testing": "合法的网络安全与防护测试",
                    "malicious_intent": "针对未经授权系统的恶意攻击",
                    "educational": "网络安全原理教学与概念探讨",
                },
            ),
            "risk_rating": QuestionDefinition(
                type="score",
                instructions="评估潜在风险等级 (1-5)",
                scale=5,
            ),
        },
    ),
    DecisionTemplate(
        id="lead-qualification",
        name="销售线索评估与意向分级",
        category="Sales & CRM",
        description="自动分析潜在企业客户咨询文本，判断购买意向阶段及预算匹配度",
        sample_input="我们是一家拥有 500 名工程师的科技公司，计划在下季度为全员采购企业级 AI 决策模型 API 服务，需要商务团队提供报价单并支持私有化部署测试。",
        questions={
            "stage": QuestionDefinition(
                type="choice",
                instructions="判断销售线索所处的生命周期阶段",
                criteria={
                    "procurement_ready": "具备明确采购预算与时间表，准备签约",
                    "solution_eval": "对比竞品评估阶段，了解技术特性",
                    "exploratory": "初期了解，暂无明确采购计划",
                },
            ),
            "is_enterprise_scale": QuestionDefinition(
                type="noul",
                instructions="该客户是否具备大型企业采购特征？",
                criteria="规模 200 人以上或提出私有化定制部署诉求",
            ),
            "intent_score": QuestionDefinition(
                type="score",
                instructions="综合购买意向评级 (1-5)",
                scale=5,
            ),
        },
    ),
    DecisionTemplate(
        id="animal-vision",
        name="多模态动物识别与特征决策",
        category="Multimodal Vision",
        description="基于 Liquid AI 原生多模态视觉单步推理，对图像中的生物进行物种判定、食性分类及危害度评估",
        sample_input="我需要知道关于这只动物的信息",
        sample_image="https://tse1-mm.cn.bing.net/th/id/OIP-C.LS_T9sXWOLjaDoXqjat2_gHaE8",
        questions={
            "intent": QuestionDefinition(
                type="choice",
                instructions="这是什么动物",
                criteria={
                    "infrastructure": "猫",
                    "billing": "鸡",
                    "general": "狗",
                },
            ),
            "is_critical": QuestionDefinition(
                type="noul",
                instructions="这是食草动物吗？",
                criteria="是食草动物",
            ),
            "urgency_score": QuestionDefinition(
                type="score",
                instructions="这只动物对人类的危害程度",
                scale=5,
            ),
        },
    ),
]

@router.get("/templates", response_model=list[DecisionTemplate])
async def list_templates():
    """Returns predefined decision question templates for quick testing."""
    return PREDEFINED_TEMPLATES

@router.post("/predict", response_model=DecisionResponse)
async def predict_decision(
    payload: DecisionRequest,
    request: Request,
    api_key: Optional[APIKey] = Depends(get_optional_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates input text against defined decision questions using Liquid AI d1-omni-600M.
    Deducts token quota and tracks usage statistics.
    """
    if not payload.questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one decision question must be specified.",
        )

    if not payload.input.strip() and not payload.image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either input text or an image must be provided.",
        )

    # 1. Calculate tokens (including visual tokens if multimodal image provided)
    prompt_tokens, decision_tokens, total_tokens = calculate_decision_tokens(
        payload.input, payload.questions, has_image=bool(payload.image)
    )

    # 2. Quota check
    if api_key:
        if not api_key.has_quota(total_tokens):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Insufficient token quota. Required: {total_tokens}, Remaining: {api_key.token_limit - api_key.tokens_used}",
            )

    # 3. Model Inference (Liquid AI d1-omni-600M or MiniCPM5-2B-Jev)
    request_id = f"dec_{uuid.uuid4().hex[:12]}"
    target_model_id = payload.model or model_engine.model_id
    answers, latency_ms, engine_name = await model_engine.predict(
        payload.input, payload.questions, model_id=payload.model, image=payload.image
    )

    # 4. Token deduction & Usage logging
    types_list = [q.type for q in payload.questions.values()]
    types_str = ",".join(types_list)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if api_key:
        await KeyService.increment_usage(db, api_key.id, total_tokens)

    await AnalyticsService.log_request(
        db=db,
        request_id=request_id,
        api_key_id=api_key.id if api_key else None,
        endpoint="/api/v1/decision/predict",
        decision_types=types_str,
        input_length=len(payload.input),
        prompt_tokens=prompt_tokens,
        decision_tokens=decision_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        status_code=200,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    return DecisionResponse(
        id=request_id,
        model=target_model_id,
        engine=engine_name,
        answers=answers,
        usage=UsageInfo(
            prompt_tokens=prompt_tokens,
            decision_tokens=decision_tokens,
            total_tokens=total_tokens,
        ),
        latency_ms=latency_ms,
        created_at=datetime.utcnow().isoformat() + "Z",
    )
