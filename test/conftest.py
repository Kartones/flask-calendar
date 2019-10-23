import pytest
from flask import Flask
from flask_calendar.app import create_app


@pytest.fixture
def app() -> Flask:
    return create_app()
