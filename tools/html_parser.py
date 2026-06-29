from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup


class HtmlParserTool:
    def extract_links(self, html: str) -> list[str]:
        soup = BeautifulSoup(html or "", "html.parser")
        urls: list[str] = []
        for anchor in soup.find_all("a", href=True):
            # pyrefly: ignore [missing-attribute]
            href = (anchor.get("href") or "").strip()
            if href:
                urls.append(href)
        return urls

    def normalize_and_filter_article_links(self, urls: list[str]) -> list[str]:
        article_like_keywords = (
            "news",
            "article",
            "story",
            "insight",
            "blog",
            "press",
            "update",
            "market",
            "finance",
            "tech",
            "economy",
            "analysis",
        )

        filtered: list[str] = []
        seen: set[str] = set()

        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                continue
            normalized = parsed._replace(fragment="").geturl()
            low = normalized.lower()
            if any(k in low for k in article_like_keywords):
                if normalized not in seen:
                    seen.add(normalized)
                    filtered.append(normalized)
        return filtered
