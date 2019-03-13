import ldap

# own stuff
import settings


class LdapHandler:

    def __init__(self, uid):
        self.userdata = None
        self.uid = uid


    # get the userdata
    def getLdapInfo(self):
        if self.uid == None:
            return

        self.userdata = {}

        # connection to the server
        self.connect = ldap.initialize(settings.data['ldap']['server'])
        self.connect.set_option(ldap.OPT_REFERRALS, 0)

        # bind
        self.connect.simple_bind_s(settings.data['ldap']['binddn'],
                settings.data['ldap']['bindpw'])

        # first get the cn
        userquery = settings.data['ldap']['userfilter'] % self.uid
        ldap_user = self.connect.search_s(settings.data['ldap']['usertree'], 
                ldap.SCOPE_SUBTREE, userquery, ['cn'])

        # User does not exist
        if len(ldap_user) == 0:
            self.userdata = None
            self.connect.unbind_s()
            return

        # save values
        self.userdata['dn'] = ldap_user[0][0]
        self.userdata['cn'] = ldap_user[0][1]['cn'][0]

        # get the groups
        groupquery = settings.data['ldap']['groupfilter'] % self.uid
        ldap_groups = self.connect.search_s(settings.data['ldap']['grouptree'],
                ldap.SCOPE_SUBTREE, groupquery, ['cn'])

        # Filter the relevant stuff
        self.userdata['groups'] = []
        for g in ldap_groups:
            self.userdata['groups'].append(g[1]['cn'][0])

        # unbind
        self.connect.unbind_s()


    # get dn of a user
    def getDn(self):
        if self.userdata == None:
            self.getLdapInfo()

        if self.userdata == None:
            return False

        return self.userdata['dn']


    # get groups of a user
    def getGroups(self):
        if self.userdata == None:
            self.getLdapInfo()

        if self.userdata == None:
            return []

        return self.userdata['groups']


    # Verifying login
    def verifyPw(self, password):
        # we need everythin fresh from ldap
        self.userdata = None

        userDn = self.getDn()

        if userDn == False:
            return False

        # Check PW
        try:
            pw_test = ldap.initialize(settings.data['ldap']['server'])
            pw_test.bind_s(userDn, password)
            pw_test.unbind_s()

        except ldap.LDAPError:
            return False

        return True


    # get the name from ldap
    def getCn(self):
        if self.userdata == None:
            self.getLdapInfo()

        # User does not exist
        if self.userdata == None:
            return "Britzel"

        return self.userdata['cn']
