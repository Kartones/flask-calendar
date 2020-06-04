from typing import Dict, Optional

from flask_calendar.calendar_data import CalendarData


class Authorization:
    def __init__(self, calendar_data: CalendarData) -> None:
        self.calendar_data = calendar_data

    def can_access(self, username: str, data: Optional[Dict] = None, calendar_id: Optional[str] = None,) -> bool:
        if calendar_id is None:
            return username in self.calendar_data.users_list(data=data)
        else:
            return username in self.calendar_data.users_list(calendar_id=calendar_id)
