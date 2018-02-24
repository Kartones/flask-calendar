#!/usr/bin/python

import locale

from flask import Flask

import config
from authentication import Authentication


from actions import (index_action, login_action, do_login_action, main_calendar_action, new_task_action,
                     edit_task_action, update_task_action, save_task_action, delete_task_action, update_task_day_action,
                     hide_repetition_task_instance_action)


app = Flask(__name__)

authentication = Authentication(data_folder=config.USERS_DATA_FOLDER, password_salt=config.PASSWORD_SALT)
if config.LOCALE is not None:
    locale.setlocale(locale.LC_ALL, config.LOCALE)

app.add_url_rule("/", "index_action", index_action, methods=["GET"])
app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
app.add_url_rule("/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"])
app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action,
                 methods=["GET"])
app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/task/<task_id>", "update_task_action", update_task_action,
                 methods=["POST"])
app.add_url_rule("/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"])
app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action,
                 methods=["DELETE"])
app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "update_task_day_action", update_task_day_action,
                 methods=["PUT"])
app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/", "hide_repetition_task_instance_action",
                 hide_repetition_task_instance_action, methods=["POST"])


if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.HOST_IP)
