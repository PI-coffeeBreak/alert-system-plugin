from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from dependencies.database import Base


class HighPriorityAlert(Base):
    """
    SQLAlchemy model for storing the last 3 high priority alerts
    """
    __tablename__ = "high_priority_alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
