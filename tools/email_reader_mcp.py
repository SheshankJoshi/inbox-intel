from __future__ import annotations

import imaplib
import json
import os
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timezone
from email import message_from_bytes
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from models import EmailMessage


class BaseEmailReaderMCP(ABC):
    @abstractmethod
    def fetch_unread(self, limit: int = 25) -> list[EmailMessage]:
        raise NotImplementedError


class SampleEmailReaderMCP(BaseEmailReaderMCP):
    def __init__(self, sample_dir: str = "demo/sample_emails") -> None:
        self.sample_dir = Path(sample_dir)

    def fetch_unread(self, limit: int = 25) -> list[EmailMessage]:
        emails: list[EmailMessage] = []
        json_files = sorted(self.sample_dir.glob("*.json"))[:limit]
        for path in json_files:
            with path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            emails.append(
                EmailMessage(
                    sender=payload.get("sender", "unknown@example.com"),
                    subject=payload.get("subject", "(no subject)"),
                    timestamp=datetime.fromisoformat(
                        payload.get("timestamp", datetime.now(timezone.utc).isoformat())
                    ),
                    html=payload.get("html", ""),
                    text=payload.get("text", ""),
                    source_id=payload.get("id", path.stem),
                )
            )
        return emails


class ImapEmailReaderMCP(BaseEmailReaderMCP):
    def __init__(self) -> None:
        self.host = os.getenv("INBOX_INTEL_IMAP_HOST", "")
        self.port = int(os.getenv("INBOX_INTEL_IMAP_PORT", "993"))
        self.username = os.getenv("INBOX_INTEL_EMAIL_USERNAME", "")
        self.password = os.getenv("INBOX_INTEL_EMAIL_PASSWORD", "")
        self.mailbox = os.getenv("INBOX_INTEL_IMAP_MAILBOX", "INBOX")

    def fetch_unread(self, limit: int = 25) -> list[EmailMessage]:
        if not all([self.host, self.username, self.password]):
            raise ValueError("IMAP credentials are missing. Configure environment variables first.")

        conn = imaplib.IMAP4_SSL(self.host, self.port)
        try:
            conn.login(self.username, self.password)
            conn.select(self.mailbox)
            status, data = conn.search(None, "UNSEEN")
            if status != "OK":
                return []

            ids = (data[0] or b"").split()
            chosen_ids = ids[-limit:]
            emails: list[EmailMessage] = []
            for email_id in chosen_ids:
                message_id = email_id.decode("utf-8", errors="ignore")
                status, msg_data = conn.fetch(message_id, "(RFC822)")
                if status != "OK" or not msg_data or msg_data[0] is None:
                    continue

                row = msg_data[0]
                raw = row[1] if isinstance(row, tuple) and len(row) >= 2 else None
                if isinstance(raw, bytearray):
                    raw = bytes(raw)
                if raw is None:
                    continue

                msg = message_from_bytes(raw)
                emails.append(self._parse_email(msg, source_id=message_id))
            return emails
        finally:
            try:
                conn.close()
            except Exception:
                pass
            conn.logout()

    def _parse_email(self, msg: Message, source_id: str) -> EmailMessage:
        sender = msg.get("From", "unknown@example.com")
        subject = msg.get("Subject", "(no subject)")

        date_header = msg.get("Date")
        if date_header:
            try:
                timestamp = parsedate_to_datetime(date_header)
            except Exception:
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)

        html_content = ""
        text_content = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                if not isinstance(payload, (bytes, bytearray)):
                    continue
                decoded = payload.decode(charset, errors="ignore")
                if content_type == "text/html" and not html_content:
                    html_content = decoded
                elif content_type == "text/plain" and not text_content:
                    text_content = decoded
        else:
            payload_raw: Any = msg.get_payload(decode=True)
            if payload_raw is not None:
                charset = msg.get_content_charset() or "utf-8"
                if not isinstance(payload_raw, (bytes, bytearray)):
                    payload_raw = str(payload_raw).encode(charset, errors="ignore")
                decoded = payload_raw.decode(charset, errors="ignore")
                if msg.get_content_type() == "text/html":
                    html_content = decoded
                else:
                    text_content = decoded

        if not html_content and text_content:
            html_content = BeautifulSoup(text_content, "html.parser").prettify()

        return EmailMessage(
            sender=sender,
            subject=subject,
            timestamp=timestamp,
            html=html_content,
            text=text_content,
            source_id=source_id,
        )
