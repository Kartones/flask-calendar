from flask_calendar.app import app
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.forms import SearchForm, Duty
from flask import flash, render_template, request, redirect, jsonify
from flask_calendar.models import Project
from flask_calendar.tables import Results
from flask_calendar.authentication import Authentication
from flask_calendar.app_utils import (
    add_session,
    authenticated,
    authorized,
    get_session_username,
    new_session_id,
    next_month_link,
    previous_month_link,
)
init_db()
app=app

def getphone(duty):
    phones = db_session.query(Project.phone).filter(Project.name==duty).all()
    phones = [item[0] for item in phones]
    phone=phones[0]
    return phone


@app.route('/allduty')
@authenticated
def show_dutys():
    results = []
    qry = db_session.query(Project)
    results = qry.all()
    # display results
    tableres = Results(results)
    tableres.border = True
    return render_template('duty.html', table=tableres)

@app.route('/new_duty', methods=['GET', 'POST'])
@authenticated
def new_duty():
    """
    Add a new duty
    """
    form = Duty(request.form)
    if request.method == 'POST' and form.validate():
        # save the duty
        duty = Duty()
        save_changes(duty, form, new=True)
        flash('Duty created successfully!')
        return redirect('/')
    return render_template('new_duty.html', form=form)

@authenticated
def save_changes(duty, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    if new:
        duty = Project()
        duty.name = form.name.data
        #duty.name = "HELLO"
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
        # Add the new album to the database
        db_session.add(duty)
    else:
        #duty = Project()
        duty.name = form.name.data
        #duty.name = "HELLO"
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
    # commit the data to the database
    db_session.commit()

@app.route('/item/<int:id>', methods=['GET', 'POST'])
@authenticated
def edit(id):
    qry = db_session.query(Project).filter(
                Project.id==id)
    duty = qry.first()
    if duty:
        form = Duty(formdata=request.form, obj=duty)
        if request.method == 'POST' and form.validate():
            # save edits
            save_changes(duty, form)
            flash('Duty updated successfully!')
            return redirect('/')
        return render_template('edit_duty.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@authenticated
def delete(id):
    """
    Delete the item in the database that matches the specified
    id in the URL
    """
    qry = db_session.query(Project).filter(
        Project.id==id)
    duty = qry.first()
    if duty:
        form = Duty(formdata=request.form, obj=duty)
        if request.method == 'POST' and form.validate():
            # delete the item from the database
            db_session.delete(duty)
            db_session.commit()
            flash('Duty deleted successfully!')
            return redirect('/')
        return render_template('delete_duty.html', form=form)
    else:
        return 'Error deleting #{id}'.format(id=id)

@app.route('/duty_choice/<value>')
@authenticated
def duty_choice(value):
    prj=value
    dutys = db_session.query(Project.name).filter(Project.project==prj).all()
    dutys = [item[0] for item in dutys]
    return jsonify({'DUTY': dutys})

@app.route('/duty_choice2/<value1>&<value2>')
def duty_choice2(value1,value2):
    prj=value1
    duty=value2
    dutys = db_session.query(Project.name).filter(Project.project==prj).all()
    dutys = [item[0] for item in dutys]
    dutys.append(dutys.pop(dutys.index(duty)))
    return jsonify({'DUTY': dutys})

@app.route('/duty_projects/')
def duty_projects():
    projects = db_session.query(Project.project).all()
    projects = [item[0] for item in projects]
    projects =list(set(projects))
    return jsonify({'PROJECTS': projects})







if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])