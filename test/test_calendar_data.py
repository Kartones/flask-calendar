from typing import Dict
from unittest.mock import ANY, MagicMock, patch

import pytest
from flask_calendar.calendar_data import CalendarData


@pytest.fixture
def calendar_data() -> CalendarData:
    return CalendarData("test/fixtures")


@pytest.fixture
def sample_data_file_data(calendar_data: CalendarData) -> Dict:
    return calendar_data.load_calendar(filename="sample_data_file")


@pytest.fixture
def past_normal_tasks_data(calendar_data: CalendarData) -> Dict:
    return calendar_data.load_calendar(filename="past_normal_tasks")


@pytest.mark.parametrize(
    "year, month, data",
    [
        (2001, 1, None),
        (2001, 1, {}),
        (2001, 1, {"tasks": {}}),
        (2001, 1, {"tasks": {"normal": {}, "hidden_repetition": {}}}),
        (2001, 1, {"tasks": {"normal": {}, "repetition": {}}}),
        (2001, 1, {"tasks": {"repetition": {}, "hidden_repetition": {}}}),
    ],
)
def test_error_retrieving_tasks_from_calendar(year: int, month: int, data: Dict, calendar_data: CalendarData) -> None:
    with pytest.raises(ValueError):
        calendar_data.tasks_from_calendar(year, month, data)


def test_loads_a_valid_data_file(calendar_data: CalendarData, sample_data_file_data: Dict) -> None:
    # If fails at loading time fixture itself will error
    calendar = sample_data_file_data
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


def test_loads_normal_tasks_from_calendar_given_data(calendar_data: CalendarData, sample_data_file_data: Dict) -> None:
    year = 2017
    month = 12
    month_str = str(month)

    tasks = calendar_data.tasks_from_calendar(year, month, sample_data_file_data)
    assert len(tasks[month_str]) == 1
    assert len(tasks[month_str]["25"]) == 2
    assert tasks[month_str]["25"][0]["id"] in [0, 1]
    assert tasks[month_str]["25"][1]["id"] in [0, 1]
    assert tasks[month_str]["25"][0]["id"] != tasks[month_str]["25"][1]["id"]


def test_joins_repetitive_tasks_with_normal_ones(calendar_data: CalendarData, sample_data_file_data: Dict) -> None:
    year = 2017
    month = 11
    month_str = str(month)

    tasks = calendar_data.tasks_from_calendar(year, month, sample_data_file_data)
    assert len(tasks[month_str]) == 1

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, sample_data_file_data, tasks)
    assert len(tasks[month_str]) > 0
    # month has 4 mondays
    repetitive_weekly_weekday_task_ocurrences = 4
    # month has 5 thursdays
    repetitive_weekly_weekday_3_task_ocurrences = 5
    repetitive_monthly_weekday_task_ocurrences = 1
    repetitive_monthly_monthday_task_ocurrences = 1

    # We're counting the number of days with tasks, not the exact number of tasks (day 6 has 2 tasks)
    assert len(tasks[month_str]) == (
        repetitive_weekly_weekday_task_ocurrences
        + repetitive_monthly_weekday_task_ocurrences
        + repetitive_monthly_monthday_task_ocurrences
        + repetitive_weekly_weekday_3_task_ocurrences
    )
    assert len(tasks[month_str]["6"]) == 2

    # Normal task should be first (as repetitive ones are appended afterwards)
    assert tasks[month_str]["6"][0]["id"] == 4
    assert "repetition_value" not in tasks[month_str]["6"][0]
    assert "repetition_value" in tasks[month_str]["6"][1]
    assert tasks[month_str]["6"][1]["repetition_value"] == 0
    assert tasks[month_str]["6"][1]["repetition_subtype"] == CalendarData.REPETITION_SUBTYPE_WEEK_DAY
    assert tasks[month_str]["6"][1]["repetition_type"] == CalendarData.REPETITION_TYPE_WEEKLY


