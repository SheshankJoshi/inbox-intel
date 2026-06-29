from agents.metadata_agent import ArticleMetadataAgent


def test_fallback_metadata_when_fetch_fails() -> None:
    agent = ArticleMetadataAgent()
    meta = agent.run("https://example.invalid/news/item")
    assert meta.url == "https://example.invalid/news/item"
    assert meta.title
