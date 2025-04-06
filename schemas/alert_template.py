from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertTemplateBase(BaseModel):
    """
    Base schema for alert template

    Attributes:
        name (str): Unique name for the template
        template (str): Message template with placeholders
    """
    name: str = Field(..., min_length=1,
                      description="Unique name for the template")
    template: str = Field(..., min_length=1,
                          description="Message template with placeholders (e.g., 'Hello {name}, your {item} is ready')")


class AlertTemplateCreate(AlertTemplateBase):
    """Schema for creating a new alert template"""
    pass


class AlertTemplateUpdate(BaseModel):
    """
    Schema for updating alert template fields
    All fields are optional since it's a partial update
    """
    name: Optional[str] = Field(None, min_length=1)
    template: Optional[str] = Field(None, min_length=1)


class AlertTemplateResponse(AlertTemplateBase):
    """
    Schema for alert template response
    Includes database fields like id and timestamps
    """
    id: int
    created_at: datetime
    updated_at: datetime
