from typing import List
from sqlalchemy.orm import Session
from ..models.high_priority_alert import HighPriorityAlert
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("coffeebreak.alert-system")


class HighPriorityAlertService:
    def __init__(self, db: Session):
        self.db = db

    def store_high_priority_alert(self, message: str) -> HighPriorityAlert:
        """
        Store a new high priority alert and maintain only the last 3
        """
        # Create new alert
        new_alert = HighPriorityAlert(message=message)
        self.db.add(new_alert)

        logger.info(f"Storing high priority alert: {message}")

        # Get all alerts ordered by creation date
        alerts = self.db.query(HighPriorityAlert).order_by(
            HighPriorityAlert.created_at.desc()
        ).all()

        # If we have more than 3 alerts, remove the oldest ones
        if len(alerts) >= 3:
            for alert in alerts[2:]:  # Keep only the 3 most recent
                self.db.delete(alert)

        self.db.commit()
        self.db.refresh(new_alert)
        return new_alert

    def get_last_high_priority_alerts(self) -> List[HighPriorityAlert]:
        """
        Get the last 3 high priority alerts ordered by creation date (newest first)
        that are not older than 1 hour
        """
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        logger.info(f"Fetching alerts newer than: {one_hour_ago}")

        # First get all alerts to check their timestamps
        alerts = self.db.query(HighPriorityAlert).order_by(
            HighPriorityAlert.created_at.desc()
        ).all()

        logger.info("All alerts in database:")
        for alert in alerts:
            logger.info(
                f"Alert created at {alert.created_at}: {alert.message}")

        # Then filter by time
        alerts = self.db.query(HighPriorityAlert).filter(
            HighPriorityAlert.created_at >= one_hour_ago
        ).order_by(
            HighPriorityAlert.created_at.desc()
        ).limit(3).all()

        logger.info(f"Found {len(alerts)} alerts after filtering by time")
        for alert in alerts:
            logger.info(
                f"Alert created at {alert.created_at}: {alert.message}")

        return alerts
