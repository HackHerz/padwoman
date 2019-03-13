from flask_restful import Resource
import flask_login
import re

# own stuff
from etherpad_cached_api import *
import settings



# Creating a new Pad in the corresponding group
class CreatePad(Resource):
    @flask_login.login_required
    def get(self, padName, group):
        ethGid = createGroupIfNotExistsFor(group)

        # Remove whitespaces on beginning and end
        padName = padName.strip()

        # Padname has at least 3 characters
        if len(padName) < 3:
            return { 'code' : 7, 'message' : 'Mach den Namen mal laenger' }

        if not bool(re.match('.*[a-zA-z]{1,}', padName)):
            return { 'code' : 6, 'message' : 'Fick dich' }

        return createGroupPad(ethGid, padName)


# Creating a pad with content
class CreateContentPad(CreatePad):
    @flask_login.login_required
    def get(self, padName, group):
        response = CreatePad.get(self, padName, group)

        # Pad Creation was a success, now content
        if response['code'] == 0:
            return setHtml(response['data']['padID'],
                    settings.getGroupTemplate(group))

        return response


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
