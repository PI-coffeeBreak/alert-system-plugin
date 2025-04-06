from utils.api import Router
from .routers import router
from .schemas.alert_component import AlertComponent
from services.component_registry import ComponentRegistry


def register_plugin():
    # Register UI components
    ComponentRegistry.register_component(AlertComponent)

    return router


def unregister_plugin():
    # Unregister UI components
    ComponentRegistry.unregister_component("AlertComponent")


REGISTER = register_plugin
UNREGISTER = unregister_plugin
