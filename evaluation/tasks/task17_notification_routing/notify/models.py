from dataclasses import dataclass


@dataclass(frozen=True)
class Preferences:
    email_enabled: bool = True
    sms_enabled: bool = False
    quiet_start_hour: int = 22
    quiet_end_hour: int = 7

    def __post_init__(self):
        for value in (self.quiet_start_hour, self.quiet_end_hour):
            if not 0 <= value <= 23:
                raise ValueError("quiet hours must be in [0, 23]")


@dataclass(frozen=True)
class Notification:
    message: str
    critical: bool = False
    preferred_channel: str | None = None
