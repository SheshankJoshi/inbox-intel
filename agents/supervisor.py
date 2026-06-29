from __future__ import annotations

from dataclasses import dataclass

from agents.classifier import EmailClassifierAgent
from agents.digest_builder import DigestBuilderAgent
from agents.email_ingestion import EmailIngestionAgent
from agents.link_extractor import LinkExtractionAgent
from agents.metadata_agent import ArticleMetadataAgent
from agents.publisher import PublisherAgent
from models import ArticleMetadata
from models import DailyDigest


@dataclass(slots=True)
class SupervisorRunResult:
    digest: DailyDigest
    published_paths: dict[str, str]
    processed_email_count: int
    newsfeed_email_count: int
    extracted_link_count: int


class SupervisorAgent:
    def __init__(
        self,
        ingestion_agent: EmailIngestionAgent,
        classifier_agent: EmailClassifierAgent,
        link_extraction_agent: LinkExtractionAgent,
        metadata_agent: ArticleMetadataAgent,
        digest_builder_agent: DigestBuilderAgent,
        publisher_agent: PublisherAgent,
    ) -> None:
        self.ingestion_agent = ingestion_agent
        self.classifier_agent = classifier_agent
        self.link_extraction_agent = link_extraction_agent
        self.metadata_agent = metadata_agent
        self.digest_builder_agent = digest_builder_agent
        self.publisher_agent = publisher_agent

    def run(self, source: str, limit: int = 25) -> SupervisorRunResult:
        emails = self.ingestion_agent.run(limit=limit)

        all_articles: list[ArticleMetadata] = []
        newsfeed_count = 0
        extracted_link_count = 0

        for email in emails:
            classified = self.classifier_agent.run(email)
            if classified.category != "Newsfeed":
                continue

            newsfeed_count += 1
            links = self.link_extraction_agent.run(email)
            extracted_link_count += len(links)

            for link in links:
                article = self.metadata_agent.run(link.url)
                all_articles.append(article)

        deduped_articles = self._dedupe_articles(all_articles)
        digest = self.digest_builder_agent.run(source=source, articles=deduped_articles)
        published_paths = self.publisher_agent.publish(digest)

        return SupervisorRunResult(
            digest=digest,
            published_paths=published_paths,
            processed_email_count=len(emails),
            newsfeed_email_count=newsfeed_count,
            extracted_link_count=extracted_link_count,
        )

    def _dedupe_articles(self, articles: list[ArticleMetadata]) -> list[ArticleMetadata]:
        seen: set[str] = set()
        unique: list[ArticleMetadata] = []
        for article in articles:
            if article.url in seen:
                continue
            seen.add(article.url)
            unique.append(article)
        return unique
