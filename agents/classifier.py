from __future__ import annotations

from models import ClassifiedEmail
from models import EmailMessage
from tools.openai_custom_client import OpenAICompatibleLLMClient
from typing import List


class EmailClassifierAgent:
    categories: List[str] = [
        "Newsfeed",
        "Promotion",
        "Social",
        "Finance",
        "Work",
        "Updates",
        "Personal",
        "Other",
    ]

    def __init__(self, llm_client: OpenAICompatibleLLMClient | None = None) -> None:
        self.llm_client = llm_client or OpenAICompatibleLLMClient.from_env()

    def run(self, email: EmailMessage) -> ClassifiedEmail:
        result = self.llm_client.classify_email(email=email, categories=self.categories)
        return ClassifiedEmail(
            email=email,
            category=result["category"],
            confidence=result["confidence"],
            reasons=result["reasons"],
        )
