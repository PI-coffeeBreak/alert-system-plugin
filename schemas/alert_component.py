from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from schemas.ui.page import BaseComponentSchema
from datetime import datetime, timezone


class AlertMessage(BaseModel):
    """
    Represents a message in the alert component
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    content: str
    priority: int = Field(ge=0, le=10)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False


class AlertComponent(BaseComponentSchema):
    """
    Represents a component that can receive highlighted alerts
    """
    messages: List[AlertMessage] = Field(
        default_factory=list)
