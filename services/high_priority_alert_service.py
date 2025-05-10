from typing import List, Set, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import logging

from services.websocket_service import WebSocketConnection
from ..models.high_priority_alert import HighPriorityAlert
from ..schemas.high_priority_alert import HighPriorityAlertResponse
logger = logging.getLogger("coffeebreak.alert-system")


class HighPriorityAlertService:
    _instance = None
    _initialized = False

    def __new__(cls, db: Optional[Session] = None):
        if cls._instance is None:
            cls._instance = super(HighPriorityAlertService, cls).__new__(cls)
        return cls._instance

    def __init__(self, db: Optional[Session] = None):
        if self._initialized:
            if db is not None:
                self.db = db
            return
        
        self.db = db
        self.subscribers: Set[WebSocketConnection] = set()
        self._initialized = True

    async def store_high_priority_alert(self, message: str) -> HighPriorityAlert:
        """
        Store a new high priority alert and maintain only the last 3
        """
        if self.db is None:
            raise ValueError("Database session is required for this operation")
            
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

        # Create a HighPriorityAlertResponse object and serialize it
        alert_response = HighPriorityAlertResponse(
            id=new_alert.id,
            message=new_alert.message,
            created_at=new_alert.created_at
        )
        
        await self.notify_subscribers(alert_response.model_dump())

        return new_alert

    def get_last_high_priority_alerts(self) -> List[HighPriorityAlertResponse]:
        """
        Get the last 3 high priority alerts ordered by creation date (newest first)
        that are not older than 1 hour
        """
        if self.db is None:
            raise ValueError("Database session is required for this operation")
            
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        logger.debug(f"Fetching alerts newer than: {one_hour_ago}")

        # First get all alerts to check their timestamps
        alerts = self.db.query(HighPriorityAlert).order_by(
            HighPriorityAlert.created_at.desc()
        ).all()

        # Then filter by time
        alerts = self.db.query(HighPriorityAlert).filter(
            HighPriorityAlert.created_at >= one_hour_ago
        ).order_by(
            HighPriorityAlert.created_at.desc()
        ).limit(3).all()

        logger.info(f"Found {len(alerts)} alerts after filtering by time")
        
        # Convert to response objects
        return [
            HighPriorityAlertResponse(
                id=alert.id,
                message=alert.message,
                created_at=alert.created_at
            )
            for alert in alerts
        ]

    def subscribe(self, connection: WebSocketConnection) -> None:
        """Add a connection to the list of subscribers"""
        self.subscribers.add(connection)

    def unsubscribe(self, connection: WebSocketConnection) -> None:
        """Remove a connection from the list of subscribers"""
        self.subscribers.discard(connection)

    async def notify_subscribers(self, alert: dict) -> None:
        """Notify all subscribers about a new high priority alert"""
        logger.info(f"Notifying {len(self.subscribers)} subscribers about new high priority alert")
        
        for connection in self.subscribers:
            logger.info(f"Notifying subscriber: {connection}")
            await connection.send("high-priority-alerts", alert)
