from typing import List, Optional

from pydantic import BaseModel


class EmailRequest(BaseModel):
    from_: str = ""
    message_id: Optional[str] = None
    reply_to: Optional[str] = None

    authentication_results: Optional[str] = None
    received_spf: Optional[str] = None
    dkim_signature: Optional[str] = None

    body: str = ""

    urls: List[str] = []

    attachments: List[str] = []


class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str


class EmailAnalysisResponse(BaseModel):
    header: dict
    url: dict
    body: dict
    attachment: dict
    authentication: dict
    risk: RiskResponse
