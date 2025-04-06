from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from utils.api import HTTPException

from ..models.alert_template import AlertTemplate
from ..schemas.alert_template import AlertTemplateCreate, AlertTemplateUpdate


class AlertTemplateService:
    def __init__(self, db: Session):
        self.db = db

    def create_template(self, template_data: AlertTemplateCreate) -> AlertTemplate:
        """
        Create a new alert template

        Args:
            template_data: Template data to create

        Returns:
            Created template

        Raises:
            HTTPException: If template with same name already exists
        """
        try:
            db_template = AlertTemplate(
                name=template_data.name,
                template=template_data.template
            )
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Template with this name already exists"
            )

    def list_templates(self, skip: int = 0, limit: int = 100) -> List[AlertTemplate]:
        """
        List all alert templates with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of templates
        """
        return self.db.query(AlertTemplate).offset(skip).limit(limit).all()

    def get_template(self, template_id: int) -> Optional[AlertTemplate]:
        """
        Get a specific template by ID

        Args:
            template_id: ID of the template to retrieve

        Returns:
            Template if found, None otherwise
        """
        return self.db.query(AlertTemplate).filter(AlertTemplate.id == template_id).first()

    def replace_template(self, template_id: int, template_data: AlertTemplateCreate) -> Optional[AlertTemplate]:
        """
        Replace an existing template completely (PUT operation)

        Args:
            template_id: ID of the template to replace
            template_data: New template data (all fields required)

        Returns:
            Updated template if found and updated successfully

        Raises:
            HTTPException: If template not found or if update violates unique constraints
        """
        db_template = self.get_template(template_id)
        if db_template is None:
            raise HTTPException(status_code=404, detail="Template not found")

        try:
            # Update all fields
            db_template.name = template_data.name
            db_template.template = template_data.template

            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Template with this name already exists"
            )

    def update_template(self, template_id: int, template_update: AlertTemplateUpdate) -> Optional[AlertTemplate]:
        """
        Update an existing template partially (PATCH operation)

        Args:
            template_id: ID of the template to update
            template_update: New template data (fields are optional)

        Returns:
            Updated template if found and updated successfully

        Raises:
            HTTPException: If template not found or if update violates unique constraints
        """
        db_template = self.get_template(template_id)
        if db_template is None:
            raise HTTPException(status_code=404, detail="Template not found")

        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Template with this name already exists"
            )

    def delete_template(self, template_id: int) -> bool:
        """
        Delete a template

        Args:
            template_id: ID of the template to delete

        Returns:
            True if template was deleted, False if template was not found
        """
        db_template = self.get_template(template_id)
        if db_template is None:
            return False

        self.db.delete(db_template)
        self.db.commit()
        return True
