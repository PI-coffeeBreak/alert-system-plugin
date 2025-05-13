from pydantic import BaseModel, field_serializer
from datetime import datetime


class HighPriorityAlertResponse(BaseModel):
    """Schema for high priority alert responses"""
    id: int
    message: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.isoformat()

    class Config:
        from_attributes = True
