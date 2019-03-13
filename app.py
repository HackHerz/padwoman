from flask import render_template
from flask import request, redirect, url_for, make_response
from flask import Flask
import flask_login
from flask_restful import Resource, Api, reqparse
from datetime import timedelta

# Own stuff
import userclass
import settings
from ldaphandler import LdapHandler
import microapi
from etherpad_cached_api import *
from _version import __version__


# Flask
app = Flask(__name__, static_folder='assets')
app.secret_key = settings.getSecretKey()
api = Api(app) # API wuhuuu


# Flask login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def user_loader(uid):
    ldapObject = LdapHandler(uid)

    # User does not exist
    if ldapObject.getDn() == False:
        return

    user = userclass.User()
    user.id = uid
    user.groups = ldapObject.getGroups()
    user.cn = ldapObject.getCn()

    return user


# Jinja template variables which are always the same
@app.context_processor
def templateDefaultValues():
    return dict(padwoman_version=__version__,
            title=settings.data['default']['title'])



@app.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')

    # check if user is already logged in
    if flask_login.current_user.is_authenticated:
        return redirect(next or url_for('index'))

    # Render the view
    if request.method == 'GET':
        return render_template('login.html')

    # Check if there is data to login the user
    if 'username' in request.form.keys() and 'password' in request.form.keys():
        username = request.form['username']

        ldapObject = LdapHandler(username)

        # redirect to index if credentials are correct
        if ldapObject.verifyPw(request.form['password']):

            user = userclass.User()
            user.id = username
            flask_login.login_user(user)

            return redirect(next or url_for('index'))

    return render_template('login.html', loginFailed=True)


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
        active_group = settings.getDefaultGroup(flask_login.current_user.id,
                flask_login.current_user.getGroups())

    # Check if user is allowed to view this group
    viewableGroups = settings.getPadGroups(flask_login.current_user.id,
            flask_login.current_user.getGroups())

    groupExistsAndAllowed = active_group in viewableGroups


    # Doing all the etherpadMagic
    etherPadAuthor = createAuthorIfNotExistsFor(flask_login.current_user.id,
            flask_login.current_user.cn)

    validUntil = int((datetime.now() + timedelta(days=1)).timestamp())

    etherPadGroupIds = {}
    etherPadSessions = []

    for g in viewableGroups:
        etherPadGroupIds[g] = createGroupIfNotExistsFor(g)
        
        # sessions for the user
        etherPadSessions.append(createSession(etherPadGroupIds[g],
            etherPadAuthor, validUntil))


    # Gathering information on the relevant pads for this group
    padlist = [] if not groupExistsAndAllowed else getPadlist(
            etherPadGroupIds[active_group])

    # Sorting the pads descending by last edited
    sortedList = sorted(padlist, key=lambda x : x['date'], reverse=True)

    # Rendering the View
    response = make_response(render_template('main.html',
        pads=sortedList, groups=viewableGroups, active_group=active_group, 
        group_has_template=settings.groupHasTemplate(active_group),
        nameSuggestionMandatory=settings.groupPadnameSuggestionMandatory(active_group),
        new_pad_name=settings.getGroupPadname(active_group),
        template_mandatory=settings.groupTemplateMandatory(active_group),
        groupExistsAndAllowed=groupExistsAndAllowed))

    # Building the user cookie
    sessionstring = '%2c'.join(etherPadSessions)
    response.set_cookie('sessionID', sessionstring, expires=validUntil) 

    return response




# Api for the javascript ui
api.add_resource(microapi.CreatePad,
        '/uapi/CreatePad/<string:group>/<string:padName>')

api.add_resource(microapi.CreateContentPad,
        '/uapi/CreateContentPad/<string:group>/<string:padName>')

api.add_resource(microapi.PadVisibility,
        '/uapi/PadVisibility/<string:padName>/<string:visibility>')


# Run
if __name__ == '__main__':
     app.run(host='0.0.0.0', port='5000')
