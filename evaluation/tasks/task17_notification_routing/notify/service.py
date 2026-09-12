from dataclasses import dataclass
from .models import Notification, Preferences
from .router import route_notification


@dataclass(frozen=True)
class Delivery:
    channel: str
    message: str


class NotificationService:
    def plan(
        self,
        notification: Notification,
        preferences: Preferences,
        *,
        hour: int,
    ) -> list[Delivery]:
        return [
            Delivery(channel=channel, message=notification.message)
            for channel in route_notification(
                notification,
                preferences,
                hour=hour,
            )
        ]
