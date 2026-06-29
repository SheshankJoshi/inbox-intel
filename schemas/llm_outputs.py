from __future__ import annotations

import json

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class LLMOutputBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def structured_output_text(cls) -> str:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        lines = ["JSON object with fields:"]
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type", "any")
            description = field_schema.get("description", "")
            required_text = "required" if field_name in required else "optional"
            lines.append(f"- {field_name} ({field_type}, {required_text}): {description}")

        lines.append("Example JSON:")
        lines.append(json.dumps(cls.model_json_schema().get("examples", [{}])[0], indent=2))
        return "\n".join(lines)


class ClassificationResult(LLMOutputBase):
    category: str = Field(description="One classification label from allowed categories")
    confidence: float = Field(description="Confidence score in range [0.0, 1.0]")
    reasons: list[str] = Field(default_factory=list, description="Concise reasons for the selected category")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "category": "Newsfeed",
                    "confidence": 0.93,
                    "reasons": ["Newsletter-style subject", "Contains multiple article links"],
                }
            ]
        },
    )


class ExtractionResult(LLMOutputBase):
    links: list[str] = Field(description="List of fully-qualified article/news URLs")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "links": [
                        "https://example.com/news/story-1",
                        "https://example.com/analysis/market-update",
                    ]
                }
            ]
        },
    )
