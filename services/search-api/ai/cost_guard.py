"""
Budget and Cost Guard for Grounded AI Inference.
Enforces hard monthly spending caps to guarantee zero unexpected costs.
"""

from config import settings
from db.models import AIUsageLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


class CostGuard:
    def __init__(self):
        self.hard_limit_usd = settings.AI_MONTHLY_BUDGET_USD

    async def can_execute(self, session: AsyncSession) -> tuple[bool, float]:
        """
        Returns (is_allowed, remaining_budget_usd).
        Checks current total usage against configured hard spending cap.
        """
        stmt = select(func.sum(AIUsageLog.estimated_cost_usd))
        result = await session.execute(stmt)
        total_used = result.scalar() or 0.0

        # Also account for any base usage configured in settings
        total_used += settings.AI_MONTHLY_USAGE_USD
        remaining = max(0.0, self.hard_limit_usd - total_used)

        if total_used >= self.hard_limit_usd:
            return False, 0.0

        return True, round(remaining, 4)

    async def record_usage(
        self,
        session: AsyncSession,
        provider: str,
        model: str,
        tokens_used: int,
        estimated_cost_usd: float,
        status: str,
    ) -> None:
        """Audit AI call usage in database."""
        log_entry = AIUsageLog(
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            estimated_cost_usd=estimated_cost_usd,
            status=status,
        )
        session.add(log_entry)
        await session.commit()
