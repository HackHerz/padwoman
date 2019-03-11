from flask_restful import Resource

# own stuff
from etherpad_cached_api import *



# Creating a new Pad in the corresponding group
class CreatePad(Resource):
    def get(self, padName, group):
        ethGid = createGroupIfNotExistsFor(group)

        return createGroupPad(ethGid, padName)


# Set visibility of pad
class PadVisibility(Resource):
    def get(self, padName, visibility):
        v = None

        if visibility == "public":
            v = True

        if visibility == "private":
            v = False

        if v == None:
            return { 'code' : 3, 'message' : 'not ok' }

        return setPublicStatus(padName, v)
