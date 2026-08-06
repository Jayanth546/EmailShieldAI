from app.analyzers.header_analyzer import HeaderAnalyzer
from app.analyzers.url_analyzer import URLAnalyzer
from app.analyzers.body_analyzer import BodyAnalyzer
from app.analyzers.attachment_analyzer import AttachmentAnalyzer
from app.analyzers.authentication_analyzer import AuthenticationAnalyzer

from app.services.risk_engine import RiskEngine
from app.utils.pdf_generator import PDFGenerator
from app.database.db_service import DatabaseService

class EmailAnalysisService:

    def __init__(self):
        self.header = HeaderAnalyzer()
        self.url = URLAnalyzer()
        self.body = BodyAnalyzer()
        self.attachment = AttachmentAnalyzer()
        self.authentication = AuthenticationAnalyzer()

        self.risk = RiskEngine()
        self.pdf = PDFGenerator()
        self.db = DatabaseService()

    def analyze(self, email):

        # Analyze email header
        header_result = self.header.analyze(email)

        # Analyze URLs
        url_result = self.url.analyze(
            email.get("urls", [])
        )

        # Analyze email body
        body_result = self.body.analyze(
            email.get("body", "")
        )

        # Analyze attachments
        attachment_result = self.attachment.analyze(
            email.get("attachments", [])
        )

        # Analyze authentication
        authentication_result = self.authentication.analyze(email)

        # Calculate overall risk
        risk_result = self.risk.analyze(
            header_result,
            url_result,
            body_result,
            attachment_result,
            authentication_result,
        )

        # Final result
        result = {
            "header": header_result,
            "url": url_result,
            "body": body_result,
            "attachment": attachment_result,
            "authentication": authentication_result,

            "risk": risk_result,

            "risk_level": risk_result["verdict"].title(),
            "total_score": risk_result["total_score"],
        }

        # Generate PDF report
        pdf_path = "email_report.pdf"
        self.pdf.generate(
            result,
            "email_report.pdf"
        )

 # Save report to database
        report_id = self.db.save_report(
            email,
            result,
            pdf_path,
        )

        # Add report ID to response
        result["report_id"] = report_id

        return result
