import requests
import redis
import json
from datetime import datetime, timedelta
from threading import Thread, Lock

# own stuff
import settings


# setup redis
red = redis.Redis(**settings.data['redis'])

# setup mutex for each padGroup to use in getPadlist
mutex = {g: Lock() for g in settings.groupDict.keys()}


def requestHandler(endpoint, data):
    data['apikey'] = settings.data['pad']['apikey']
    r = requests.get(settings.data['pad']['apiurl'] + '1.2/' + endpoint,
            params=data)

    return r.json()


# creates a new pad in this group
def createGroupPad(groupId, padName):
    # invalidate cache
    red.delete("padlist:%s" % groupId)

    data = { 'groupID' : groupId,
            'padName' : padName }

    r = requestHandler('createGroupPad', data)

    return r


# this functions helps you to map your application author ids to etherpad lite author ids
def createAuthorIfNotExistsFor(uid, name):
    redisKey = 'author:' + uid
    rVal = red.get(redisKey)

    # trying the cache
    if rVal is not None:
        return rVal.decode('utf-8')

    data = { 'authorMapper' : uid, 'name' : name }
    r = requestHandler('createAuthorIfNotExistsFor', data)

    # everything was ok
    if r['code'] == 0:
        rVal = r['data']['authorID']
        red.set(redisKey, rVal)
        return rVal

    # Otherwise
    return None


# this functions helps you to map your application group ids to etherpad lite group ids
def createGroupIfNotExistsFor(groupMapper):
    redisKey = 'group:' + groupMapper
    rVal = red.get(redisKey)

    # trying the cache
    if rVal is not None:
        return rVal.decode('utf-8')

    data = { 'groupMapper' : groupMapper }
    r = requestHandler('createGroupIfNotExistsFor', data)

    # everything was ok
    if r['code'] == 0:
        rVal = r['data']['groupID']
        red.set(redisKey, rVal)
        return rVal

    # Otherwise
    return None


# returns all pads of this group
def listPads(groupId, forceFresh=False):
    redisKey = f"padlist:{groupId}"

    cacheVal = None
    if not forceFresh:
        cacheVal = red.get(redisKey)

    if cacheVal is None:
        data = {'groupID': groupId}
        r = requestHandler('listPads', data)

        # everything was ok
        if r['code'] == 0:
            pads = r['data']['padIDs']
            red.set(redisKey, json.dumps(pads), ex=timedelta(days=1))
            return pads

        return []

    else:
        return json.loads(cacheVal.decode('utf-8'))


# returns the timestamp of the last revision of the pad
def getLastEdited(padId, forceFresh=False):
    redisKey = f"pad:lastEdit:{padId}"

    rVal = None
    if not forceFresh:
        rVal = red.get(redisKey)

    # trying the cache
    if rVal is not None:
        return rVal.decode('utf-8')

    data = {'padID': padId}
    r = requestHandler('getLastEdited', data)

    # everything was ok
    if r['code'] == 0:
        editTime = datetime.fromtimestamp(int(r['data']['lastEdited']) / 1000)
        rVal = editTime.strftime('%Y-%m-%d %H:%M')

        # 20s per day
        expire = ((datetime.now() - editTime) * 20).days
        # between 1min and 1hour
        expire = max(60, min(3600, expire))

        red.set(redisKey, rVal, ex=expire)
        return rVal

    # Otherwise
    return "1970-01-01 00:00"


# returns if the pad is public
def getPublicStatus(padId, forceFresh=False):
    redisKey = f"pad:public:{padId}"

    rVal = None
    if not forceFresh:
        rVal = red.get(redisKey)

    # trying the cache
    if rVal is not None:
        return rVal.decode('utf-8')

    data = {'padID': padId}
    r = requestHandler('getPublicStatus', data)

    # everything was ok
    if r['code'] == 0:
        rVal = "True" if r['data']['publicStatus'] else "False"
        red.set(redisKey, rVal)
        return rVal

    # Otherwise
    return ""

