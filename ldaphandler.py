from ldappool import ConnectionManager
import ldap
import redis
import json

# own stuff
import settings

# Connection Manager
cm = ConnectionManager(settings.data['ldap']['server'],
        settings.data['ldap']['binddn'], settings.data['ldap']['bindpw'])

# Redis
red = redis.Redis(**settings.data['redis'])


class LdapHandler:

    def __init__(self, uid):
        self.userdata = None
        self.uid = uid
        self.redisKey = "ldap:uid:%s" % uid


    # get userdata from cache if exists
    def getCache(self):
        if self.uid != "":
            redisVal = red.get(self.redisKey)

            if redisVal == None:
                self.userdata = None
                return

            self.userdata = json.loads(redisVal.decode('utf-8'))


    # save data to the cache
    def setCache(self):
        if self.userdata != None:
            red.set(self.redisKey, json.dumps(self.userdata))

    
    # used when the cache data is known to be irrelevant
    def flushCache(self):
        red.delete(self.redisKey)

    # get the userdata
    def getLdapInfo(self):
        if self.uid == None:
            return

        # Check if data is in the cache
        self.getCache()
        if self.userdata != None:
            return

        # Proceed if data was not in cache
        self.userdata = {}

        print("LDAP....")

        # connection to the server
        with cm.connection() as conn:
            # first get the cn
            userquery = settings.data['ldap']['userfilter'] % self.uid
            ldap_user = conn.search_s(settings.data['ldap']['usertree'], 
                    ldap.SCOPE_SUBTREE, userquery, ['cn'])

            # User does not exist
            if len(ldap_user) == 0:
                self.userdata = None
                return

            # save values
            self.userdata['dn'] = ldap_user[0][0]
            self.userdata['cn'] = ldap_user[0][1]['cn'][0].decode('utf-8')

            # get the groups
            groupquery = settings.data['ldap']['groupfilter'] % self.uid
            ldap_groups = conn.search_s(settings.data['ldap']['grouptree'],
                    ldap.SCOPE_SUBTREE, groupquery, ['cn'])

            # Filter the relevant stuff
            self.userdata['groups'] = []
            for g in ldap_groups:
                self.userdata['groups'].append(g[1]['cn'][0].decode('utf-8'))

        # Save data in cache
        self.setCache()


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
        # we need everything fresh from ldap
        self.userdata = None
        self.flushCache()

        userDn = self.getDn()

        if userDn == False:
            return False

        # Check PW
        try:
            with cm.connection(userDn, password) as conn:
                pass

            cm.purge(userDn, password) # Purge this connection from the pool

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
