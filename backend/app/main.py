from fastapi import FastAPI

from app.api.auth_routes import router as auth_router
from app.api.report_routes import router as report_router
from app.schemas.email_schema import EmailRequest
from app.services.email_analysis_service import EmailAnalysisService


app = FastAPI(
    title="EmailShield AI",
    version="1.0",
)

service = EmailAnalysisService()


@app.get("/")
def root():
    return {
        "message": "Welcome to EmailShield AI"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
def analyze_email(request: EmailRequest):

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

    result = service.analyze(parsed_email)

    return result


# Register Report API
app.include_router(report_router)

# Register Authentication API
app.include_router(auth_router)
