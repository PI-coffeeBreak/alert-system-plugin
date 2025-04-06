from pydantic import BaseModel


class AlertRequest(BaseModel):
    """
    Schema for alert notifications

    Attributes:
        message (str): The alert message to be sent
        high_priority (bool): Flag to indicate if this is a high priority alert
    """
    message: str
    high_priority: bool = False
