from __future__ import annotations

from models import ArticleMetadata
from tools.http_fetch_mcp import HttpFetchMCP


class ArticleMetadataAgent:
    def __init__(self, http_tool: HttpFetchMCP | None = None) -> None:
        self.http_tool = http_tool or HttpFetchMCP()

    def run(self, url: str) -> ArticleMetadata:
        return self.http_tool.fetch_article_metadata(url)
