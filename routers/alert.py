from utils.api import Router, Depends
from dependencies.auth import check_role
from services.message_bus import MessageBus
from dependencies.database import get_db
from schemas.notification import NotificationRequest, RecipientType
from ..schemas.alert import AlertRequest

router = Router()


@router.post("/")
async def send_notification(data: AlertRequest, user: dict = Depends(check_role(["send_alert"])), db=Depends(get_db)):
    # Convert AlertRequest to NotificationRequest
    notification = NotificationRequest(
        type="in-app",
        recipient_type=RecipientType.GROUP,
        recipient="attendee",  # Send to the user who created the alert
        payload=data.message,
        priority=10 if data.high_priority else 5  # High priority = 10, Normal = 5
    )

    message_bus = MessageBus(db)
    await message_bus.send_notification(notification)
    return {"status": "ok"}
