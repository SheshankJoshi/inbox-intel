from __future__ import annotations

from models import EmailMessage
from tools.email_reader_mcp import BaseEmailReaderMCP


class EmailIngestionAgent:
    def __init__(self, email_reader: BaseEmailReaderMCP) -> None:
        self.email_reader = email_reader

    def run(self, limit: int = 25) -> list[EmailMessage]:
        return self.email_reader.fetch_unread(limit=limit)
