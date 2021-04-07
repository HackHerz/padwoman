import redis
from random import shuffle
from threading import Lock

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
    cList = [x.decode('utf-8')[13:] for x in r.keys('pad:lastEdit:*')]

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
