from app.analyzers.header_analyzer import HeaderAnalyzer
from app.analyzers.url_analyzer import URLAnalyzer
from app.analyzers.body_analyzer import BodyAnalyzer
from app.analyzers.attachment_analyzer import AttachmentAnalyzer
from app.analyzers.authentication_analyzer import AuthenticationAnalyzer

from app.services.risk_engine import RiskEngine
from app.utils.pdf_generator import PDFGenerator
from app.database.db_service import DatabaseService

from ml.prediction.spam_predictor import SpamPredictor


class EmailAnalysisService:

    def __init__(self):
        # Traditional security analyzers
        self.header = HeaderAnalyzer()
        self.url = URLAnalyzer()
        self.body = BodyAnalyzer()
        self.attachment = AttachmentAnalyzer()
        self.authentication = AuthenticationAnalyzer()

        # Risk engine
        self.risk = RiskEngine()

        # PDF and database services
        self.pdf = PDFGenerator()
        self.db = DatabaseService()

        # Machine-learning spam predictor
        self.spam_predictor = SpamPredictor()

    def analyze(self, email, user_id=None):
        """
        Analyze an email using traditional security analysis
        and machine-learning spam prediction.

        Supports:

            service.analyze(email)

        and:

            service.analyze(email, user_id)
        """

        # --------------------------------------------------
        # 1. Header analysis
        # --------------------------------------------------
        header_result = self.header.analyze(email)

        # --------------------------------------------------
        # 2. URL analysis
        # --------------------------------------------------
        url_result = self.url.analyze(
            email.get("urls", [])
        )

        # --------------------------------------------------
        # 3. Body analysis
        # --------------------------------------------------
        body_text = email.get("body", "")

        body_result = self.body.analyze(
            body_text
        )

        # --------------------------------------------------
        # 4. Attachment analysis
        # --------------------------------------------------
        attachment_result = self.attachment.analyze(
            email.get("attachments", [])
        )

        # --------------------------------------------------
        # 5. Authentication analysis
        # --------------------------------------------------
        authentication_result = self.authentication.analyze(
            email
        )

        # --------------------------------------------------
        # 6. Machine-learning spam prediction
        # --------------------------------------------------
        spam_result = self.spam_predictor.predict(
            body_text
        )

        # --------------------------------------------------
        # 7. Traditional risk calculation
        # --------------------------------------------------
        risk_result = self.risk.analyze(
            header_result,
            url_result,
            body_result,
            attachment_result,
            authentication_result,
            spam_result,
        )

        # --------------------------------------------------
        # 8. Combine ML result with security analysis
        # --------------------------------------------------
        result = {
            "header": header_result,
            "url": url_result,
            "body": body_result,
            "attachment": attachment_result,
            "authentication": authentication_result,

            # Machine-learning result
            "spam": spam_result,

            # Traditional risk analysis
            "risk": risk_result,

            "risk_level": risk_result["verdict"].title(),
            "total_score": risk_result["total_score"],
        }

        # --------------------------------------------------
        # 9. Generate PDF report
        # --------------------------------------------------
        pdf_path = "email_report.pdf"

        self.pdf.generate(
            result,
            pdf_path,
        )

        # --------------------------------------------------
        # 10. Save report to database
        # --------------------------------------------------
        if user_id is not None:
            report_id = self.db.save_report(
                user_id,
                email,
                result,
                pdf_path,
            )

            result["report_id"] = report_id

        return result
