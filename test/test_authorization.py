import pytest

from calendar_data import CalendarData
from authorization import Authorization

EXISTING_USER_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def authorization() -> Authorization:
    return Authorization(calendar_data=CalendarData("test/fixtures"))


def test_unauthorized_if_calendar_users_list_empty(authorization: Authorization) -> None:
    assert authorization.can_access(user_id="an_irrelevant_user_id", calendar_id="sample_empty_data_file") is False


def test_unauthorized_if_calendar_user_not_in_list(authorization: Authorization) -> None:
    assert authorization.can_access(user_id="an_irrelevant_user_id", calendar_id="sample_data_file") is False


def test_authorized_if_calendar_user_in_list(authorization: Authorization) -> None:
    assert authorization.can_access(user_id=EXISTING_USER_ID, calendar_id="sample_data_file") is True


def test_authorized_if_calendar_user_in_list_using_calendar_data(authorization: Authorization) -> None:
    data = {
        "users": [EXISTING_USER_ID]
    }
    assert authorization.can_access(user_id=EXISTING_USER_ID, data=data) is True
