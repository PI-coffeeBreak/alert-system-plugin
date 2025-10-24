from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import uuid4
from coffeebreak.schemas import BaseComponent as BaseComponentSchema
from datetime import datetime, timezone


class Alert(BaseComponentSchema):
    name: Literal["Alert"] = Field(default="Alert", title="Component Name")
