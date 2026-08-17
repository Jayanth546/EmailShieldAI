from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_: str = Field(
        default="",
        alias="from",
        max_length=320,
    )

    message_id: str | None = Field(
        default=None,
        max_length=512,
    )

    reply_to: str | None = Field(
        default=None,
        max_length=320,
    )

    authentication_results: str | None = Field(
        default=None,
        max_length=4096,
    )

    received_spf: str | None = Field(
        default=None,
        max_length=1024,
    )

    dkim_signature: str | None = Field(
        default=None,
        max_length=8192,
    )

    body: str = Field(
        default="",
        max_length=100_000,
    )

    urls: list[str] = Field(
        default_factory=list,
        max_length=100,
    )

    attachments: list[str] = Field(
        default_factory=list,
        max_length=50,
    )

    @field_validator("from_", "reply_to", "message_id")
    @classmethod
    def reject_newlines(cls, value):
        if value is not None and ("\r" in value or "\n" in value):
            raise ValueError("Header fields must not contain newline characters")
        return value

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, urls):
        for url in urls:
            if len(url) > 2048:
                raise ValueError("URL exceeds maximum allowed length")

            if "\r" in url or "\n" in url:
                raise ValueError("URL must not contain newline characters")

        return urls

    @field_validator("attachments")
    @classmethod
    def validate_attachments(cls, attachments):
        for filename in attachments:
            if len(filename) > 255:
                raise ValueError("Attachment filename is too long")

            if "\x00" in filename:
                raise ValueError("Attachment filename contains an invalid character")

            if "\r" in filename or "\n" in filename:
                raise ValueError(
                    "Attachment filename must not contain newline characters"
                )

        return attachments


class RiskResponse(BaseModel):
    total_score: int
    verdict: str
    rule_based_score: int
    spam_score: int
    reasons: list[dict[str, Any]]
    details: dict[str, Any]


class EmailAnalysisResponse(BaseModel):
    header: dict[str, Any]
    url: dict[str, Any]
    body: dict[str, Any]
    attachment: dict[str, Any]
    authentication: dict[str, Any]
    spam: dict[str, Any]
    risk: RiskResponse
    risk_level: str
    total_score: int
    report_id: int | None = None

