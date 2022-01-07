import sys
from datetime import datetime
import functools
import operator

# own stuff
import settings
import etherpad_cached_api as eca


# Delete expired etherpad sessions
def deleteExpiredSessions():
    # get the list of groupIds
    groupIds = map(eca.createGroupIfNotExistsFor, settings.groupDict)

    # get all sessions (of these groups)
    # pseudocode: fold(or, map(eca.listSessionsOfGroup, groupIds), {})
    if sys.version_info >= (3, 9):
        sessions = functools.reduce(operator.or_, map(eca.listSessionsOfGroup, groupIds), {})
    else:
        sessions = functools.reduce(lambda a, b: {**a, **b}, map(eca.listSessionsOfGroup, groupIds), {})
    # pythonic (but slower) way would be:
    #sessions = {k: v for sessionDict in [eca.listSessionsOfGroup(gId) for gId in groupIds] for k, v in sessionDict.items()}

    # filter out sessions that are not expired
    sessions = filter(lambda s: s[1]['validUntil'] < datetime.now().timestamp(), sessions.items())

    # delete sessions
    for k, v in sessions:
        eca.deleteSession(k)
