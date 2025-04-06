from utils.api import Router
from .alert import router as alert_router
from .alert_template import router as alert_template_router

router = Router()
router.include_router(alert_router, "/alert")
router.include_router(alert_template_router, "/template")
