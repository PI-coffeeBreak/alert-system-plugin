from .routers import router
from .schemas.alert_component import Alert
from coffeebreak import ComponentRegistry


def REGISTER():
    ComponentRegistry.register_component(Alert)


def UNREGISTER():
    ComponentRegistry.unregister_component("Alert")
