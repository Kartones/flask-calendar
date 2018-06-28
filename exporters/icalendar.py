from typing import Dict

from calendar_data import CalendarData
from gregorian_calendar import GregorianCalendar


# https://tools.ietf.org/html/rfc5545
class ICalendar:

    def __init__(self, username: str, timezone: str, months_to_export: int) -> None:
        self.username = username
        self.timezone = timezone
        self.months_to_export = months_to_export

    def write(self, calendar_data: CalendarData, data: Dict) -> bool:
        current_day, current_month, current_year = GregorianCalendar.current_date()

        output: str = self._get_header(calendar_name=data["name"])

        year = current_year
        month = current_month

        for index in range(self.months_to_export):
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1

            all_tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)
            all_tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year,
                                                                         month=month,
                                                                         data=data,
                                                                         tasks=all_tasks,
                                                                         view_past_tasks=False)
            for day, tasks in all_tasks.items():
                for task in tasks:
                    output += self._get_task(task, year, month, day)

        output += self._get_footer()

        print(output)
        return True

    def _get_header(self, calendar_name: str) -> str:
        return f"""BEGIN:VCALENDAR
VERSION:2.0
METHOD:PUBLISH
X-WR-CALNAME:{calendar_name}
PRODID:-//{self.username}//{calendar_name}//EN
"""

    @staticmethod
    def _get_footer() -> str:
        return "END:VCALENDAR"

    def _get_task(self, task: Dict, year: int, month: int, day: int) -> str:
        month_str: str = str(month).zfill(2)
        day_str: str = str(day).zfill(2)
        time_start: str = "0000"
        time_end: str = "2359"

        if not task["is_all_day"]:
            time_start = task["due_time"].replace(":", "")
            if int(time_start[:2]) < 23:
                time_end = str(int(time_start[:2]) + 1) + time_start[2:]
            else:
                time_end = "2359"

        if task["details"] == "&nbsp;":
            task["details"] = ""
        else:
            task["details"] = task["details"].replace("<br>", " ")

        title = task["title"]

        if "repetition_type" in task:
            title = "{} [R]".format(title)

        return f"""BEGIN:VEVENT
UID:{task["id"]}@{self.username}
DTSTART;TZID={self.timezone}:{year}{month_str}{day_str}T{time_start}00
DTEND;TZID={self.timezone}:{year}{month_str}{day_str}T{time_end}00
SUMMARY:{title}
DESCRIPTION:{task["details"]}
END:VEVENT
"""
