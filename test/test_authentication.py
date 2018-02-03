import pytest

from authentication import Authentication

EXISTING_USERNAME = "a_username"
CORRECT_PASSWORD = "a_password"


@pytest.fixture
def authentication() -> Authentication:
    return Authentication(data_folder="test/fixtures", password_salt="a test salt")


def test_not_authenticated_if_username_doesnt_exists(authentication: Authentication) -> None:
    assert authentication.is_valid(username="an_irrelevant_username", password="an_irrelevant_password") is False


def test_not_authenticated_if_password_doesnt_matches(authentication: Authentication) -> None:
    assert authentication.is_valid(username=EXISTING_USERNAME, password="an_irrelevant_password") is False


def test_authenticated_if_credentials_correct(authentication: Authentication) -> None:
    assert authentication.is_valid(username=EXISTING_USERNAME, password=CORRECT_PASSWORD) is True


def test_retrieve_user_data(authentication: Authentication) -> None:
    user = authentication.user_data(username=EXISTING_USERNAME)
    assert user is not None
    for key in ["username", "id", "password"]:
        assert key in user.keys()
        assert user[key] is not None


def test_password_is_not_stored_plain(authentication: Authentication) -> None:
    user = authentication.user_data(username=EXISTING_USERNAME)
    assert user["password"] != CORRECT_PASSWORD
    assert user["password"] == authentication._hash_password(CORRECT_PASSWORD)
