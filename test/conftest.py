import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_calendar.app import create_app


@pytest.fixture
def app() -> Flask:
    return create_app({"TESTING": True, "FAILED_LOGIN_DELAY_BASE": 0})


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
