import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, cast

import flask_calendar.constants as constants
from flask import current_app
from flask_calendar.gregorian_calendar import GregorianCalendar

KEY_TASKS = "tasks"
KEY_USERS = "users"
KEY_NORMAL_TASK = "normal"
KEY_REPETITIVE_TASK = "repetition"
KEY_REPETITIVE_HIDDEN_TASK = "hidden_repetition"


class CalendarData:

    REPETITION_TYPE_WEEKLY = "w"
    REPETITION_TYPE_MONTHLY = "m"
    REPETITION_SUBTYPE_WEEK_DAY = "w"
    REPETITION_SUBTYPE_MONTH_DAY = "m"

    def __init__(self, data_folder: str, first_weekday: int = constants.WEEK_START_DAY_MONDAY) -> None:
        self.data_folder = data_folder
        self.gregorian_calendar = GregorianCalendar
        self.gregorian_calendar.setfirstweekday(first_weekday)

    def load_calendar(self, filename: str) -> Dict:
        with open(os.path.join(".", self.data_folder, "{}.json".format(filename))) as file:
            contents = json.load(file)
        if type(contents) is not dict:
            raise ValueError("Error loading calendar from file '{}'".format(filename))
        return cast(Dict, contents)

    def users_list(self, data: Optional[Dict] = None, calendar_id: Optional[str] = None) -> List:
        if data is None:
            if calendar_id is None:
                raise ValueError("Need to provide either calendar_id or loaded data")
            else:
                data = self.load_calendar(calendar_id)
        if KEY_USERS not in data:
            raise ValueError("Incomplete data for calendar id '{}'".format(calendar_id))

        return cast(List, data[KEY_USERS])

    def user_details(self, username: str, data: Optional[Dict] = None, calendar_id: Optional[str] = None,) -> Dict:
        if data is None:
            if calendar_id is None:
                raise ValueError("Need to provide either calendar_id or loaded data")
            else:
                data = self.load_calendar(calendar_id)
        if KEY_USERS not in data:
            raise ValueError("Incomplete data for calendar id '{}'".format(calendar_id))

        return cast(Dict, data[KEY_USERS][username])

    @staticmethod
    def is_past(year: int, month: int, current_year: int, current_month: int) -> bool:
        if year < current_year:
            return True
        elif year == current_year:
            if month < current_month:
                return True
        return False

    def tasks_from_calendar(self, year: int, month: int, data: Dict) -> Dict:
        if not data or KEY_TASKS not in data:
            raise ValueError("Incomplete data for calendar")
        if not all(
            [
                KEY_NORMAL_TASK in data[KEY_TASKS],
                KEY_REPETITIVE_TASK in data[KEY_TASKS],
                KEY_REPETITIVE_HIDDEN_TASK in data[KEY_TASKS],
            ]
        ):
            raise ValueError("Incomplete data for calendar")

        tasks = {}  # type: Dict

        (current_day, current_month, current_year,) = self.gregorian_calendar.current_date()

        for day in self.gregorian_calendar.month_days(year, month):
            month_str = str(day.month)
            year_str = str(day.year)
            if (
                year_str in data[KEY_TASKS][KEY_NORMAL_TASK]
                and month_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str]
                and month_str not in tasks
            ):
                tasks[month_str] = data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]

        return tasks

    def hide_past_tasks(self, year: int, month: int, tasks: Dict) -> None:
        (current_day, current_month, current_year,) = self.gregorian_calendar.current_date()

        for day in self.gregorian_calendar.month_days(year, month):
            month_str = str(day.month)

            # empty past months and be careful of future dates, which might not have tasks
            if self.is_past(day.year, day.month, current_year, current_month) or month_str not in tasks:
                tasks[month_str] = {}

            for task_day_number in tasks[month_str]:
                if day.month == current_month and int(task_day_number) < current_day:
                    tasks[month_str][task_day_number] = []

    def task_from_calendar(self, calendar_id: str, year: int, month: int, day: int, task_id: int) -> Dict:
        data = self.load_calendar(calendar_id)

        year_str = str(year)
        month_str = str(month)
        day_str = str(day)

        for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
            if task["id"] == task_id:
                task["repeats"] = False
                task["date"] = self.date_for_frontend(year, month, day)
                return cast(Dict, task)
        raise ValueError("Task id '{}' not found".format(task_id))

    def repetitive_task_from_calendar(self, calendar_id: str, year: int, month: int, task_id: int) -> Dict:
        data = self.load_calendar(calendar_id)

        task = [task for task in data[KEY_TASKS][KEY_REPETITIVE_TASK] if task["id"] == task_id][0]  # type: Dict
        task["repeats"] = True
        task["date"] = self.date_for_frontend(year, month, 1)
        return task

    @staticmethod
    def date_for_frontend(year: int, month: int, day: int) -> str:
        return "{0}-{1:02d}-{2:02d}".format(int(year), int(month), int(day))

    def add_repetitive_tasks_from_calendar(self, year: int, month: int, data: Dict, tasks: Dict) -> Dict:
        (current_day, current_month, current_year,) = self.gregorian_calendar.current_date()

        repetitive_tasks = self._repetitive_tasks_from_calendar(year, month, data)

        for repetitive_tasks_month in repetitive_tasks:
            for day, day_tasks in repetitive_tasks[repetitive_tasks_month].items():
                if repetitive_tasks_month not in tasks:
                    tasks[repetitive_tasks_month] = {}
                if day not in tasks[repetitive_tasks_month]:
                    tasks[repetitive_tasks_month][day] = []

                for task in day_tasks:
                    tasks[repetitive_tasks_month][day].append(task)

        return tasks

    def delete_task(self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id: int,) -> None:
        deleted = False
        data = self.load_calendar(calendar_id)

        if (
            year_str in data[KEY_TASKS][KEY_NORMAL_TASK]
            and month_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str]
            and day_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]
        ):
            for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
                if task["id"] == task_id:
                    data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].pop(index)
                    deleted = True

        if not deleted:
            for index, task in enumerate(data[KEY_TASKS][KEY_REPETITIVE_TASK]):
                if task["id"] == task_id:
                    data[KEY_TASKS][KEY_REPETITIVE_TASK].pop(index)
                    if str(task_id) in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
                        del data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][str(task_id)]

        self._save_calendar(data, filename=calendar_id)

    def update_task_day(
        self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id: int, new_day_str: str,
    ) -> None:
        data = self.load_calendar(calendar_id)

        task_to_update = None
        for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
            if task["id"] == task_id:
                task_to_update = data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].pop(index)

        if task_to_update is None:
            return

        if new_day_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]:
            data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][new_day_str] = []
        data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][new_day_str].append(task_to_update)

        self._save_calendar(data, filename=calendar_id)

    def create_task(
        self,
        calendar_id: str,
        year: Optional[int],
        month: Optional[int],
        day: Optional[int],
        title: str,
        is_all_day: bool,
        start_time: str,
        details: str,
        color: str,
        has_repetition: bool,
        repetition_type: Optional[str],
        repetition_subtype: Optional[str],
        repetition_value: int,
        end_time: Optional[str] = None,
    ) -> bool:
        details = details if len(details) > 0 else "&nbsp;"
        data = self.load_calendar(calendar_id)

        new_task = {
            "id": int(time.time()),
            "color": color,
            "start_time": start_time,
            "end_time": end_time if end_time else start_time,
            "is_all_day": is_all_day,
            "title": title,
            "details": details,
        }
        if has_repetition:
            if repetition_type == self.REPETITION_SUBTYPE_MONTH_DAY and repetition_value == 0:
                return False
            new_task["repetition_type"] = repetition_type
            new_task["repetition_subtype"] = repetition_subtype
            new_task["repetition_value"] = repetition_value
            data[KEY_TASKS][KEY_REPETITIVE_TASK].append(new_task)
        else:
            if year is None or month is None or day is None:
                return False
            year_str = str(year)
            month_str = str(month)
            day_str = str(day)
            if year_str not in data[KEY_TASKS][KEY_NORMAL_TASK]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str] = {}
            if month_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str] = {}
            if day_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str] = []
            data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].append(new_task)

        self._save_calendar(data, filename=calendar_id)
        return True

    def hide_repetition_task_instance(
        self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id_str: str,
    ) -> None:
        data = self.load_calendar(calendar_id)

        if task_id_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str] = {}
        if year_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str] = {}
        if month_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str][month_str] = {}
        data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str][month_str][day_str] = True

        self._save_calendar(data, filename=calendar_id)

    @staticmethod
    def add_task_to_list(tasks: Dict, day_str: str, month_str: str, new_task: Dict) -> None:
        if day_str not in tasks[month_str]:
            tasks[month_str][day_str] = []
        tasks[month_str][day_str].append(new_task)

    def _repetitive_tasks_from_calendar(self, year: int, month: int, data: Dict) -> Dict:
        if KEY_TASKS not in data:
            ValueError("Incomplete data for calendar")
        if KEY_REPETITIVE_TASK not in data[KEY_TASKS]:
            ValueError("Incomplete data for calendar")

        repetitive_tasks = {}  # type: Dict
        year_and_months = set(
            [(source_day.year, source_day.month) for source_day in self.gregorian_calendar.month_days(year, month)]
        )

        for source_year, source_month in year_and_months:
            month_str = str(source_month)
            year_str = str(source_year)
            repetitive_tasks[month_str] = {}

            for task in data[KEY_TASKS][KEY_REPETITIVE_TASK]:
                id_str = str(task["id"])
                monthly_task_assigned = False
                for week in self.gregorian_calendar.month_days_with_weekday(source_year, source_month):
                    for weekday, day in enumerate(week):
                        if day == 0:
                            continue
                        day_str = str(day)
                        if (
                            task["repetition_type"] == self.REPETITION_TYPE_WEEKLY
                            and not self._is_repetition_hidden_for_day(data, id_str, year_str, month_str, str(day))
                            and task["repetition_value"] == weekday
                        ):
                            self.add_task_to_list(repetitive_tasks, day_str, month_str, task)
                        elif task["repetition_type"] == self.REPETITION_TYPE_MONTHLY and not self._is_repetition_hidden(
                            data, id_str, year_str, month_str
                        ):
                            if task["repetition_subtype"] == self.REPETITION_SUBTYPE_WEEK_DAY:
                                if task["repetition_value"] == weekday and not monthly_task_assigned:
                                    monthly_task_assigned = True
                                    self.add_task_to_list(repetitive_tasks, day_str, month_str, task)
                            else:
                                if task["repetition_value"] == day:
                                    self.add_task_to_list(repetitive_tasks, day_str, month_str, task)

        return repetitive_tasks

    @staticmethod
    def _is_repetition_hidden_for_day(data: Dict, id_str: str, year_str: str, month_str: str, day_str: str) -> bool:
        if id_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            if (
                year_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str]
                and month_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str]
                and day_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str][month_str]
            ):
                return True
        return False

    @staticmethod
    def _is_repetition_hidden(data: Dict, id_str: str, year_str: str, month_str: str) -> bool:
        if id_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            if (
                year_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str]
                and month_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str]
            ):
                return True
        return False

    def _save_calendar(self, data: Dict, filename: str) -> None:
        self._clear_empty_entries(data)
        self._clear_past_hidden_entries(data)
        with open(os.path.join(".", self.data_folder, "{}.json".format(filename)), "w+") as file:
            json.dump(data, file)

    @staticmethod
    def _clear_empty_entries(data: Dict) -> None:
        years_to_delete = []

        for year in data[KEY_TASKS][KEY_NORMAL_TASK]:
            months_to_delete = []
            for month in data[KEY_TASKS][KEY_NORMAL_TASK][year]:
                days_to_delete = []
                for day in data[KEY_TASKS][KEY_NORMAL_TASK][year][month]:
                    if len(data[KEY_TASKS][KEY_NORMAL_TASK][year][month][day]) == 0:
                        days_to_delete.append(day)
                for day in days_to_delete:
                    del data[KEY_TASKS][KEY_NORMAL_TASK][year][month][day]
                if len(data[KEY_TASKS][KEY_NORMAL_TASK][year][month]) == 0:
                    months_to_delete.append(month)
            for month in months_to_delete:
                del data[KEY_TASKS][KEY_NORMAL_TASK][year][month]
            if len(data[KEY_TASKS][KEY_NORMAL_TASK][year]) == 0:
                years_to_delete.append(year)

        for year in years_to_delete:
            del data[KEY_TASKS][KEY_NORMAL_TASK][year]

    def _clear_past_hidden_entries(self, data: Dict) -> None:
        _, current_month, current_year = self.gregorian_calendar.current_date()
        # normalize to 1st day of month
        current_date = datetime(current_year, current_month, 1, 0, 0)
        tasks_to_delete = []

        for task_id in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            for year in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id]:
                for month in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id][year]:
                    task_date = datetime(int(year), int(month), 1, 0, 0)
                    if (current_date - task_date).days > current_app.config["DAYS_PAST_TO_KEEP_HIDDEN_TASKS"]:
                        tasks_to_delete.append((year, month, task_id))

        for task_info in tasks_to_delete:
            year, month, task_id = task_info
            del data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id][year][month]
            if len(data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id]) == 0:
                del data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id]
