from .models import Notification, Preferences
from .time_rules import in_quiet_hours


VALID_CHANNELS = ("email", "sms")


def enabled_channels(preferences: Preferences) -> list[str]:
    channels = []
    if preferences.email_enabled:
        channels.append("email")
    if preferences.sms_enabled:
        channels.append("sms")
    return channels


def route_notification(
    notification: Notification,
    preferences: Preferences,
    *,
    hour: int,
) -> list[str]:
    channels = enabled_channels(preferences)

    if (
        not notification.critical
        and in_quiet_hours(
            hour,
            preferences.quiet_start_hour,
            preferences.quiet_end_hour,
        )
    ):
        return []

    if notification.preferred_channel in channels:
        preferred = notification.preferred_channel
        channels = [preferred] + [c for c in channels if c != preferred]

    # BUG: disabled channels must never be invented as a fallback.
    if not channels:
        return ["email"]

    return channels
