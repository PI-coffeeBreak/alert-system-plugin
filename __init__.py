from utils.api import Router
from .routers import router
from .schemas.alert_component import Alert
from services.component_registry import ComponentRegistry

NAME = "Alert System Plugin"
DESCRIPTION = "A plugin for the Alert System"

def register_plugin():
    # Register UI components
    ComponentRegistry.register_component(Alert)
    return router


def unregister_plugin():
    # Unregister UI components
    ComponentRegistry.unregister_component("Alert")

REGISTER = register_plugin
UNREGISTER = unregister_plugin

CONFIG_PAGE = True
