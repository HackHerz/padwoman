import oyaml as yaml
from datetime import datetime
from jinja2 import Template

# Open Config file
stream = open('settings.yml', 'r')
data = yaml.load(stream, Loader=yaml.SafeLoader)

# make groups more accessible
groupDict = {}
for g in data['padgroups']:
    values = data['padgroups'][g]
    groupDict[values['name']] = values


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


# check if the group has a name suggestion
def groupHasPadnameSuggestion(group):
    if group not in groupDict.keys():
        return False

    return "padname" in groupDict[group].keys()


# check if the group name suggestion is mandatory
def groupPadnameSuggestionMandatory(group):
    # Mandatory is irrelevant if there is no name suggestion
    if not groupHasPadnameSuggestion(group):
        return False

    # if key exists check the value
    if "padnameismandatory" in groupDict[group].keys():
        return groupDict[group]['padnameismandatory']

    return False


# check if the group has a template
def groupHasTemplate(group):
    if group not in groupDict.keys():
        return False

    return "content" in groupDict[group].keys()


# check if the group template is mandatory
def groupTemplateMandatory(group):
    if groupHasTemplate(group):
        if "contentismandatory" in groupDict[group].keys():
            return groupDict[group]['contentismandatory']

    return False


# Helper
def render(template):
    t = Template(template)

    tDate = datetime.now().strftime('%Y-%m-%d')
    tTime = datetime.now().strftime('%H:%M')
    tDatetime = tDate + ' ' + tTime

    return t.render(date=tDate, time=tTime, datetime=tDatetime)


# render group template
def getGroupTemplate(group):
    if not groupHasTemplate:
        return None
    
    body = render(groupDict[group]['content'])
    return "<!DOCTYPE HTML><html><body>%s</body></html>" % body


# render group name
def getGroupPadname(group):
    if not groupHasPadnameSuggestion(group):
        return ""
    
    name = render(groupDict[group]['padname'])
    return name.replace(' ', '_')


