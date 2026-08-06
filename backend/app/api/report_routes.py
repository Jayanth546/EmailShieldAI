from fastapi import APIRouter, HTTPException

from app.database.db_service import DatabaseService

router = APIRouter()

db = DatabaseService()


@router.get("/reports")
def get_reports():
    reports = db.get_reports()

    return [
        {
            "id": report.id,
            "sender": report.sender,
            "message_id": report.message_id,
            "risk_level": report.risk_level,
            "total_score": report.total_score,
            "report_path": report.report_path,
        }
        for report in reports
    ]


@router.get("/reports/{report_id}")
def get_report(report_id: int):
    report = db.get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return {
        "id": report.id,
        "sender": report.sender,
        "message_id": report.message_id,
        "body": report.body,
        "risk_level": report.risk_level,
        "total_score": report.total_score,
        "report_path": report.report_path,
    }
