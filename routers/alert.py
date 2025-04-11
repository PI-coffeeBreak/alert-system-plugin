from utils.api import Router, Depends
from services.message_bus import MessageBus
from models.message import RecipientType
from schemas.notification import NotificationRequest
from dependencies.auth import get_current_user
from dependencies.database import get_db
from sqlalchemy.orm import Session
from ..schemas.alert import AlertRequest

router = Router()


@router.post("/")
async def create_alert(
    alert: AlertRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Creates a new alert that will be broadcast to all users"""
    message_bus = MessageBus(db)
    notification = NotificationRequest(
        type="in-app",  # Standard notification type
        recipient_type=RecipientType.BROADCAST,  # Always broadcast
        recipient=None,  # No specific recipient for broadcast
        payload=alert.message,
        # High priority (10) or normal (5)
        priority=10 if alert.high_priority else 5
    )

    return await message_bus.send_notification(notification)
