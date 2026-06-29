from __future__ import annotations

from datetime import datetime
from datetime import timezone

from models import ArticleMetadata
from models import DailyDigest


class DigestBuilderAgent:
    def run(self, source: str, articles: list[ArticleMetadata]) -> DailyDigest:
        now = datetime.now(timezone.utc)
        return DailyDigest(
            email_date=now.date().isoformat(),
            source=source,
            generated_at=now.isoformat().replace("+00:00", "Z"),
            articles=articles,
        )
