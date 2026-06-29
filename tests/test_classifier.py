from datetime import datetime
from datetime import timezone

from agents.classifier import EmailClassifierAgent
from models import EmailMessage


class _StubLLMClient:
    def classify_email(self, email: EmailMessage, categories: list[str]) -> dict[str, object]:
        return {"category": "Newsfeed", "confidence": 0.98, "reasons": ["stubbed"]}


def test_newsletter_classified_as_newsfeed() -> None:
    agent = EmailClassifierAgent(llm_client=_StubLLMClient()) # type: ignore
    email = EmailMessage(
        sender="sender@example.com",
        subject="Morning newsletter",
        timestamp=datetime.now(timezone.utc),
        html="<a href='https://example.com/news/story'>story</a>",
        text="Daily digest",
    )
    result = agent.run(email)
    assert result.category == "Newsfeed"
