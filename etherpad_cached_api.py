import requests
import redis
from datetime import datetime

# own stuff
import settings


# setup redis
red = redis.Redis(host='localhost')


def requestHandler(endpoint, data):
    data['apikey'] = settings.data['pad']['apikey']
    r = requests.get(settings.data['pad']['apiurl'] + '1.2/' + endpoint,
            params=data)
    
    return r.json()


# creates a new pad in this group 
# TODO: invalidate certain caches
def createGroupPad(groupID, padName):
    data = { 'groupID' : groupID,
            'padName' : padName }

    r = requestHandler('createGroupPad', data)


# this functions helps you to map your application author ids to etherpad lite author ids 
def createAuthorIfNotExistsFor(uid, cn):
    redisKey = 'author:' + uid
    rVal = red.get(redisKey)

    # trying the cache
    if rVal != None:
        return rVal

    data = { 'authorMapper' : uid }
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
        return rVal

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
    return 0

# returns if the pad is public
def getPublicStatus(padId):
    data = { 'padID' : padId }
    r = requestHandler('getPublicStatus', data)

    # everything was ok
    if r['code'] == 0:
        return r['data']['publicStatus']

    # Otherwise
    return False
