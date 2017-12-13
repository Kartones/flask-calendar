#!/usr/bin/python
# -!- coding: utf-8 -!-

from flask import Flask, render_template, request, jsonify, redirect, abort
import re

import config
from gregorian_calendar import GregorianCalendar
from calendar_data import CalendarData

app = Flask(__name__)


def _previous_month_link(year, month):
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


def _next_month_link(year, month):
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return "" if year < config.MIN_YEAR or year > config.MAX_YEAR else "?y={}&m={}".format(year, month)


@app.route("/<calendar_id>/", methods=["GET"])
def main_calendar(calendar_id):

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
    tasks = calendar_data.tasks_from_calendar(year=year, month=month, data=data)

    if not view_past_tasks:
        if year < current_year:
            tasks = {}
        elif year == current_year:
            if month < current_month:
                tasks = {}
            else:
                for day in tasks.keys():
                    if month == current_month and int(day) < current_day:
                        tasks[day] = []

    repetitive_tasks = calendar_data.repetitive_tasks_from_calendar(
        month_days=GregorianCalendar.month_days_with_weekday(year=year, month=month),
        data=data)
    for day, day_tasks in repetitive_tasks.items():
        if not view_past_tasks:
            if year < current_year:
                continue
            if year == current_year:
                if month < current_month or (month == current_month and int(day) < current_day):
                    continue
        if day not in tasks:
            tasks[day] = []
        for task in day_tasks:
            tasks[day].append(task)

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
def new_task(calendar_id, year, month):
    current_day, *_ = GregorianCalendar.current_date()
    year = max(min(int(year), config.MAX_YEAR), config.MIN_YEAR)
    month = max(min(int(month), 12), 1)
    month_names = GregorianCalendar.MONTH_NAMES

    return render_template("task.html",
                           calendar_id=calendar_id,
                           year=year,
                           month=month,
                           min_year=config.MIN_YEAR,
                           max_year=config.MAX_YEAR,
                           current_day=current_day,
                           month_names=month_names,
                           base_url=config.BASE_URL)


@app.route("/<calendar_id>/new_task", methods=["POST"])
def save_task(calendar_id):
    title = request.form["title"]
    date = request.form.get("date", "")
    if len(date) > 0:
        year, month, day = [int(fragment) for fragment in re.split('-', date)]
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
def delete_task(calendar_id, year, month, day, task_id):
    CalendarData(config.DATA_FOLTER).delete_task(calendar_id=calendar_id,
                                                 year_str=year,
                                                 month_str=month,
                                                 day_str=day,
                                                 task_id=int(task_id))
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=config.DEBUG)
