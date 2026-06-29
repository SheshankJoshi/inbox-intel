from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from bs4 import Tag

from models import ArticleMetadata


class HttpFetchMCP:
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def fetch_article_metadata(self, url: str) -> ArticleMetadata:
        try:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "InboxIntel/1.0"})
            response.raise_for_status()
        except Exception:
            return ArticleMetadata(
                title=self._fallback_title(url),
                url=url,
                publisher=self._publisher_from_url(url),
                summary="Unable to fetch this page during processing.",
            )

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._meta_or_default(
            soup,
            [
                ("property", "og:title"),
                ("name", "twitter:title"),
            ],
            default=(soup.title.string.strip() if soup.title and soup.title.string else self._fallback_title(url)),
        )
        description = self._meta_or_default(
            soup,
            [
                ("property", "og:description"),
                ("name", "description"),
            ],
            default="",
        )
        published_at = self._meta_or_default(
            soup,
            [
                ("property", "article:published_time"),
                ("name", "pubdate"),
            ],
            default="",
        )
        publisher = self._meta_or_default(
            soup,
            [
                ("property", "og:site_name"),
                ("name", "publisher"),
            ],
            default=self._publisher_from_url(url),
        )

        summary = self._summarize(description, title)

        return ArticleMetadata(
            title=title,
            url=url,
            publisher=publisher,
            description=description,
            summary=summary,
            published_at=published_at,
        )

    def _meta_or_default(
        self,
        soup: BeautifulSoup,
        selectors: list[tuple[str, str]],
        default: str,
    ) -> str:
        for key, value in selectors:
            tag = soup.find("meta", attrs={key: value})
            if isinstance(tag, Tag) and tag.get("content"):
                return str(tag.get("content")).strip()
        return default

    def _publisher_from_url(self, url: str) -> str:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "")

    def _fallback_title(self, url: str) -> str:
        path = urlparse(url).path.strip("/")
        if not path:
            return url
        return path.split("/")[-1].replace("-", " ").title()

    def _summarize(self, description: str, title: str) -> str:
        text = description.strip() or f"Article about {title}."
        if len(text) <= 220:
            return text
        return text[:217] + "..."
