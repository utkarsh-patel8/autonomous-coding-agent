from notify.models import Notification, Preferences
from notify.router import route_notification
from notify.service import NotificationService
from notify.time_rules import in_quiet_hours


def test_quiet_hours_cross_midnight():
    assert in_quiet_hours(23, 22, 7)
    assert in_quiet_hours(2, 22, 7)
    assert not in_quiet_hours(12, 22, 7)


def test_noncritical_message_is_suppressed_during_overnight_quiet_hours():
    prefs = Preferences(email_enabled=True, sms_enabled=True, quiet_start_hour=22, quiet_end_hour=7)
    note = Notification("daily summary")
    assert route_notification(note, prefs, hour=1) == []


def test_critical_message_bypasses_quiet_hours_but_respects_enabled_channels():
    prefs = Preferences(email_enabled=False, sms_enabled=True, quiet_start_hour=22, quiet_end_hour=7)
    note = Notification("server down", critical=True)
    assert route_notification(note, prefs, hour=2) == ["sms"]


def test_no_enabled_channels_means_no_delivery_even_for_critical_message():
    prefs = Preferences(email_enabled=False, sms_enabled=False)
    note = Notification("server down", critical=True)
    assert route_notification(note, prefs, hour=12) == []


def test_preferred_channel_is_first_only_when_enabled():
    prefs = Preferences(email_enabled=True, sms_enabled=True)
    assert route_notification(Notification("x", preferred_channel="sms"), prefs, hour=12) == ["sms", "email"]

    email_only = Preferences(email_enabled=True, sms_enabled=False)
    assert route_notification(Notification("x", preferred_channel="sms"), email_only, hour=12) == ["email"]


def test_service_builds_deliveries_from_router_result():
    prefs = Preferences(email_enabled=True, sms_enabled=True)
    result = NotificationService().plan(Notification("hello", preferred_channel="sms"), prefs, hour=12)
    assert [(d.channel, d.message) for d in result] == [("sms", "hello"), ("email", "hello")]
