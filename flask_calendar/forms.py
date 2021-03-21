from wtforms import Form, StringField, SelectField
class SearchForm(Form):
    choices = [('Duty', 'Duty'),
               ('Project', 'Project'),
               ('Phone', 'Phone')]
    select = SelectField('Search for project:', choices=choices)
    search = StringField('')

class Duty(Form):
    name = StringField('Name')
    project = StringField('Project')
    phone = StringField('Phone')
    email = StringField('Email')
