import yaml

# Open Config file
stream = open('settings.yml', 'r')
data = yaml.load(stream)


# FIXME
# Returns the allowed padgroups for uid and ldapgroups
def getPadGroups(uid, groupids):
    buf = []

    for g in data['padgroups']:
        buf.append(data['padgroups'][g]['name'])

    return buf



def getSecretKey():
    key = data['default']['secretkey'] # FIXME
    return key

def getDefaultGroup(uid, groupids):
    return getPadGroups(uid, groupids)[0]

print(getDefaultGroup("", ""))
