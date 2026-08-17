from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class EmailReport(Base):
    __tablename__ = "email_reports"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    risk_level = Column(String(20))
    total_score = Column(Integer)

    sender = Column(String(255))
    message_id = Column(String(255))

    report_path = Column(String(255))

    body = Column(Text)

    user = relationship(
        "User",
        back_populates="reports",
    )
