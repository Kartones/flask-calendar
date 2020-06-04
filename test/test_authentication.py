import pytest
from flask_calendar.authentication import Authentication

EXISTING_USERNAME = "a_username"
CORRECT_PASSWORD = "a_password"


@pytest.fixture
def authentication() -> Authentication:
    return Authentication(data_folder="test/fixtures", password_salt="a test salt", failed_login_delay_base=0,)


@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("an_irrelevant_username", "an_irrelevant_password", False),
        (EXISTING_USERNAME, "an_irrelevant_password", False),
        (EXISTING_USERNAME, CORRECT_PASSWORD, True),
    ],
)
def test_is_valid_authentication(authentication: Authentication, username: str, password: str, expected: bool) -> None:
    assert authentication.is_valid(username=username, password=password) is expected


def test_retrieve_user_data(authentication: Authentication) -> None:
    user = authentication.user_data(username=EXISTING_USERNAME)
    assert user is not None
    for key in ["username", "password", "default_calendar"]:
        assert key in user
        assert user[key] is not None


def test_password_is_not_stored_plain(authentication: Authentication) -> None:
    user = authentication.user_data(username=EXISTING_USERNAME)
    assert user["password"] != CORRECT_PASSWORD
    assert user["password"] == authentication._hash_password(CORRECT_PASSWORD)
