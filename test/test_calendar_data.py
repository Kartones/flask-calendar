from unittest.mock import ANY, patch, MagicMock

import pytest

from calendar_data import CalendarData


@pytest.fixture
def calendar_data() -> CalendarData:
    return CalendarData("test/fixtures")


def test_error_retrieving_tasks_from_calendar(subtests, calendar_data: CalendarData) -> None:
    test_data = [
        {"year": 2001, "month": 1, "calendar_id": None, "data": None},
        {"year": 2001, "month": 1, "calendar_id": None, "data": {}},
        {"year": 2001, "month": 1, "calendar_id": None, "data": {"tasks": {}}},
        {"year": 2001, "month": 1, "calendar_id": None, "data": {"tasks": {
            "normal": {},
            "hidden_repetition": {}}}},
        {"year": 2001, "month": 1, "calendar_id": None, "data": {"tasks": {
            "normal": {},
            "repetition": {}}}},
        {"year": 2001, "month": 1, "calendar_id": None, "data": {"tasks": {
            "repetition": {},
            "hidden_repetition": {}}}},
    ]
    for data in test_data:
        with subtests.test(data=data["data"]):
            with pytest.raises(ValueError):
                calendar_data.tasks_from_calendar(**data)


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
    assert tasks["25"][0]["id"] in [0, 1]
    assert tasks["25"][1]["id"] in [0, 1]
    assert tasks["25"][0]["id"] != tasks["25"][1]["id"]


def test_loads_normal_tasks_from_calendar_given_data(calendar_data: CalendarData) -> None:
    data = calendar_data.load_calendar("sample_data_file")
    tasks = calendar_data.tasks_from_calendar(year=2017, month=12, data=data)
    assert len(tasks) == 1
    assert len(tasks["25"]) == 2
    assert tasks["25"][0]["id"] in [0, 1]
    assert tasks["25"][1]["id"] in [0, 1]
    assert tasks["25"][0]["id"] != tasks["25"][1]["id"]


def test_joins_repetitive_tasks_with_normal_ones(calendar_data: CalendarData) -> None:
    year = 2017
    month = 11
    data = calendar_data.load_calendar("sample_data_file")

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)
    assert len(tasks) == 1

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks)
    assert len(tasks) > 0
    repetitive_weekly_weekday_task_ocurrences = 4    # month has 4 mondays
    repetitive_weekly_weekday_3_task_ocurrences = 5  # month has 5 thursdays
    repetitive_monthly_weekday_task_ocurrences = 1
    repetitive_monthly_monthday_task_ocurrences = 1

    # We"re counting the number of days with tasks, not the exact number of tasks (day 6 has 2 tasks)
    assert len(tasks) == (repetitive_weekly_weekday_task_ocurrences + repetitive_monthly_weekday_task_ocurrences +
                          repetitive_monthly_monthday_task_ocurrences + repetitive_weekly_weekday_3_task_ocurrences)
    assert len(tasks["6"]) == 2

    # Normal task should be first (as repetitive ones are appended afterwards)
    assert tasks["6"][0]["id"] == 4
    assert "repetition_value" not in tasks["6"][0]
    assert "repetition_value" in tasks["6"][1]
    assert tasks["6"][1]["repetition_value"] == 0
    assert tasks["6"][1]["repetition_subtype"] == CalendarData.REPETITION_SUBTYPE_WEEK_DAY
    assert tasks["6"][1]["repetition_type"] == CalendarData.REPETITION_TYPE_WEEKLY


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
    calendar_id = "sample_empty_data_file"

    result = calendar_data.create_task(calendar_id=calendar_id, year=year, month=month, day=day,
                                       title=title,
                                       is_all_day=is_all_day, due_time=due_time, details=details, color=color,
                                       has_repetition=has_repetition, repetition_type=repetition_type,
                                       repetition_subtype=repetition_subtype, repetition_value=repetition_value)
    assert result is True

    save_calendar_mock.assert_called_once_with(contents=ANY, filename=calendar_id)
    args, kwargs = save_calendar_mock.call_args
    assert "contents" in kwargs
    assert "tasks" in kwargs["contents"]
    assert "normal" in kwargs["contents"]["tasks"]
    assert str(year) in kwargs["contents"]["tasks"]["normal"]
    assert str(month) in kwargs["contents"]["tasks"]["normal"][str(year)]
    assert str(day) in kwargs["contents"]["tasks"]["normal"][str(year)][str(month)]
    assert len(kwargs["contents"]["tasks"]["normal"][str(year)][str(month)][str(day)]) == 1
    assert "title" in kwargs["contents"]["tasks"]["normal"][str(year)][str(month)][str(day)][0]
    assert kwargs["contents"]["tasks"]["normal"][str(year)][str(month)][str(day)][0]["title"] == title


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


def test_if_dont_want_to_view_past_tasks_dont_appear(calendar_data: CalendarData) -> None:
    all_tasks = calendar_data.tasks_from_calendar(year=2001, month=1, view_past_tasks=True,
                                                  calendar_id="past_normal_tasks")
    non_past_tasks = calendar_data.tasks_from_calendar(year=2001, month=2, view_past_tasks=False,
                                                       calendar_id="past_normal_tasks")

    assert len(all_tasks) > len(non_past_tasks)
    assert len(non_past_tasks) == 0


def test_existing_individual_task_retrieval(calendar_data: CalendarData) -> None:
    task_id = 4
    task = calendar_data.task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, day=6, task_id=4)
    assert task is not None
    assert task["id"] == task_id
    assert task["is_all_day"] is True


def test_non_existing_individual_task_retrieval(calendar_data: CalendarData) -> None:
    with pytest.raises(ValueError):
        calendar_data.task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, day=6, task_id=0)


def test_existing_repetitive_task_retrieval(calendar_data: CalendarData) -> None:
    task_id = 2
    task = calendar_data.repetitive_task_from_calendar(calendar_id="sample_data_file", year=2017, month=11,
                                                       task_id=task_id)
    assert task is not None
    assert task["id"] == task_id
    assert task["is_all_day"] is True


def test_non_existing_repetitive_task_retrieval(calendar_data: CalendarData) -> None:
    with pytest.raises(IndexError):
        calendar_data.repetitive_task_from_calendar(calendar_id="sample_data_file", year=2017, month=11, task_id=111)
