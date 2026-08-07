from app.database.database import SessionLocal
from app.models.email_report import EmailReport
from app.models.user import User


class DatabaseService:

    def save_report(self, email, result, report_path):
        db = SessionLocal()

        try:
            report = EmailReport(
                sender=email.get("from", ""),
                message_id=email.get("message_id"),
                body=email.get("body", ""),
                risk_level=result["risk_level"],
                total_score=result["total_score"],
                report_path=report_path,
            )

            db.add(report)
            db.commit()
            db.refresh(report)

            return report.id

        finally:
            db.close()

    def get_reports(self):
        db = SessionLocal()

        try:
            return db.query(EmailReport).all()

        finally:
            db.close()

    def get_report(self, report_id):
        db = SessionLocal()

        try:
            return (
                db.query(EmailReport)
                .filter(EmailReport.id == report_id)
                .first()
            )

        finally:
            db.close()

    def create_user(self, username, email, hashed_password):
        db = SessionLocal()

        try:
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        finally:
            db.close()

    def get_user_by_username(self, username):
        db = SessionLocal()

        try:
            return (
                db.query(User)
                .filter(User.username == username)
                .first()
            )

        finally:
            db.close()

    def get_user_by_email(self, email):
        db = SessionLocal()

        try:
            return (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

        finally:
            db.close()
