from functools import wraps
from typing import Any, Callable
import uuid
from werkzeug.contrib.cache import SimpleCache

from flask import abort, redirect, request

import config
from gregorian_calendar import GregorianCalendar


cache = SimpleCache()


def authenticated(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_id = request.cookies.get("sid")
        if session_id is None or not is_session_valid(session_id):
            # TODO: Improve to just separate responses from ajax actions
            if request.method == "GET":
                return redirect("/login")
            else:
                abort(401)
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
