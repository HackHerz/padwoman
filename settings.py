import oyaml as yaml
import datetime
from jinja2 import Template
from re import search, sub

# Open Config file
stream = open('settings.yml', 'r')
data = yaml.load(stream, Loader=yaml.SafeLoader)

# make groups more accessible
groupDict = {}
for g in data['padgroups']:
    values = data['padgroups'][g]
    groupDict[values['name']] = values

# retain backwards compatibility with old configs
if 'auth' not in data.keys():
    data['auth'] = {'method': 'ldap'}
    data['auth']['ldap'] = data['ldap']


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


# check if the datetime is adjustable for the group
def datetimeAdjustable(group):
    if group in groupDict.keys():
        if "datetimeadjustable" in groupDict[group].keys():
            return groupDict[group]['datetimeadjustable']

    return False


# calculate default date from defaultweekday
def getDateDefault(group):
    if group in groupDict.keys():
        if "weekdaydefault" in groupDict[group].keys():
            weekdaydefault = max(1, min(7, int(groupDict[group]['weekdaydefault'])))
            d = datetime.date.today()
            while d.isoweekday() != weekdaydefault:
                d += datetime.timedelta(1)
            return d.strftime("%Y-%m-%d")

    return ""

# check if either the name or content include the date
def groupHasDate(group):
    if group in groupDict.keys():
        pattern = "{{ *date(time)? *}}"
        return (search(pattern, groupDict[group].get('padname', "")) is not None
                or search(pattern, groupDict[group].get('content', "")) is not None)
    return False


# check if either the name or content include the date
def groupHasTime(group):
    if group in groupDict.keys():
        pattern = "{{ *(date)?time *}}"
        return (search(pattern, groupDict[group].get('padname', "")) is not None
                or search(pattern, groupDict[group].get('content', "")) is not None)
    return


# Helper
def render(template, timestamp):
    t = Template(template)

    tDate = timestamp.strftime('%Y-%m-%d')
    tTime = timestamp.strftime('%H:%M')
    tDatetime = tDate + ' ' + tTime

    return t.render(date=tDate, time=tTime, datetime=tDatetime)


# render group template
def getGroupTemplate(group, timestamp):
    if not groupHasTemplate:
        return None

    body = render(groupDict[group]['content'], timestamp)
    return "<!DOCTYPE HTML><html><body>%s</body></html>" % body


# render group name
def getGroupPadname(group):
    if not groupHasPadnameSuggestion(group):
        return ""

    return sub(r" (?![^{]*}})", '_', groupDict[group]['padname'])
