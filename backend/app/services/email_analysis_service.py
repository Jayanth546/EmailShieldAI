from app.analyzers.header_analyzer import HeaderAnalyzer
from app.analyzers.url_analyzer import URLAnalyzer
from app.analyzers.body_analyzer import BodyAnalyzer
from app.analyzers.attachment_analyzer import AttachmentAnalyzer
from app.analyzers.authentication_analyzer import AuthenticationAnalyzer

from app.services.risk_engine import RiskEngine


class EmailAnalysisService:

    def __init__(self):
        self.header = HeaderAnalyzer()
        self.url = URLAnalyzer()
        self.body = BodyAnalyzer()
        self.attachment = AttachmentAnalyzer()
        self.authentication = AuthenticationAnalyzer()
        self.risk = RiskEngine()

    def analyze(self, email):

        header_result = self.header.analyze(email)

        url_result = self.url.analyze(
            email.get("urls", [])
        )

        body_result = self.body.analyze(
            email.get("body", "")
        )

        attachment_result = self.attachment.analyze(
            email.get("attachments", [])
        )

        authentication_result = self.authentication.analyze(email)

        risk_result = self.risk.analyze(
            header_result,
            url_result,
            body_result,
            attachment_result,
            authentication_result,
        )

        return {
            "header": header_result,
            "url": url_result,
            "body": body_result,
            "attachment": attachment_result,
            "authentication": authentication_result,

            # Risk Engine output
            "risk": risk_result,

            # Convenience fields for tests/API
            "risk_level": risk_result["verdict"].title(),
            "total_score": risk_result["total_score"],
        }
