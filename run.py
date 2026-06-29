from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from agents.classifier import EmailClassifierAgent
from agents.digest_builder import DigestBuilderAgent
from agents.email_ingestion import EmailIngestionAgent
from agents.link_extractor import LinkExtractionAgent
from agents.metadata_agent import ArticleMetadataAgent
from agents.publisher import PublisherAgent
from agents.supervisor import SupervisorAgent
from tools.email_reader_mcp import BaseEmailReaderMCP
from tools.email_reader_mcp import ImapEmailReaderMCP
from tools.email_reader_mcp import SampleEmailReaderMCP
from tools.openai_custom_client import LLMConfigurationError
from tools.openai_custom_client import OpenAICompatibleLLMClient


def build_supervisor(source: str, output_dir: str) -> SupervisorAgent:
    email_reader: BaseEmailReaderMCP
    llm_client = OpenAICompatibleLLMClient.from_env()
    if source == "imap":
        email_reader = ImapEmailReaderMCP()
    else:
        email_reader = SampleEmailReaderMCP()

    return SupervisorAgent(
        ingestion_agent=EmailIngestionAgent(email_reader=email_reader),
        classifier_agent=EmailClassifierAgent(llm_client=llm_client),
        link_extraction_agent=LinkExtractionAgent(llm_client=llm_client),
        metadata_agent=ArticleMetadataAgent(),
        digest_builder_agent=DigestBuilderAgent(),
        publisher_agent=PublisherAgent(output_dir=output_dir),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="InboxIntel autonomous newsfeed intelligence agent")
    parser.add_argument(
        "--source",
        choices=["sample", "imap"],
        default=os.getenv("INBOX_INTEL_SOURCE", "sample"),
        help="Email source to process",
    )
    parser.add_argument(
        "--max-emails",
        type=int,
        default=int(os.getenv("INBOX_INTEL_MAX_EMAILS", "25")),
        help="Max unread emails to process in one run",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where digest artifacts will be written",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start FastAPI server after digest generation",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("INBOX_INTEL_API_HOST", "127.0.0.1"),
        help="Host for the API server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("INBOX_INTEL_API_PORT", "8000")),
        help="Port for the API server",
    )
    return parser.parse_args()


def main() -> int:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

    args = parse_args()
    try:
        supervisor = build_supervisor(source=args.source, output_dir=args.output_dir)
    except LLMConfigurationError as exc:
        print(f"Configuration error: {exc}")
        print("Set INBOX_INTEL_OPENAI_BASE_URL, INBOX_INTEL_OPENAI_API_KEY, and INBOX_INTEL_OPENAI_MODEL.")
        return 2

    result = supervisor.run(source=args.source, limit=args.max_emails)

    print("InboxIntel run complete")
    print(f"Processed emails: {result.processed_email_count}")
    print(f"Newsfeed emails: {result.newsfeed_email_count}")
    print(f"Extracted links: {result.extracted_link_count}")
    print(f"Published JSON: {result.published_paths['json']}")
    print(f"Published Markdown: {result.published_paths['markdown']}")
    print(f"Published HTML: {result.published_paths['html']}")

    if args.serve:
        print(f"Starting API at http://{args.host}:{args.port}")
        PublisherAgent(output_dir=args.output_dir).serve(result.digest, host=args.host, port=args.port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
