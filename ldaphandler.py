import ldap

# own stuff
import settings

connect = ldap.initialize(settings.data['ldap']['server'])
connect.set_option(ldap.OPT_REFERRALS, 0)

# Establish ldap connection
def ldapConnect():
    connect.simple_bind_s(settings.data['ldap']['binddn'],
            settings.data['ldap']['bindpw'])

# bind to ldap
ldapConnect()

# get dn of a user
def getDn(uid):
    # Check if username is empty
    if uid == "":
        return False

    # first get the cn
    try:
        query = settings.data['ldap']['userfilter'] % uid
        ldap_user = connect.search_s(settings.data['ldap']['usertree'], 
                ldap.SCOPE_SUBTREE, query, ['cn'])
    except ldap.SERVER_DOWN:
        print("exception")
        ldapConnect()


    # User does not exist
    if len(ldap_user) == 0:
        return False

    return ldap_user[0][0]


# get groups of a user
def getGroups(uid):

    if uid == "":
        return []

    try:
        query = settings.data['ldap']['groupfilter'] % uid
        ldap_groups = connect.search_s(settings.data['ldap']['grouptree'],
                ldap.SCOPE_SUBTREE, query, ['cn'])

    except ldap.SERVER_DOWN:
        print("exception")
        ldapConnect()

    # Filter the relevant stuff
    buf = []
    for g in ldap_groups:
        buf.append(g[1]['cn'][0].decode('utf-8'))

    return buf


# Verifying login
def verifyPw(username, password):
    dn_user = getDn(username)

    if dn_user == False:
        return False

    # Check PW
    try:
        pw_test = ldap.initialize(settings.data['ldap']['server'])
        pw_test.bind_s(dn_user, password)
        pw_test.unbind_s()

    except ldap.LDAPError:
        return False

    return True
