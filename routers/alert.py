from utils.api import Router, Depends
from dependencies.auth import check_role
from services.message_bus import MessageBus
from dependencies.database import get_db
from schemas.notification import NotificationRequest

router = Router()

@router.post("/")
def send_notification(data: NotificationRequest, user: dict = Depends(check_role(["send-alerts"])), db = Depends(get_db)):
    MessageBus().send_message("alert", data)
    return {"status": "ok"}