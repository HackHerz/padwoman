from flask_restful import Resource
from flask import Response
import flask_login
import re
from latex import latex

# own stuff
from etherpad_cached_api import *
import settings


def parseTimestamp(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    else:
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', timestamp):
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
        elif re.match(r'\d{4}-\d{2}-\d{2}', timestamp):
            return datetime.strptime(timestamp, '%Y-%m-%d')
        elif re.match(r'\d{2}:\d{2}', timestamp):
            return datetime.strptime(timestamp, '%H:%M')
        else:
            return datetime.now()



# Creating a new Pad in the corresponding group
class CreatePadDatetime(Resource):
    @flask_login.login_required
    def get(self, padName, group, timestamp):
        ethGid = createGroupIfNotExistsFor(group)

        time = parseTimestamp(timestamp)

        # Remove whitespaces on beginning and end
        padName = settings.render(padName.strip(), time).replace(' ', '_')

        # Padname has at least 3 characters
        if len(padName) < 3:
            return { 'code' : 7, 'message' : 'Mach den Namen mal laenger' }

        if not bool(re.match(r'.*[a-zA-z]{1,}', padName)):
            return { 'code' : 6, 'message' : 'Probiere es mal mit Buchstaben' }

        return createGroupPad(ethGid, padName)


# Creating a pad with content
class CreateContentPadDatetime(CreatePadDatetime):
    @flask_login.login_required
    def get(self, padName, group, timestamp):
        time = parseTimestamp(timestamp)

        response = CreatePadDatetime.get(self, padName, group, timestamp)

        # Pad Creation was a success, now content
        if response['code'] == 0:
            return setHtml(response['data']['padID'],
                    settings.getGroupTemplate(group, time))

        return response


# Creating a pad without user timestamp
class CreatePad(CreatePadDatetime):
    @flask_login.login_required
    def get(self, padName, group):
        return CreatePadDatetime.get(self, padName, group, datetime.now())


# Creating a pad with content and without user timestamp
class CreateContentPad(CreateContentPadDatetime):
    @flask_login.login_required
    def get(self, padName, group):
        return CreateContentPadDatetime.get(self, padName, group, datetime.now())


# Set visibility of pad
class PadVisibility(Resource):
    @flask_login.login_required
    def get(self, padName, visibility):
        v = None

        if visibility == "public":
            v = True

        if visibility == "private":
            v = False

        if v == None:
            return { 'code' : 3, 'message' : 'not ok' }

        return setPublicStatus(padName, v)


# Export LaTeX of Pad
class ExportLatex(Resource):
    @flask_login.login_required
    def get(self, padName):
        j = getHtml(padName)
        r = Response(latex(j['data']['html']), mimetype='application/x-latex')
        r.headers['Content-Disposition'] = 'attachment; filename=%s.tex' % padName.split('$')[1]
        return r
