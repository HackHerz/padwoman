import redis
from random import shuffle
from threading import Lock
import sys
from datetime import datetime
import functools
import operator

# own stuff
import settings
import etherpad_cached_api as eca


# We only need a cozy cache if someone is using the site
def touchClockwork(sched):
    r = redis.Redis(**settings.data['redis'])
    cw = r.get('clockwork')

    # trigger updateTimestamps immediately if flag did not exist
    if cw is None:
        sched.add_job(updateTimestamps)

    # Set Flag
    r.set('clockwork', 'ignore me', ex=300)  # TTL=5min


mutex = Lock()  # To prevent updateTimestamps from running multiple times


# Updates all the Timestamps for all Groups
def updateTimestamps():
    r = redis.Redis(**settings.data['redis'])

    if r.get('clockwork') is None:  # no need to do shit
        return

    # Acquire mutex if possible or exit immediately
    if not mutex.acquire(timeout=0):
        return

    # getting the list of groupIds
    groupIds = []
    for g in settings.groupDict:
        groupIds.append(eca.createGroupIfNotExistsFor(g))

    # getting the padlist
    padList = []
    for g in groupIds:
        padList += eca.getPadsFromCache(g)

    # getting pads which are in the cache
    cList = [x.decode('utf-8')[13:] for x in r.scan_iter('pad:lastEdit:*')]

    # guessing which pads are not in the cache
    notCache = [p for p in padList if p not in cList]

    # shuffle the list for a fair distribution
    shuffle(notCache)

    # getting the timestamps
    for pad in notCache:
        tStamp = eca.getLastEdited(pad)
        r.set('pad:lastEdit:%s' % pad, tStamp, eca.calcExpTime(tStamp))

    # Release mutex
    mutex.release()


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
