from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
engine = create_engine('sqlite:///duty.db', echo=True)
Base = declarative_base()

class Project(Base):
    """"""
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    project = Column(String)
    phone = Column(String)
    email = Column(String)
# create tables
Base.metadata.create_all(engine)