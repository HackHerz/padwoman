from flask import render_template
from flask import Flask

app = Flask(__name__)


fake_data = [
        { 'title': 'sitzung_01', 'date': '2018-18-18 18:18', 'public': False },
        { 'title': 'sitzung_02', 'date': '2018-18-18 18:18', 'public': True },
        { 'title': 'sitzung_03', 'date': '2018-18-18 18:18' },
        { 'title': 'sitzung_04', 'date': '2018-18-18 18:18' },
        { 'title': 'sitzung_05', 'date': '2018-18-18 18:18' },
        { 'title': 'sitzung_06', 'date': '2018-18-18 18:18' },
        { 'title': 'sitzung_07', 'date': '2018-18-18 18:18' },
        { 'title': 'sitzung_08', 'date': '2018-18-18 18:18' },
        ]

fake_groups = [
        { 'name' : 'Allgemein', 'id' : 'allgemein' },
        { 'name' : 'Sitzung', 'id' : 'sitzung', 'active': True },
        { 'name' : 'Redaktion', 'id' : 'redaktion' },
        { 'name' : 'Admins', 'id' : 'admins' },
        ]


@app.route('/')
@app.route('/index')
def index():
    return render_template('main.html', title='Fachschafts Pads', pads=fake_data, groups=fake_groups, active_group="Sitzung")


# Run
if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5000')
