from flask import render_template
from flask import request, redirect, url_for
from flask import Flask
import flask_login
import ldap

# Own stuff
import userclass
import settings


# LDAP
connect = ldap.initialize(settings.data['ldap']['server'])

connect.set_option(ldap.OPT_REFERRALS, 0)

connect.simple_bind_s(settings.data['ldap']['binddn'],
        settings.data['ldap']['bindpw'])

# Flask
app = Flask(__name__)
app.secret_key = settings.getSecretKey()


# Flask login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def user_loader(uid):
    query = settings.data['ldap']['userfilter'] % uid
    ldap_user = connect.search_s(settings.data['ldap']['usertree'], ldap.SCOPE_SUBTREE,
            query, ['cn'])

    # User does not exist
    if len(ldap_user) == 0:
        return

    user = userclass.User()
    user.id = uid
    return user


# Data
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

# Verifying login
def verify_pw(username, password):
    print("pw is being checked...")

    # Check if username is empty
    if username == "":
        return False

    # Verify user against ldap
    # first get the cn
    query = settings.data['ldap']['userfilter'] % username
    ldap_user = connect.search_s(settings.data['ldap']['usertree'], ldap.SCOPE_SUBTREE,
            query, ['cn'])

    # User does not exist
    if len(ldap_user) == 0:
        return False

    dn_user = ldap_user[0][0]

    # Check PW
    try:
        pw_test = ldap.initialize(settings.data['ldap']['server'])
        pw_test.bind_s(dn_user, password)
        pw_test.unbind_s()

    except ldap.LDAPError:
        return False

    return True



@app.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')

    # check if user is already logged in
    if flask_login.current_user.is_authenticated:
        return redirect(next or url_for('index'))

    # Render the view
    if request.method == 'GET':
        return render_template('login.html', title=settings.data['default']['title'])

    # Check if there is data to login the user
    username = request.form['username']

    if verify_pw(username, request.form['password']):
        user = userclass.User()
        user.id = username
        flask_login.login_user(user)

        return redirect(next or url_for('index'))

    return render_template('login.html', title=settings.data['default']['title'],
            loginFailed=True)



# Logout
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for("login"))



# Serving the actual site
@app.route('/')
@flask_login.login_required
def index():
    # get selected tab
    active_group = request.args.get('group')

    # default group
    if active_group == None:
        active_group = settings.getDefaultGroup("", "") # FIXME

    # Check if user is allowed to view this group
    groupExistsAndAllowed = active_group in settings.getPadGroups("", "")
 
    return render_template('main.html', title=settings.data['default']['title'],
            pads=fake_data, groups=settings.getPadGroups("", ""), active_group=active_group,
            group_has_template=True, groupExistsAndAllowed=groupExistsAndAllowed)



# Run
if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5000')
