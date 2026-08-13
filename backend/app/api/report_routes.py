from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from app.auth.dependencies import get_current_user
from app.database.db_service import DatabaseService
from app.config import REPORTS_DIR


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


@router.get("/reports/{report_id}/pdf")
def download_report_pdf(
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

    # Resolve the configured reports directory
    reports_dir = REPORTS_DIR.resolve()

    # Resolve the stored PDF path safely
    report_path = Path(report.report_path)

    if not report_path.is_absolute():
        report_path = Path("/app") / report_path

    report_path = report_path.resolve()

    # Ensure the PDF is inside the configured reports directory
    try:
        report_path.relative_to(reports_dir)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid report path",
        )

    # Only allow PDF files
    if report_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid report file",
        )

    # Verify that the PDF exists
    if not report_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF report file not found",
        )

    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename=report_path.name,
    )


@router.delete("/reports/{report_id}")
def delete_report(
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
            detail="You do not have permission to delete this report",
        )

    # Delete PDF file first
    if report.report_path:
        report_path = Path(report.report_path)

        # Resolve the configured reports directory
        reports_dir = REPORTS_DIR.resolve()

        if not report_path.is_absolute():
            report_path = Path("/app") / report_path

        report_path = report_path.resolve()

        # Prevent path traversal
        try:
            report_path.relative_to(reports_dir)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid report path",
            )

        # Only delete PDF files
        if report_path.suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=400,
                detail="Invalid report file",
            )

        if report_path.is_file():
            report_path.unlink()

    # Delete database record
    deleted = db.delete_report(report_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return {
        "message": "Report deleted successfully",
        "report_id": report_id,
    }
