from app import app
from db_setup import init_db, db_session
from forms import SearchForm, Duty
from flask import flash, render_template, request, redirect, jsonify
from models import Project
from tables import Results


import sys
sys.path.append('../')

init_db()
#projects = db_session.query(Project).filter(Project.project).all()
id=1
projects = db_session.query(Project.project).all()
projects = [item[0] for item in projects]
print(projects)

#for project in projects:
    #print(project)

prj='DDPS'
dutys = db_session.query(Project.name).filter(Project.project==prj).all()
dutys = [item[0] for item in dutys]
#print(dutys)
jsonify({'DUTY': dutys})

#for duty in dutys:
#    print(duty)

#for project in projects:
#    print(project.__dict__)
