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
