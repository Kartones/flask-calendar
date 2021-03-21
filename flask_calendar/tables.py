from flask_table import Table, Col, LinkCol
class Results(Table):
    id = Col('Id', show=False)
    name = Col('name')
    project = Col('project')
    phone = Col('phone')
    email = Col('email')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete', url_kwargs=dict(id='id'))