# set the public status of a pad
def setPublicStatus(padId, publicStatus):
    redisKey = f"pad:public:{padId}"

    data = { 'padID' : padId,
            'publicStatus' : "true" if publicStatus else "false" }

    r = requestHandler('setPublicStatus', data)
    if r['code'] == 0:
        red.set(redisKey, "True" if publicStatus else "False")
    else:
        red.delete(redisKey)

    return r

# creates a new session. validUntil is an unix timestamp in seconds
def createSession(groupId, authorId, padwomanSession, datetimeNow = datetime.now(), validFor = timedelta(days=1), atLeastValidFor = timedelta(hours=6)):
    redisKey = f"session:{authorId}:{padwomanSession}:{groupId}"
    rVal = red.ttl(redisKey)

    # trying the cache
    if rVal > atLeastValidFor.total_seconds():
        return red.get(redisKey).decode('utf-8')

    validUntil = round((datetimeNow + validFor).timestamp())
    data = { 'groupID' : groupId, 'authorID' : authorId,
            'validUntil' : validUntil }
    r = requestHandler('createSession', data)

    # everything was ok
    if r['code'] == 0:
        rVal = r['data']['sessionID']
        red.set(redisKey, rVal, ex=(datetimeNow + validFor - datetime.now()))
        return rVal

    # Otherwise
    return ""


def listSessionsOfGroup(groupId):
    data = {'groupID': groupId}
    r = requestHandler('listSessionsOfGroup', data)

    # everything was ok
    if r['code'] == 0:
        return r['data']

    return []


def deleteSession(sessionId, authorId = None, groupId = None, padwomanSession = None):
    if None not in (authorId, groupId, padwomanSession):
        red.delete(f"session:{authorId}:{padwomanSession}:{groupId}")

    data = {'sessionID': sessionId}
    r = requestHandler('deleteSession', data)

    return r


def deleteSessionsOfAuthorAndPadwomanSession(authorId, padwomanSession):
    keys = red.scan_iter(f"session:{authorId}:{padwomanSession}:*")
    for key in keys:
        sessionId = red.get(key)

        data = {'sessionID': sessionId}
        r = requestHandler('deleteSession', data)

        red.delete(key)


def setHtml(padId, html):
    data = { 'padID' : padId, 'html' : html }
    r = requestHandler('setHTML', data)

    return r


# returns the human friendly name of a pad
def humanPadName(padId):
    splat = padId.split('$', 1)

    if len(splat) > 1:
        return splat[1]

    return padId


# returns a list of all pads and their necessary values
def getPadlist(group, groupId=None, synchronous=False):
    if groupId is None:
        groupId = createGroupIfNotExistsFor(group)

    padIds = listPads(groupId)

    # gather information of these pads
    lastEditPipe = red.pipeline()
    publicPipe = red.pipeline()

    # Load Values from Cache
    for p in padIds:
        lastEditPipe.get(f"pad:lastEdit:{p}")
        publicPipe.get(f"pad:public:{p}")

    needFetch = False

    def preparePad(padId, lastEdit, public):
        nonlocal needFetch

        if public is not None:
            public = public.decode('utf-8')
        else:
            if synchronous:
                public = getPublicStatus(padId, True)
            else:
                public = "Unavailable"
                needFetch = True

        if lastEdit is not None:
            lastEdit = lastEdit.decode('utf-8')
        else:
            if synchronous:
                lastEdit = getLastEdited(padId, True)
            else:
                lastEdit = "Unavailable"
                needFetch = True

        return {'name': humanPadName(padId),
                'id': padId,
                'url': settings.data['pad']['url'] + padId,
                'date': lastEdit,
                'public': public}

    # acquire mutex so if another thread fetches this group, we can read its data from redis after it is done
    if synchronous:
        mutex[group].acquire()

    padlist = [preparePad(p, le, pub) for p, le, pub in zip(padIds, lastEditPipe.execute(), publicPipe.execute())]

    # release mutex after fetching data
    if synchronous:
        mutex[group].release()

    # the data will be requested soon, so better start fetching
    if needFetch and not synchronous:
        Thread(target=getPadlist, args=[group, groupId, True]).start()

    return padlist


# set the public status of a pad
def getHtml(padId):
    data = { 'padID' : padId }
    r = requestHandler('getHTML', data)

    return r
