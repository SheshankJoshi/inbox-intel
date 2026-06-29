from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
import yaml

from models import EmailMessage
from schemas.llm_outputs import ClassificationResult
from schemas.llm_outputs import ExtractionResult


class LLMConfigurationError(Exception):
    pass


class LLMResponseError(Exception):
    pass


@dataclass(slots=True)
class OpenAICompatibleConfig:
    base_url: str
    api_key: str
    model: str
    chat_path: str = "/v1/chat/completions"
    timeout_seconds: int = 45
    key_header: str = "Authorization"
    key_prefix: str = "Bearer"
    prompts_file: str = "prompts/llm_prompts.yaml"

    @classmethod
    def from_env(cls) -> "OpenAICompatibleConfig":
        base_url = os.getenv("INBOX_INTEL_OPENAI_BASE_URL", "").strip()
        api_key = os.getenv("INBOX_INTEL_OPENAI_API_KEY", "").strip()
        model = os.getenv("INBOX_INTEL_OPENAI_MODEL", "").strip()

        if not base_url:
            raise LLMConfigurationError("Missing INBOX_INTEL_OPENAI_BASE_URL")
        if not api_key:
            raise LLMConfigurationError("Missing INBOX_INTEL_OPENAI_API_KEY")
        if not model:
            raise LLMConfigurationError("Missing INBOX_INTEL_OPENAI_MODEL")

        timeout_seconds = int(os.getenv("INBOX_INTEL_OPENAI_TIMEOUT_SECONDS", "45"))
        chat_path = os.getenv("INBOX_INTEL_OPENAI_CHAT_PATH", "/v1/chat/completions").strip() or "/v1/chat/completions"
        key_header = os.getenv("INBOX_INTEL_OPENAI_KEY_HEADER", "Authorization").strip() or "Authorization"
        key_prefix = os.getenv("INBOX_INTEL_OPENAI_KEY_PREFIX", "Bearer").strip()
        prompts_file = os.getenv("INBOX_INTEL_PROMPTS_FILE", "prompts/llm_prompts.yaml").strip() or "prompts/llm_prompts.yaml"

        return cls(
            base_url=base_url,
            api_key=api_key,
            model=model,
            chat_path=chat_path,
            timeout_seconds=timeout_seconds,
            key_header=key_header,
            key_prefix=key_prefix,
            prompts_file=prompts_file,
        )


class OpenAICompatibleLLMClient:
    def __init__(self, config: OpenAICompatibleConfig) -> None:
        self.config = config
        self.prompts = self._load_prompts(config.prompts_file)

    @classmethod
    def from_env(cls) -> "OpenAICompatibleLLMClient":
        return cls(config=OpenAICompatibleConfig.from_env())

    def classify_email(self, email: EmailMessage, categories: list[str]) -> dict[str, Any]:
        prompt = self._build_classification_prompt(email=email, categories=categories)
        result = self._ask_json(prompt)
        parsed = ClassificationResult.model_validate(result)

        category = parsed.category.strip()
        if category not in categories:
            category = "Other"

        confidence_float = float(parsed.confidence)
        confidence_float = max(0.0, min(1.0, confidence_float))

        reasons = [item.strip() for item in parsed.reasons if item.strip()]
        if not reasons:
            reasons = ["LLM classification result"]

        return {
            "category": category,
            "confidence": confidence_float,
            "reasons": reasons,
        }

    def extract_article_links(self, email: EmailMessage) -> list[str]:
        prompt = self._build_extraction_prompt(email=email)
        result = self._ask_json(prompt)
        parsed = ExtractionResult.model_validate(result)
        links = parsed.links

        normalized: list[str] = []
        seen: set[str] = set()
        for link in links:
            url = str(link).strip()
            if not url.lower().startswith(("http://", "https://")):
                continue
            if url not in seen:
                seen.add(url)
                normalized.append(url)
        return normalized

    def _ask_json(self, user_prompt: str) -> dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": self.prompts["system_prompt"],
            },
            {"role": "user", "content": user_prompt},
        ]

        url = urljoin(self.config.base_url.rstrip("/") + "/", self.config.chat_path.lstrip("/"))
        headers = {
            "Content-Type": "application/json",
            self.config.key_header: self._build_auth_value(),
        }
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout_seconds)
        if response.status_code >= 400:
            raise LLMResponseError(f"LLM request failed ({response.status_code}): {response.text[:300]}")

        response_json = response.json()
        content = self._extract_message_content(response_json)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = json.loads(self._extract_first_json_object(content))

        if not isinstance(parsed, dict):
            raise LLMResponseError("LLM output is not a JSON object")
        return parsed

    def _extract_message_content(self, response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices", [])
        if not choices:
            raise LLMResponseError("LLM response has no choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(str(part.get("text", "")))
            joined = "".join(text_parts).strip()
            if joined:
                return joined

        raise LLMResponseError("Unable to extract text content from LLM response")

    def _extract_first_json_object(self, text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMResponseError("No JSON object found in LLM output")
        return text[start : end + 1]

    def _build_auth_value(self) -> str:
        if self.config.key_prefix:
            return f"{self.config.key_prefix} {self.config.api_key}"
        return self.config.api_key

    def _build_classification_prompt(self, email: EmailMessage, categories: list[str]) -> str:
        return self.prompts["classification_prompt"].format(
            categories=", ".join(categories),
            output_schema=ClassificationResult.structured_output_text(),
            sender=email.sender,
            subject=email.subject,
            timestamp=email.timestamp.isoformat(),
            text_body=self._truncate(email.text, 6000),
            html_body=self._truncate(email.html, 12000),
        )

    def _build_extraction_prompt(self, email: EmailMessage) -> str:
        return self.prompts["extraction_prompt"].format(
            output_schema=ExtractionResult.structured_output_text(),
            sender=email.sender,
            subject=email.subject,
            timestamp=email.timestamp.isoformat(),
            text_body=self._truncate(email.text, 6000),
            html_body=self._truncate(email.html, 14000),
        )

    def _load_prompts(self, prompts_file: str) -> dict[str, str]:
        root = Path(__file__).resolve().parents[1]
        path = root / prompts_file
        if not path.exists():
            raise LLMConfigurationError(f"Prompt file not found: {path}")

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise LLMConfigurationError("Prompt YAML must be a mapping")

        required = {"system_prompt", "classification_prompt", "extraction_prompt"}
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise LLMConfigurationError(f"Prompt YAML missing keys: {', '.join(missing)}")

        return {
            "system_prompt": str(data["system_prompt"]),
            "classification_prompt": str(data["classification_prompt"]),
            "extraction_prompt": str(data["extraction_prompt"]),
        }

    def _truncate(self, text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        return text[:max_len] + "\n...[truncated]"
