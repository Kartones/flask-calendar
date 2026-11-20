import re
import uuid
from functools import wraps
from typing import Any, Callable

from cachelib.simple import SimpleCache
from flask import abort, current_app, redirect, request
from flask_calendar.authorization import Authorization
from flask_calendar.calendar_data import CalendarData
from flask_calendar.constants import SESSION_ID
from flask_calendar.gregorian_calendar import GregorianCalendar
from markupsafe import Markup, escape

cache = SimpleCache()

# see `app_utils` tests for details, but TL;DR is that urls must start with `http://` or `https://` to match
URLS_REGEX_PATTERN = r"(https?\:\/\/[\w/\-?=%.]+\.[\w/\+\-?=%.~&\[\]\#]+)"
DECORATED_URL_FORMAT = '<a href="{}" target="_blank">{}</a>'
LINE_BREAK_MARKER = "<br>"
EMPTY_DETAILS_PLACEHOLDER = "&nbsp;"


def authenticated(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_id = request.cookies.get(SESSION_ID)
        if session_id is None or not is_session_valid(str(session_id)):
            if request.headers.get("Content-Type", "") == "application/json":
                abort(401)
            return redirect("/login")
        return decorated_function(*args, **kwargs)

    return wrapper


def authorized(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        username = get_session_username(str(request.cookies.get(SESSION_ID)))
        authorization = Authorization(calendar_data=CalendarData(data_folder=current_app.config["DATA_FOLDER"]))
        if "calendar_id" not in kwargs:
            raise ValueError("calendar_id")
        calendar_id = str(kwargs["calendar_id"])
        if not authorization.can_access(username=username, calendar_id=calendar_id):
            abort(403)
        return decorated_function(*args, **kwargs)

    return wrapper


def previous_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return (
        ""
        if year < current_app.config["MIN_YEAR"] or year > current_app.config["MAX_YEAR"]
        else "?y={}&m={}".format(year, month)
    )


def next_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return (
        ""
        if year < current_app.config["MIN_YEAR"] or year > current_app.config["MAX_YEAR"]
        else "?y={}&m={}".format(year, month)
    )


def new_session_id() -> str:
    return str(uuid.uuid4())


def is_session_valid(session_id: str) -> bool:
    return cache.get(session_id) is not None


def add_session(session_id: str, username: str) -> None:
    cache.set(session_id, username, timeout=2678400)  # 1 month


def get_session_username(session_id: str) -> str:
    return str(cache.get(session_id))


def task_details_for_markup(details: str) -> Markup:
    if details == EMPTY_DETAILS_PLACEHOLDER:
        return Markup(details)

    lines = details.split(LINE_BREAK_MARKER)
    return Markup(LINE_BREAK_MARKER).join(_markup_line(line) for line in lines)


def _markup_line(line: str) -> Markup:
    if not current_app.config["AUTO_DECORATE_TASK_DETAILS_HYPERLINK"]:
        return escape(line)

    fragments = re.split(URLS_REGEX_PATTERN, line)
    return Markup("").join(_markup_fragment(index, fragment) for index, fragment in enumerate(fragments))


def _markup_fragment(index: int, fragment: str) -> Markup:
    is_url = index % 2 == 1
    if is_url:
        return Markup(DECORATED_URL_FORMAT).format(fragment, fragment)

    return escape(fragment)
