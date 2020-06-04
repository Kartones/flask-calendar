import pytest
from flask_calendar.authorization import Authorization
from flask_calendar.calendar_data import CalendarData

EXISTING_USERNAME = "a_username"


@pytest.fixture
def authorization() -> Authorization:
    return Authorization(calendar_data=CalendarData("test/fixtures"))


def test_unauthorized_if_calendar_users_list_empty(authorization: Authorization,) -> None:
    assert authorization.can_access(username="an_irrelevant_user_id", calendar_id="sample_empty_data_file") is False


def test_unauthorized_if_calendar_user_not_in_list(authorization: Authorization,) -> None:
    assert authorization.can_access(username="an_irrelevant_user_id", calendar_id="sample_data_file") is False


def test_authorized_if_calendar_user_in_list(authorization: Authorization) -> None:
    assert authorization.can_access(username=EXISTING_USERNAME, calendar_id="sample_data_file") is True


def test_authorized_if_calendar_user_in_list_using_calendar_data(authorization: Authorization,) -> None:
    data = {"users": [EXISTING_USERNAME]}
    assert authorization.can_access(username=EXISTING_USERNAME, data=data) is True
