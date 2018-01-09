#!/usr/bin/python
# -!- coding: utf-8 -!-

from flask import Flask, render_template, request, jsonify, redirect, abort, Response
import re
from typing import Optional  # noqa: F401

import config
from gregorian_calendar import GregorianCalendar
from calendar_data import CalendarData

app = Flask(__name__)


def _previous_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


def _next_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


@app.route("/<calendar_id>/", methods=["GET"])
def main_calendar(calendar_id: str) -> Response:

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, config.MAX_YEAR), config.MIN_YEAR)
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]

    view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    calendar_data = CalendarData(config.DATA_FOLTER)
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        abort(404)

    tasks = calendar_data.tasks_from_calendar(year=year, month=month, view_past_tasks=view_past_tasks, data=data)

    tasks = calendar_data.add_repetitive_tasks_from_calendar(year=year, month=month, data=data, tasks=tasks,
                                                             view_past_tasks=view_past_tasks)

    return render_template("calendar.html",
                           calendar_id=calendar_id,
                           year=year,
                           month=month,
                           month_name=month_name,
                           current_year=current_year,
                           current_month=current_month,
                           current_day=current_day,
                           month_days=GregorianCalendar.month_days(year=year, month=month),
                           previous_month_link=_previous_month_link(year=year, month=month),
                           next_month_link=_next_month_link(year=year, month=month),
                           base_url=config.BASE_URL,
                           tasks=tasks)


@app.route("/<calendar_id>/<year>/<month>/new_task")
def new_task(calendar_id: str, year: int, month: int) -> Response:
    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = max(min(int(year), config.MAX_YEAR), config.MIN_YEAR)
    month = max(min(int(month), 12), 1)
    month_names = GregorianCalendar.MONTH_NAMES

    if current_month == month and current_year == year:
        day = current_day
    else:
        day = 1

    task = {
        "date": CalendarData.date_for_frontend(year=year, month=month, day=day),
        "is_all_day": True,
        "repeats": False,
    }

    return render_template("task.html",
                           calendar_id=calendar_id,
                           year=year,
                           month=month,
                           min_year=config.MIN_YEAR,
                           max_year=config.MAX_YEAR,
                           month_names=month_names,
                           task=task,
                           base_url=config.BASE_URL,
                           editing=False)


@app.route("/<calendar_id>/<year>/<month>/<day>/<task_id>/", methods=["GET"])
def edit_task(calendar_id: str, year: int, month: int, day: int, task_id: int) -> Response:
    month_names = GregorianCalendar.MONTH_NAMES
    calendar_data = CalendarData(config.DATA_FOLTER)

    repeats = request.args.get("repeats") == "1"

    try:
        if repeats:
            task = calendar_data.repetitive_task_from_calendar(calendar_id=calendar_id, year=year, month=month,
                                                               task_id=int(task_id))
        else:
            task = calendar_data.task_from_calendar(calendar_id=calendar_id, year=year, month=month, day=day,
                                                    task_id=int(task_id))
    except (FileNotFoundError, IndexError):
        abort(404)

    return render_template("task.html",
                           calendar_id=calendar_id,
                           year=year,
                           month=month,
                           day=day,
                           min_year=config.MIN_YEAR,
                           max_year=config.MAX_YEAR,
                           month_names=month_names,
                           task=task,
                           base_url=config.BASE_URL,
                           editing=True)


@app.route("/<calendar_id>/<year>/<month>/<day>/task/<task_id>", methods=["POST"])
def update_task(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    # Logic is same as save + delete, could refactor but can wait until need to change any save/delete logic

    calendar_data = CalendarData(config.DATA_FOLTER)

    # For creation of "updated" task use only form data
    title = request.form["title"]
    date = request.form.get("date", "")
    if len(date) > 0:
        fragments = re.split('-', date)
        updated_year = fragments[0]  # Optional[int]
        updated_month = fragments[1]  # Optional[int]
        updated_day = fragments[2]  # Optional[int]
    else:
        updated_year = updated_month = updated_day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    due_time = request.form["due_time"]
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type", "")
    repetition_subtype = request.form.get("repetition_subtype", "")
    repetition_value = int(request.form["repetition_value"])  # type: int
    calendar_data.create_task(calendar_id=calendar_id,
                              year=updated_year,
                              month=updated_month,
                              day=updated_day,
                              title=title,
                              is_all_day=is_all_day,
                              due_time=due_time,
                              details=details,
                              color=color,
                              has_repetition=has_repetition,
                              repetition_type=repetition_type,
                              repetition_subtype=repetition_subtype,
                              repetition_value=repetition_value)

    # For deletion of old task data use only url data
    calendar_data.delete_task(calendar_id=calendar_id,
                              year_str=year,
                              month_str=month,
                              day_str=day,
                              task_id=int(task_id))

    if updated_year is None:
        return redirect("{}/{}/".format(config.BASE_URL, calendar_id), code=302)
    else:
        return redirect("{}/{}/?y={}&m={}".format(config.BASE_URL, calendar_id, updated_year, updated_month), code=302)


@app.route("/<calendar_id>/new_task", methods=["POST"])
def save_task(calendar_id: str) -> Response:
    title = request.form["title"]
    date = request.form.get("date", "")
    if len(date) > 0:
        date_fragments = re.split('-', date)
        year = int(date_fragments[0])  # type: Optional[int]
        month = int(date_fragments[1])  # type: Optional[int]
        day = int(date_fragments[2])  # type: Optional[int]
    else:
        year = month = day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    due_time = request.form["due_time"]
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type")
    repetition_subtype = request.form.get("repetition_subtype")
    repetition_value = int(request.form["repetition_value"])

    CalendarData(config.DATA_FOLTER).create_task(calendar_id=calendar_id,
                                                 year=year,
                                                 month=month,
                                                 day=day,
                                                 title=title,
                                                 is_all_day=is_all_day,
                                                 due_time=due_time,
                                                 details=details,
                                                 color=color,
                                                 has_repetition=has_repetition,
                                                 repetition_type=repetition_type,
                                                 repetition_subtype=repetition_subtype,
                                                 repetition_value=repetition_value)

    if year is None:
        return redirect("{}/{}/".format(config.BASE_URL, calendar_id), code=302)
    else:
        return redirect("{}/{}/?y={}&m={}".format(config.BASE_URL, calendar_id, year, month), code=302)


@app.route("/<calendar_id>/<year>/<month>/<day>/<task_id>/", methods=["DELETE"])
def delete_task(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    CalendarData(config.DATA_FOLTER).delete_task(calendar_id=calendar_id,
                                                 year_str=year,
                                                 month_str=month,
                                                 day_str=day,
                                                 task_id=int(task_id))
    return jsonify({})


@app.route("/<calendar_id>/<year>/<month>/<day>/<task_id>/", methods=["PUT"])
def update_task_day(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    new_day = request.data.decode("utf-8")
    CalendarData(config.DATA_FOLTER).update_task_day(calendar_id=calendar_id,
                                                     year_str=year,
                                                     month_str=month,
                                                     day_str=day,
                                                     task_id=int(task_id),
                                                     new_day_str=new_day)
    return jsonify({})


@app.route("/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/", methods=["POST"])
def hide_repetition_task_instance(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    CalendarData(config.DATA_FOLTER).hide_repetition_task_instance(calendar_id=calendar_id,
                                                                   year_str=year,
                                                                   month_str=month,
                                                                   day_str=day,
                                                                   task_id_str=task_id)
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=config.DEBUG)
