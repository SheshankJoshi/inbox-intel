from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class EmailMessage:
    sender: str
    subject: str
    timestamp: datetime
    html: str
    text: str = ""
    source_id: str = ""


@dataclass(slots=True)
class ClassifiedEmail:
    email: EmailMessage
    category: str
    confidence: float
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ArticleLink:
    url: str
    source_email_subject: str


@dataclass(slots=True)
class ArticleMetadata:
    title: str
    url: str
    publisher: str
    description: str = ""
    summary: str = ""
    published_at: str = ""


@dataclass(slots=True)
class DailyDigest:
    email_date: str
    source: str
    generated_at: str
    articles: list[ArticleMetadata]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["articles"] = [asdict(article) for article in self.articles]
        return payload
