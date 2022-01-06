import requests
import redis
import json
from datetime import datetime, timedelta

# own stuff
import settings


# setup redis
red = redis.Redis(**settings.data['redis'])


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
    if rVal != None:
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
    if rVal != None:
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
def listPads(groupId):
    data = { 'groupID' : groupId }
    r = requestHandler('listPads', data)

    # everything was ok
    if r['code'] == 0:
        return r['data']['padIDs']

    # Otherwise
    return []


# returns the timestamp of the last revision of the pad
def getLastEdited(padId):
    data = { 'padID' : padId }
    r = requestHandler('getLastEdited', data)

    # everything was ok
    if r['code'] == 0:
        timestamp = int(r['data']['lastEdited']) / 1000
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

    # Otherwise
    return "0"

# returns if the pad is public
def getPublicStatus(padId):
    data = { 'padID' : padId }
    r = requestHandler('getPublicStatus', data)

    # everything was ok
    if r['code'] == 0:
        return r['data']['publicStatus']

    # Otherwise
    return False

# set the public status of a pad
def setPublicStatus(padId, publicStatus):
    red.delete("pad:public:%s" % padId)

    data = { 'padID' : padId,
            'publicStatus' : "true" if publicStatus else "false" }

    r = requestHandler('setPublicStatus', data)

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


# Calcualte the time before expiration
def calcExpTime(datum):
    if(len(datum) < 10):
        return 60

    year = int(datum[0:4])
    month = int(datum[5:7])
    day = int(datum[8:10])

    dStamp = datetime(year, month, day)
    delta = datetime.now() - dStamp

    value = delta.days * 20 # 20s per day

    # Min and max values
    if value < 60:
        return 60

    if value > 3600:
        return 3600

    return value


# caching is fun
def getPadsFromCache(groupId):
    padsInGroup = []

    # Check Cache for the list of pads
    redisKey = "padlist:%s" % groupId
    cacheVal = red.get(redisKey)

    # Was not in cache
    if cacheVal == None:
        padsInGroup = listPads(groupId)
        red.set(redisKey, json.dumps(padsInGroup))
    else:
        padsInGroup = json.loads(cacheVal.decode('utf-8'))

    return padsInGroup


# returns a list of all pads and their necessary values
def getPadlist(groupId):
    padsInGroup = getPadsFromCache(groupId)

    # gather information of these pads
    lastEditPipe = red.pipeline()
    publicPipe = red.pipeline()

    # Load Values from Cache
    for p in padsInGroup:
        lastEditPipe.get("pad:lastEdit:%s" % p)
        publicPipe.get("pad:public:%s" % p)

    # execute pipes
    lastEditResp = lastEditPipe.execute()
    publicRespo = publicPipe.execute()

    cacheUpdate = red.pipeline()
    padlist = []

    # Check where values are missing
    for i in range(0, len(padsInGroup)):
        # Public Value
        if publicRespo[i] == None:
            pub = getPublicStatus(padsInGroup[i])
            cacheUpdate.set("pad:public:%s" % padsInGroup[i], str(pub))
            publicRespo[i] = pub
        else:
            publicRespo[i] = bool(publicRespo[i].decode('utf-8') == "True") # convert from string to boolean

        # Last edited value
        if lastEditResp[i] == None:
            tm = getLastEdited(padsInGroup[i])
            lastEditResp[i] = tm
            cacheUpdate.set("pad:lastEdit:%s" % padsInGroup[i], tm,
                    calcExpTime(tm))

        else:
            lastEditResp[i] = lastEditResp[i].decode('utf-8')

        # Current pad
        p = padsInGroup[i]

        padlist.append({ 'title' : humanPadName(p),
            'id' : p,
            'url' : settings.data['pad']['url'] + p,
            'date' : lastEditResp[i],
            'public' : publicRespo[i] })

    # perform actual cache update
    cacheUpdate.execute()

    return padlist


# set the public status of a pad
def getHtml(padId):
    data = { 'padID' : padId }
    r = requestHandler('getHTML', data)

    return r
