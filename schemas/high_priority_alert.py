from pydantic import BaseModel
from datetime import datetime


class HighPriorityAlertResponse(BaseModel):
    """
    Schema for high priority alert response
    """
    id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
