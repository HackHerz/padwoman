from pytz import utc
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask import Flask
import flask_login
from flask_restful import Api
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from importlib import import_module

# Own stuff
import microapi
from etherpad_cached_api import *
from _version import __version__
from clockwork import updateTimestamps, touchClockwork


# Flask
app = Flask(__name__, static_folder='assets')
app.secret_key = settings.getSecretKey()
api = Api(app) # API wuhuuu


# Flask login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load Authentication
User = getattr(import_module('auth.' + settings.data['auth']['method']), 'User')
AuthMechanism = getattr(import_module('auth.' + settings.data['auth']['method']), 'AuthMechanism')

# Job to renew lastEdit timestamps in the cache
sched = BackgroundScheduler(timezone=utc)
sched.start()
sched.add_job(updateTimestamps, 'interval', seconds=59)


@login_manager.user_loader
def user_loader(uid):
    user = User(uid)

    if not user.exists():
        return None

    user.populate()

    return user


# Jinja template variables which are always the same
@app.context_processor
def templateDefaultValues():
    return dict(padwoman_version=__version__,
            title=settings.data['default']['title'])



@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if user is already logged in
    if flask_login.current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('index'))

    return AuthMechanism.login(User)


# Logout
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return AuthMechanism.logout()


# Serving the actual site
@app.route('/')
@flask_login.login_required
def index():
    # get selected tab
    active_group = request.args.get('group')

    # default group
    if active_group == None:
        active_group = settings.getDefaultGroup(flask_login.current_user.id,
                flask_login.current_user.groups)

    # Check if user is allowed to view this group
    viewableGroups = settings.getPadGroups(flask_login.current_user.id,
            flask_login.current_user.groups)

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
        group_has_date=settings.groupHasDate(active_group),
        group_has_time=settings.groupHasTime(active_group),
        datetimeAdjustable=settings.datetimeAdjustable(active_group),
        dateDefault=settings.getDateDefault(active_group),
        timeDefault=settings.groupDict[active_group].get('timedefault', ""),
        groupExistsAndAllowed=groupExistsAndAllowed))

    # Building the user cookie
    sessionstring = '%'.join(etherPadSessions)
    response.set_cookie('sessionID', sessionstring, expires=validUntil,
                        samesite="Strict")

    # Flask would escape the ',', but etherpad has become very picky recently
    response.headers['Set-Cookie'] = response.headers['Set-Cookie'].replace('%', ',')
    return response


# Execute on every request
@app.before_request
def do_something_whenever_a_request_comes_in():
    touchClockwork(sched)


# Api for the javascript ui
api.add_resource(microapi.CreatePad,
        '/uapi/CreatePad/<string:group>/<string:padName>')

api.add_resource(microapi.CreateContentPad,
        '/uapi/CreateContentPad/<string:group>/<string:padName>')

api.add_resource(microapi.CreatePadDatetime,
        '/uapi/CreatePad/<string:group>/<string:padName>/<string:timestamp>')

api.add_resource(microapi.CreateContentPadDatetime,
        '/uapi/CreateContentPad/<string:group>/<string:padName>/<string:timestamp>')

api.add_resource(microapi.PadVisibility,
        '/uapi/PadVisibility/<string:padName>/<string:visibility>')

api.add_resource(microapi.ExportLatex, '/uapi/ExportLatex/<string:padName>')

# Run
if __name__ == '__main__':
     app.run(host=settings.data['default'].get('host', '0.0.0.0'), port=settings.data['default'].get('port', '5000'))
