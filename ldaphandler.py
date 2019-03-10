import ldap

# own stuff
import settings


class LdapHandler:

    # establish the connection
    def __init__(self):
        self.connect = ldap.initialize(settings.data['ldap']['server'])
        self.connect.set_option(ldap.OPT_REFERRALS, 0)

        self.connect.simple_bind_s(settings.data['ldap']['binddn'],
                settings.data['ldap']['bindpw'])


    # get dn of a user
    def getDn(self, uid):
        # Check if username is empty
        if uid == "":
            return False

        # first get the cn
        query = settings.data['ldap']['userfilter'] % uid
        ldap_user = self.connect.search_s(settings.data['ldap']['usertree'], 
                ldap.SCOPE_SUBTREE, query, ['cn'])

        # User does not exist
        if len(ldap_user) == 0:
            return False

        return ldap_user[0][0]


    # get groups of a user
    def getGroups(self, uid):

        if uid == "":
            return []

        query = settings.data['ldap']['groupfilter'] % uid
        ldap_groups = self.connect.search_s(settings.data['ldap']['grouptree'],
                ldap.SCOPE_SUBTREE, query, ['cn'])

        # Filter the relevant stuff
        buf = []
        for g in ldap_groups:
            buf.append(g[1]['cn'][0].decode('utf-8'))

        return buf


    # Verifying login
    def verifyPw(self, username, password):
        dn_user = self.getDn(username)

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


    # get the name from ldap
    def getCn(self, uid):
        # Check if username is empty
        if uid == "":
            return False

        # first get the cn
        query = settings.data['ldap']['userfilter'] % uid
        ldap_user = self.connect.search_s(settings.data['ldap']['usertree'], 
                ldap.SCOPE_SUBTREE, query, ['cn'])

        # User does not exist
        if len(ldap_user) == 0:
            return "Britzel"

        return ldap_user[0][1]['cn'][0]
