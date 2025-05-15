from typing import List
from utils.api import Router, Depends, HTTPException
from dependencies.auth import check_role
from dependencies.database import get_db
from sqlalchemy.orm import Session

from ..schemas.alert_template import (
    AlertTemplateCreate,
    AlertTemplateUpdate,
    AlertTemplateResponse
)
from ..services.alert_template_service import AlertTemplateService

router = Router()


@router.post("/", response_model=AlertTemplateResponse)
async def create_template(
    template: AlertTemplateCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """Create a new alert template"""
    service = AlertTemplateService(db)
    return service.create_template(template)


@router.get("/", response_model=List[AlertTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """List all alert templates"""
    service = AlertTemplateService(db)
    return service.list_templates(skip=skip, limit=limit)


@router.get("/{template_id}", response_model=AlertTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """Get a specific alert template by ID"""
    service = AlertTemplateService(db)
    template = service.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=AlertTemplateResponse)
async def replace_template(
    template_id: int,
    template: AlertTemplateCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """Replace an alert template completely (all fields required)"""
    service = AlertTemplateService(db)
    return service.replace_template(template_id, template)


@router.patch("/{template_id}", response_model=AlertTemplateResponse)
async def update_template(
    template_id: int,
    template_update: AlertTemplateUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """Update an alert template partially (fields are optional)"""
    service = AlertTemplateService(db)
    return service.update_template(template_id, template_update)


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_alerts"]))
):
    """Delete an alert template"""
    service = AlertTemplateService(db)
    if not service.delete_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"detail": "Template deleted successfully"}
