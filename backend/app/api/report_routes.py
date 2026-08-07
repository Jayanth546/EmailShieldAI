from fastapi import APIRouter, HTTPException, Depends

from app.auth.dependencies import get_current_user
from app.database.db_service import DatabaseService

router = APIRouter()

db = DatabaseService()


@router.get("/reports")
def get_reports(
    current_user=Depends(get_current_user),
):
    reports = db.get_reports(current_user.id)

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
def get_report(
    report_id: int,
    current_user=Depends(get_current_user),
):
    report = db.get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    # Ownership check
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this report",
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
