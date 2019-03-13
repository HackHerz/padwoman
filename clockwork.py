import redis
from random import shuffle

# own stuff
import settings
from etherpad_cached_api import *


def updateTimestamps():
    # getting the list of groupIds
    groupIds = []
    for g in settings.groupDict:
        groupIds.append(createGroupIfNotExistsFor(g))

    # getting the padlist
    padList = []
    for g in groupIds:
        padList += getPadsFromCache(g)

    # getting pads which are in the cache
    r = redis.Redis(**settings.data['redis'])
    cList = [ x.decode('utf-8')[13:] for x in r.keys('pad:lastEdit:*') ]
    
    # guessing which pads are not in the cache
    notCache = [ p for p in padList if p not in cList ]

    # shuffle the list for a fair distribution
    shuffle(notCache)
    
    # getting the timestamps
    for pad in notCache:
        tStamp = getLastEdited(pad)
        r.set('pad:lastEdit:%s' % pad, tStamp, calcExpTime(tStamp))
