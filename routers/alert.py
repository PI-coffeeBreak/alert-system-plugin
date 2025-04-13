from utils.api import Router, Depends
from services.message_bus import MessageBus
from models.message import RecipientType
from schemas.notification import NotificationRequest
from dependencies.auth import check_role
from dependencies.database import get_db
from sqlalchemy.orm import Session
from typing import List
from ..schemas.alert import AlertRequest
from ..schemas.high_priority_alert import HighPriorityAlertResponse
from ..services.high_priority_alert_service import HighPriorityAlertService

router = Router()


@router.post("/")
async def create_alert(
    alert: AlertRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(check_role(["manage_alerts"]))
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

    # If it's a high priority alert, store it
    if alert.high_priority:
        HighPriorityAlertService(db).store_high_priority_alert(alert.message)

    return await message_bus.send_notification(notification)


@router.get("/high-priority", response_model=List[HighPriorityAlertResponse])
async def get_high_priority_alerts(
    db: Session = Depends(get_db),
):
    """Returns the last 3 high priority alerts from the last hour"""
    return HighPriorityAlertService(db).get_last_high_priority_alerts()
