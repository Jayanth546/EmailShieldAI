from sqlalchemy.orm import Session

from app.models.analysis import Analysis


def save_analysis(
    db: Session,
    sender,
    subject,
    risk_level,
    total_score,
    issues,
):
    analysis = Analysis(
        sender=sender,
        subject=subject,
        risk_level=risk_level,
        total_score=total_score,
        issues=issues,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


def get_all_analyses(db: Session):
    return db.query(Analysis).all()
