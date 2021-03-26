from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config  # noqa: F401
from flask import Flask
db = Flask(__name__)
db.config.from_object("config")
database=db.config["SQLALCHEMY_DATABASE_URI"]
engine = create_engine(database, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
def init_db():
    import flask_calendar.models
    Base.metadata.create_all(bind=engine)