from utils.api import Router, Depends
from services.message_bus import MessageBus
from schemas.notification import RecipientType
from schemas.notification import NotificationRequest
from dependencies.auth import check_role
from dependencies.database import get_db
from sqlalchemy.orm import Session
from typing import List
from ..schemas.alert import AlertRequest
from ..schemas.high_priority_alert import HighPriorityAlertResponse
from ..services.high_priority_alert_service import HighPriorityAlertService
from services.websocket_service import WebSocketService, WebSocketConnection
from datetime import datetime, timezone
import logging

logger = logging.getLogger("coffeebreak.alert-system")

router = Router()
websocket_service = WebSocketService()


@websocket_service.on_subscribe("high-priority-alerts")
async def handle_alert_subscription(connection: WebSocketConnection):
    """Handle subscription to high priority alerts topic"""
    logger.info(f"New subscription to high priority alerts from {connection}")
    HighPriorityAlertService(get_db()).subscribe(connection)

@websocket_service.on_unsubscribe("high-priority-alerts")
async def handle_alert_unsubscribe(connection: WebSocketConnection):
    """Handle unsubscription from high priority alerts topic"""
    logger.info(f"Unsubscribed from high priority alerts: {connection}")
    HighPriorityAlertService(get_db()).unsubscribe(connection)

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

    if alert.high_priority:
        await HighPriorityAlertService(db).store_high_priority_alert(alert.message)

    return await message_bus.send_notification(notification)


@router.get("/high-priority", response_model=List[HighPriorityAlertResponse])
async def get_high_priority_alerts(
    db: Session = Depends(get_db),
):
    """Returns the last 3 high priority alerts from the last hour"""
    return HighPriorityAlertService(db).get_last_high_priority_alerts()
