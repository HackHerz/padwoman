import yaml

# Open Config file
stream = open('settings.yml', 'r')
data = yaml.load(stream)


# Returns the allowed padgroups for uid and ldapgroups
def getPadGroups(uid, groupids):
    buf = []

    for g in data['padgroups']:
        groupIter = data['padgroups'][g]

        hasUserKey = "user" in groupIter.keys()
        hasGroupKey = "groups" in groupIter.keys()

        # If both keys dont exist everyone has access
        if not hasGroupKey and not hasUserKey:
            buf.append(groupIter['name'])
            continue

        # check for username
        if hasUserKey and uid in groupIter['user']:
            buf.append(groupIter['name'])
            continue

        # Check for groups
        if hasGroupKey:
            if any(gu in groupIter["groups"] for gu in groupids):
                buf.append(groupIter['name'])
                continue

    return buf



def getSecretKey():
    key = data['default']['secretkey'] # FIXME
    return key


def getDefaultGroup(uid, groupids):
    return getPadGroups(uid, groupids)[0]


# Check if the group has a template
def groupHasTemplate(groupid):
    for g in data['padgroups']:
        groupData = data['padgroups'][g]

        if groupData['name'] == groupid and "content" in groupData.keys():
            return True

    return False
