from typing import Dict, Optional

from calendar_data import CalendarData


class Authorization:

    def __init__(self, calendar_data: CalendarData) -> None:
        self.calendar_data = calendar_data

    def can_access(self, username: str, data: Optional[Dict]=None, calendar_id: Optional[str]=None) -> bool:
        if calendar_id is None:
            return username in self.calendar_data.users(data=data)
        else:
            return username in self.calendar_data.users(calendar_id=calendar_id)
