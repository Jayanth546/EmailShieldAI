from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.schemas.email_schema import EmailRequest, EmailAnalysisResponse
from app.services.email_analysis_service import EmailAnalysisService


router = APIRouter()

service = EmailAnalysisService()


@router.post(
    "/analyze",
    response_model=EmailAnalysisResponse,
)
def analyze_email(
    request: EmailRequest,
    current_user=Depends(get_current_user),
):
    parsed_email = {
        "from": request.from_,
        "message_id": request.message_id,
        "reply_to": request.reply_to,
        "authentication_results": request.authentication_results,
        "received_spf": request.received_spf,
        "dkim_signature": request.dkim_signature,
        "body": request.body,
        "urls": request.urls,
        "attachments": request.attachments,
    }

    result = service.analyze(
        parsed_email,
        current_user.id,
    )

    return result
