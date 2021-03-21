from flask_calendar.app import db



class Project(db.Model):
    """"""
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    project = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)