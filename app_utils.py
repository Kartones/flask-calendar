from functools import wraps
from typing import Any, Callable
import uuid
from werkzeug.contrib.cache import SimpleCache

from flask import abort, redirect, request

import config
from gregorian_calendar import GregorianCalendar
from calendar_data import CalendarData
from authorization import Authorization


cache = SimpleCache()


def authenticated(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_id = request.cookies.get("sid")
        if session_id is None or not is_session_valid(str(session_id)):
            if request.headers.get("Content-Type", "") == "application/json":
                abort(401)
            return redirect("/login")
        return decorated_function(*args, **kwargs)
    return wrapper


def authorized(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        username = get_session_username(str(request.cookies.get("sid")))
        authorization = Authorization(calendar_data=CalendarData(data_folder=config.DATA_FOLTER))
        if "calendar_id" not in kwargs:
            raise ValueError("calendar_id")
        calendar_id = str(kwargs["calendar_id"])
        if not authorization.can_access(username=username, calendar_id=calendar_id):
            abort(403)
        return decorated_function(*args, **kwargs)
    return wrapper


def previous_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


def next_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


def new_session_id() -> str:
    return str(uuid.uuid4())


def is_session_valid(session_id: str) -> bool:
    return cache.get(session_id) is not None


def add_session(session_id: str, username: str) -> None:
    cache.set(session_id, username, timeout=2678400)    # 1 month


def get_session_username(session_id: str) -> str:
    return str(cache.get(session_id))
