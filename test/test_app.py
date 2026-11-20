import pytest
from flask import Flask
from flask.testing import FlaskClient

from flask_calendar.constants import LINE_BREAK_MARKER, NEWLINE, SESSION_ID


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
        assert response.headers["Location"] in ["http://localhost/", "/"]
    else:
        assert response.headers["Location"] in ["http://localhost/login", "/login"]


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

    cookie = client.get_cookie(SESSION_ID)

    if cookie is not None:
        assert success and cookie.value is not None
    else:
        assert not success and cookie is None


def test_redirects_to_calendar_when_logged_in(client: FlaskClient) -> None:
    client.post("/do_login", data=dict(username="a_username", password="a_password"))
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] in ["http://localhost/sample/", "/sample/"]


def test_line_break_marker_is_available_to_templates(app: Flask) -> None:
    template = app.jinja_env.from_string("{{ details|replace(LINE_BREAK_MARKER, NEWLINE) }}")

    assert template.render(details=f"line1{LINE_BREAK_MARKER}line2") == f"line1{NEWLINE}line2"
