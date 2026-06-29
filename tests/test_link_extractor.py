from datetime import datetime
from datetime import timezone

from agents.link_extractor import LinkExtractionAgent
from models import EmailMessage


class _StubLLMClient:
    def extract_article_links(self, email: EmailMessage) -> list[str]:
        return ["https://example.com/news/story-1"]


def test_extracts_article_links() -> None:
    agent = LinkExtractionAgent(llm_client=_StubLLMClient())
    email = EmailMessage(
        sender="sender@example.com",
        subject="Digest",
        timestamp=datetime.now(timezone.utc),
        html="<a href='https://example.com/news/story-1'>A</a><a href='https://example.com/about'>B</a>",
    )

    links = agent.run(email)
    assert len(links) == 1
    assert links[0].url == "https://example.com/news/story-1"
