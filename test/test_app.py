import pytest
from flask.testing import FlaskClient
from flask_calendar.constants import SESSION_ID


@pytest.mark.parametrize(
    ("username", "password", "success"),
    (
        ("", "", False),
        ("wrong_username", "", False),
        ("a_username", "", False),
        ("a_username", "wrong_password", False),
        ("a_username", "a_password", True),
    ),
)
def test_login_credentials(client: FlaskClient, username: str, password: str, success: bool) -> None:
    response = client.post("/do_login", data=dict(username=username, password=password))
    assert response.status_code == 302
    if success:
        assert response.headers["Location"] == "http://localhost/"
    else:
        assert response.headers["Location"] == "http://localhost/login"


@pytest.mark.parametrize(
    ("username", "password", "success"),
    (
        ("", "", False),
        ("wrong_username", "", False),
        ("a_username", "", False),
        ("a_username", "wrong_password", False),
        ("a_username", "a_password", True),
    ),
)
def test_session_id_cookie_set_when_logged_in(client: FlaskClient, username: str, password: str, success: bool) -> None:
    response = client.post("/do_login", data=dict(username=username, password=password))
    assert response.status_code == 302
    cookie = next((c for c in client.cookie_jar), None)
    if cookie is not None:
        assert success and cookie.name == SESSION_ID
    else:
        assert not success and cookie is None


def test_redirects_to_calendar_when_logged_in(client: FlaskClient) -> None:
    client.post("/do_login", data=dict(username="a_username", password="a_password"))
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/sample/"
