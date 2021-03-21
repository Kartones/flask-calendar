#!/usr/bin/python

import locale
import os
from typing import Dict




import config  # noqa: F401
from flask import Flask, Response, send_from_directory, flash, render_template, request, redirect, jsonify
from flask_calendar.db_setup import init_db, db_session
from flask_sqlalchemy import SQLAlchemy
from flask_calendar.actions import (
    delete_task_action,
    do_login_action,
    edit_task_action,
    hide_repetition_task_instance_action,
    index_action,
    login_action,
    main_calendar_action,
    new_task_action,
    save_task_action,
    update_task_action,
    update_task_day_action,
)
from flask_calendar.app_utils import task_details_for_markup

#dbapp = Flask(__name__)
#dbapp.config.from_object("config")
#dbapp = SQLAlchemy(dbapp)

def get_db(app):
    db = SQLAlchemy(app)
    return db


def create_app(config_overrides: Dict = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    #init_db()
    #db = SQLAlchemy(app)
    #db = get_db(app)

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon() -> Response:
        return send_from_directory(
            os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )

    app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/task/<task_id>",
        "update_task_action",
        update_task_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action, methods=["DELETE"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/",
        "update_task_day_action",
        update_task_day_action,
        methods=["PUT"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/",
        "hide_repetition_task_instance_action",
        hide_repetition_task_instance_action,
        methods=["POST"],
    )
    

        

    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup

    return app

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///duty.db'
app.secret_key = "justkey"
db = SQLAlchemy(app)

#if __name__ == "__main__":
#    app = create_app()

    #init_db()
    #get_db(app)
    #global db
    #db = SQLAlchemy(app)



#   app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
