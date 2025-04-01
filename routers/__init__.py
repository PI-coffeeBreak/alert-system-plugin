from utils.api import Router
from .alert import router as alert_router

router = Router()
router.include_router(alert_router, "/alert")
