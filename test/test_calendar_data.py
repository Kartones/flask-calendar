from unittest.mock import patch, MagicMock

import pytest

from calendar_data import CalendarData


@pytest.fixture
def calendar_data() -> CalendarData:
    return CalendarData("test/fixtures")


def test_loads_a_valid_data_file(calendar_data: CalendarData) -> None:
    calendar = calendar_data.load_calendar("sample_data_file")
    assert calendar is not None
    assert type(calendar) == dict
    assert "tasks" in calendar
    assert "repetition" in calendar["tasks"]
    assert len(calendar["tasks"]["repetition"]) > 0
    assert "normal" in calendar["tasks"]
    assert "2017" in calendar["tasks"]["normal"]
    assert "12" in calendar["tasks"]["normal"]["2017"]
    assert "25" in calendar["tasks"]["normal"]["2017"]["12"]
    assert len(calendar["tasks"]["normal"]["2017"]["12"]["25"]) == 2
    task = calendar["tasks"]["normal"]["2017"]["12"]["25"][1]
    assert task["id"] == 1
    assert task["is_all_day"] is False


def test_loads_normal_tasks_from_calendar_given_calendar_id(calendar_data: CalendarData) -> None:
    tasks = calendar_data.tasks_from_calendar(year=2017, month=12, calendar_id="sample_data_file")
    assert len(tasks) == 1
    assert len(tasks["25"]) == 2


def test_loads_normal_tasks_from_calendar_given_data(calendar_data: CalendarData) -> None:
    data = calendar_data.load_calendar("sample_data_file")
    tasks = calendar_data.tasks_from_calendar(year=2017, month=12, data=data)
    assert len(tasks) == 1
    assert len(tasks["25"]) == 2

    # TODO: expand test checking details, etc.


def test_joins_repetitive_tasks_with_normal_ones(calendar_data: CalendarData) -> None:
    year = 2017
    month = 11
    data = calendar_data.load_calendar("sample_data_file")

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)
    assert len(tasks) == 0

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)
    assert len(tasks) > 0
    repetitive_weekly_weekday_task_ocurrences = 4    # month has 4 mondays
    repetitive_weekly_weekday_3_task_ocurrences = 5  # month has 5 thursdays
    repetitive_monthly_weekday_task_ocurrences = 1
    repetitive_monthly_monthday_task_ocurrences = 1

    assert len(tasks) == (repetitive_weekly_weekday_task_ocurrences + repetitive_monthly_weekday_task_ocurrences +
                          repetitive_monthly_monthday_task_ocurrences + repetitive_weekly_weekday_3_task_ocurrences)

    # TODO: expand test checking day, etc.


def test_add_repetitive_tasks_calendar_data(calendar_data: CalendarData) -> None:
    year = 2017
    month = 11
    data = calendar_data.load_calendar("sample_data_file")

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)
    assert len(tasks) > 0
    repetitive_weekly_weekday_task_ocurrences = 4    # month has 4 mondays
    repetitive_weekly_weekday_3_task_ocurrences = 5  # month has 5 thursdays
    repetitive_monthly_weekday_task_ocurrences = 1
    repetitive_monthly_monthday_task_ocurrences = 1

    assert len(tasks) == (repetitive_weekly_weekday_task_ocurrences + repetitive_monthly_weekday_task_ocurrences +
                          repetitive_monthly_monthday_task_ocurrences + repetitive_weekly_weekday_3_task_ocurrences)

    # TODO: expand test checking day, etc.


@patch("calendar_data.CalendarData._save_calendar")
def test_creates_new_normal_task(save_calendar_mock: MagicMock, calendar_data: CalendarData) -> None:
    year = 2017
    month = 12
    day = 10
    title = "an irrelevant title"
    is_all_day = True
    due_time = "00:00"
    details = ""
    color = "an_irrelevant_color"
    has_repetition = False
    repetition_type = ""
    repetition_subtype = ""
    repetition_value = 0

    result = calendar_data.create_task(calendar_id="sample_empty_data_file", year=year, month=month, day=day,
                                       title=title,
                                       is_all_day=is_all_day, due_time=due_time, details=details, color=color,
                                       has_repetition=has_repetition, repetition_type=repetition_type,
                                       repetition_subtype=repetition_subtype, repetition_value=repetition_value)
    assert result is True

    # TODO: check actual fields being added etc.
    # (contents=data, filename=calendar_id)
    save_calendar_mock.assert_called_once()


def test_hidden_montly_monthday_repetitions_dont_appear(calendar_data: CalendarData) -> None:
    year = 2017
    month = 12
    data = calendar_data.load_calendar("repetitive_monthly_monthday_hidden_task_data_file")
    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)
    assert len(tasks) == 0


def test_hidden_montly_weekday_repetitions_dont_appear(calendar_data: CalendarData) -> None:
    year = 2017
    month = 12
    data = calendar_data.load_calendar("repetitive_monthly_weekday_hidden_task_data_file")
    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)
    assert len(tasks) == 0
