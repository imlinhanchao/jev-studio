from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TokenUsageLog, APIKey
from app.schemas.analytics import (
    SummaryStats,
    TimeSeriesPoint,
    DecisionTypeDistribution,
    KeyUsageItem,
    UsageLogItem,
    AnalyticsDashboardData,
)

class AnalyticsService:
    @staticmethod
    async def log_request(
        db: AsyncSession,
        request_id: str,
        api_key_id: Optional[int],
        endpoint: str,
        decision_types: str,
        input_length: int,
        prompt_tokens: int,
        decision_tokens: int,
        total_tokens: int,
        latency_ms: float,
        status_code: int = 200,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenUsageLog:
        log_entry = TokenUsageLog(
            request_id=request_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            decision_types=decision_types,
            input_length=input_length,
            prompt_tokens=prompt_tokens,
            decision_tokens=decision_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log_entry)
        await db.flush()
        return log_entry

    @staticmethod
    async def get_dashboard_data(db: AsyncSession) -> AnalyticsDashboardData:
        # 1. Summary Metrics
        summary_query = select(
            func.count(TokenUsageLog.id).label("total_requests"),
            func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(TokenUsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(TokenUsageLog.decision_tokens), 0).label("decision_tokens"),
            func.coalesce(func.avg(TokenUsageLog.latency_ms), 0.0).label("avg_latency"),
        )
        summary_row = (await db.execute(summary_query)).one()

        # Key counts
        keys_count_query = select(
            func.count(APIKey.id).label("total_keys"),
            func.coalesce(func.sum(case((APIKey.is_active == True, 1), else_=0)), 0).label("active_keys")
        )
        keys_row = (await db.execute(keys_count_query)).one()

        summary = SummaryStats(
            total_requests=summary_row.total_requests or 0,
            total_tokens=int(summary_row.total_tokens or 0),
            prompt_tokens=int(summary_row.prompt_tokens or 0),
            decision_tokens=int(summary_row.decision_tokens or 0),
            avg_latency_ms=round(float(summary_row.avg_latency or 0.0), 2),
            active_keys_count=int(keys_row.active_keys or 0),
            total_keys_count=int(keys_row.total_keys or 0),
        )

        # 2. Time series (last 7 days grouped by date)
        # Using date formatting in sqlite: strftime('%Y-%m-%d', created_at)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        ts_query = (
            select(
                func.strftime("%Y-%m-%d", TokenUsageLog.created_at).label("day"),
                func.count(TokenUsageLog.id).label("reqs"),
                func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("toks"),
                func.coalesce(func.avg(TokenUsageLog.latency_ms), 0.0).label("lat"),
            )
            .where(TokenUsageLog.created_at >= seven_days_ago)
            .group_by("day")
            .order_by("day")
        )
        ts_rows = (await db.execute(ts_query)).all()
        timeseries = [
            TimeSeriesPoint(
                date=row.day,
                requests=row.reqs,
                tokens=int(row.toks),
                avg_latency_ms=round(float(row.lat), 2),
            )
            for row in ts_rows
        ]
        
        # If empty, provide today's date placeholder
        if not timeseries:
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            timeseries.append(TimeSeriesPoint(date=today_str, requests=0, tokens=0, avg_latency_ms=0.0))

        # 3. Decision Type Distribution
        all_logs = (await db.execute(select(TokenUsageLog.decision_types))).scalars().all()
        choice_cnt = 0
        noul_cnt = 0
        score_cnt = 0
        for dt_str in all_logs:
            types = [t.strip().lower() for t in dt_str.split(",") if t.strip()]
            for t in types:
                if "choice" in t:
                    choice_cnt += 1
                elif "noul" in t:
                    noul_cnt += 1
                elif "score" in t:
                    score_cnt += 1

        type_distribution = DecisionTypeDistribution(
            choice=choice_cnt,
            noul=noul_cnt,
            score=score_cnt,
        )

        # 4. Key Usage Breakdown
        key_usage_query = (
            select(
                APIKey.id,
                APIKey.name,
                APIKey.key_prefix,
                APIKey.tokens_used,
                APIKey.token_limit,
                APIKey.is_active,
                func.count(TokenUsageLog.id).label("req_count"),
            )
            .outerjoin(TokenUsageLog, TokenUsageLog.api_key_id == APIKey.id)
            .group_by(APIKey.id)
            .order_by(desc(APIKey.tokens_used))
            .limit(10)
        )
        key_rows = (await db.execute(key_usage_query)).all()
        
        key_usage: list[KeyUsageItem] = []
        for kr in key_rows:
            pct = 0.0
            if kr.token_limit > 0:
                pct = round(min(100.0, (kr.tokens_used / kr.token_limit) * 100), 2)
            key_usage.append(
                KeyUsageItem(
                    key_id=kr.id,
                    name=kr.name,
                    key_prefix=kr.key_prefix,
                    tokens_used=kr.tokens_used,
                    token_limit=kr.token_limit,
                    percent_used=pct,
                    requests_count=kr.req_count or 0,
                    is_active=kr.is_active,
                )
            )

        return AnalyticsDashboardData(
            summary=summary,
            timeseries=timeseries,
            type_distribution=type_distribution,
            key_usage=key_usage,
        )

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        api_key_id: Optional[int] = None
    ) -> list[UsageLogItem]:
        query = (
            select(
                TokenUsageLog.id,
                TokenUsageLog.request_id,
                TokenUsageLog.api_key_id,
                APIKey.name.label("key_name"),
                APIKey.key_prefix.label("key_prefix"),
                TokenUsageLog.decision_types,
                TokenUsageLog.prompt_tokens,
                TokenUsageLog.decision_tokens,
                TokenUsageLog.total_tokens,
                TokenUsageLog.latency_ms,
                TokenUsageLog.status_code,
                TokenUsageLog.created_at,
            )
            .outerjoin(APIKey, TokenUsageLog.api_key_id == APIKey.id)
            .order_by(desc(TokenUsageLog.created_at))
        )
        if api_key_id is not None:
            query = query.where(TokenUsageLog.api_key_id == api_key_id)

        query = query.offset(skip).limit(limit)
        rows = (await db.execute(query)).all()

        return [
            UsageLogItem(
                id=r.id,
                request_id=r.request_id,
                key_id=r.api_key_id,
                key_name=r.key_name,
                key_prefix=r.key_prefix,
                decision_types=r.decision_types,
                prompt_tokens=r.prompt_tokens,
                decision_tokens=r.decision_tokens,
                total_tokens=r.total_tokens,
                latency_ms=round(r.latency_ms, 2),
                status_code=r.status_code,
                created_at=r.created_at,
            )
            for r in rows
        ]
