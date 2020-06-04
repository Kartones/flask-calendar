from flask_calendar import app as flask_app

app = flask_app.create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