@patch("flask_calendar.calendar_data.CalendarData._save_calendar")
def test_creates_new_normal_task(save_calendar_mock: MagicMock, calendar_data: CalendarData) -> None:
    year = 2017
    month = 12
    day = 10
    title = "an irrelevant title"
    is_all_day = True
    start_time = "00:00"
    details = ""
    color = "an_irrelevant_color"
    has_repetition = False
    repetition_type = ""
    repetition_subtype = ""
    repetition_value = 0
    calendar_id = "sample_empty_data_file"

    result = calendar_data.create_task(
        calendar_id=calendar_id,
        year=year,
        month=month,
        day=day,
        title=title,
        is_all_day=is_all_day,
        start_time=start_time,
        details=details,
        color=color,
        has_repetition=has_repetition,
        repetition_type=repetition_type,
        repetition_subtype=repetition_subtype,
        repetition_value=repetition_value,
    )
    assert result is True

    save_calendar_mock.assert_called_once_with(ANY, filename=calendar_id)
    call_args, _ = save_calendar_mock.call_args
    data = call_args[0]
    assert "tasks" in data
    assert "normal" in data["tasks"]
    assert str(year) in data["tasks"]["normal"]
    assert str(month) in data["tasks"]["normal"][str(year)]
    assert str(day) in data["tasks"]["normal"][str(year)][str(month)]
    assert len(data["tasks"]["normal"][str(year)][str(month)][str(day)]) == 1
    assert "title" in data["tasks"]["normal"][str(year)][str(month)][str(day)][0]
    assert data["tasks"]["normal"][str(year)][str(month)][str(day)][0]["title"] == title


@patch("flask_calendar.calendar_data.CalendarData._save_calendar")
def test_creates_task_with_start_and_end_dates(save_calendar_mock: MagicMock, calendar_data: CalendarData) -> None:
    year = 2017
    month = 12
    day = 10
    title = "an irrelevant title"
    is_all_day = False
    start_time = "12:00"
    end_time = "13:00"
    details = ""
    color = "an_irrelevant_color"
    has_repetition = False
    repetition_type = ""
    repetition_subtype = ""
    repetition_value = 0
    calendar_id = "sample_empty_data_file"

    result = calendar_data.create_task(
        calendar_id=calendar_id,
        year=year,
        month=month,
        day=day,
        title=title,
        is_all_day=is_all_day,
        start_time=start_time,
        end_time=end_time,
        details=details,
        color=color,
        has_repetition=has_repetition,
        repetition_type=repetition_type,
        repetition_subtype=repetition_subtype,
        repetition_value=repetition_value,
    )
    assert result is True

    save_calendar_mock.assert_called_once_with(ANY, filename=calendar_id)
    call_args, _ = save_calendar_mock.call_args
    data = call_args[0]
    assert "tasks" in data
    assert "normal" in data["tasks"]
    assert str(year) in data["tasks"]["normal"]
    assert str(month) in data["tasks"]["normal"][str(year)]
    assert str(day) in data["tasks"]["normal"][str(year)][str(month)]
    assert len(data["tasks"]["normal"][str(year)][str(month)][str(day)]) == 1

    task_data = data["tasks"]["normal"][str(year)][str(month)][str(day)][0]

    assert "title" in task_data
    assert task_data["title"] == title
    assert task_data["is_all_day"] is False
    assert task_data["start_time"] == start_time
    assert task_data["end_time"] == end_time


def test_hidden_montly_monthday_repetitions_dont_appear(calendar_data: CalendarData,) -> None:
    year = 2017
    month = 12
    data = calendar_data.load_calendar("repetitive_monthly_monthday_hidden_task_data_file")

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)

    assert str(month) not in tasks


def test_hidden_montly_weekday_repetitions_dont_appear(calendar_data: CalendarData,) -> None:
    year = 2017
    month = 12
    data = calendar_data.load_calendar("repetitive_monthly_weekday_hidden_task_data_file")

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)

    assert str(month) not in tasks


def test_tasks_can_be_filtered_after_retrieval(calendar_data: CalendarData, past_normal_tasks_data: Dict) -> None:
    year = 2001

    tasks = calendar_data.tasks_from_calendar(year, 1, past_normal_tasks_data)
    assert len(tasks["1"]) > 0
    # if we switch to next month, month 1 should become empty
    calendar_data.hide_past_tasks(year, 2, tasks)
    assert len(tasks["1"]) == 0


def test_existing_individual_task_retrieval(calendar_data: CalendarData) -> None:
    task_id = 4

    task = calendar_data.task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, day=6, task_id=task_id)
    assert task is not None
    assert task["id"] == task_id
    assert task["is_all_day"] is True


def test_non_existing_individual_task_retrieval(calendar_data: CalendarData) -> None:
    with pytest.raises(ValueError):
        calendar_data.task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, day=6, task_id=0)


def test_existing_repetitive_task_retrieval(calendar_data: CalendarData) -> None:
    task_id = 2
    task = calendar_data.repetitive_task_from_calendar(
        calendar_id="sample_data_file", year=2017, month=11, task_id=task_id
    )
    assert task is not None
    assert task["id"] == task_id
    assert task["is_all_day"] is True


def test_non_existing_repetitive_task_retrieval(calendar_data: CalendarData) -> None:
    with pytest.raises(IndexError):
        calendar_data.repetitive_task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, task_id=111)
