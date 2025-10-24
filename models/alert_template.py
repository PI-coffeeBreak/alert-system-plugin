from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from coffeebreak.db import ModelBase as Base


class AlertTemplate(Base):
    """
    SQLAlchemy model for alert templates
    Stores message templates with placeholders for dynamic content
    """
    __tablename__ = "alert_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())
