from __future__ import annotations

from models import ArticleLink
from models import EmailMessage
from tools.openai_custom_client import OpenAICompatibleLLMClient


class LinkExtractionAgent:
    def __init__(self, llm_client: OpenAICompatibleLLMClient | None = None) -> None:
        self.llm_client = llm_client or OpenAICompatibleLLMClient.from_env()

    def run(self, email: EmailMessage) -> list[ArticleLink]:
        links = self.llm_client.extract_article_links(email=email)
        return [ArticleLink(url=url, source_email_subject=email.subject) for url in links]
