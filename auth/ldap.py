from ldappool import ConnectionManager
import ldap
import redis
import json
from flask import request, redirect, url_for, render_template
from flask_login import login_user

# own stuff
import auth.auth
import settings

# Connection Manager
cm = ConnectionManager(settings.data['auth']['ldap']['server'],
        settings.data['auth']['ldap']['binddn'], settings.data['auth']['ldap']['bindpw'])

# Redis
red = redis.Redis(**settings.data['redis'])


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login():
        if request.method == 'GET':
            return render_template('login.html', showUsername=True, showPassword=True)

        # Check if there is data to login the user
        if 'username' in request.form.keys() and 'password' in request.form.keys():
            username = request.form['username']

            user = User(username)

            # redirect to index if credentials are correct
            if user.verifyPw(request.form['password']):
                login_user(user)

                return redirect(request.args.get('next') or url_for('index'))

        return render_template('login.html', showUsername=True, showPassword=True, loginFailed=True)


class User(auth.auth.User):
    def __init__(self, id):
        super(User, self).__init__(id)
        self.userdata = None
        self.redisKey = "ldap:uid:%s" % id

    def exists(self):
        if self.__getDn() == False:
            return False
        else:
            return True

    def populate(self):
        if self.userdata == None:
            self.__getLdapInfo()

        if self.userdata == None:
            self.groups = []
            self.cn = "Britzel"
        else:
            self.groups = self.userdata['groups']
            self.cn = self.userdata['cn']

    def verifyPw(self, password):
        # we need everything fresh from ldap
        self.userdata = None
        self.__flushCache()

        userDn = self.__getDn()

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

    # get userdata from cache if exists
    def __getCache(self):
        if self.id != "":
            redisVal = red.get(self.redisKey)

            if redisVal == None:
                self.userdata = None
                return

            self.userdata = json.loads(redisVal.decode('utf-8'))

    # save data to the cache
    def __setCache(self):
        if self.userdata != None:
            red.set(self.redisKey, json.dumps(self.userdata))

    # used when the cache data is known to be irrelevant
    def __flushCache(self):
        red.delete(self.redisKey)

    # get the userdata
    def __getLdapInfo(self):
        if self.id == None:
            return

        # Check if data is in the cache
        self.__getCache()
        if self.userdata != None:
            return

        # Proceed if data was not in cache
        self.userdata = {}

        print("LDAP....")

        # connection to the server
        with cm.connection() as conn:
            # first get the cn
            userquery = settings.data['auth']['ldap']['userfilter'] % self.id
            ldap_user = conn.search_s(settings.data['auth']['ldap']['usertree'],
                    ldap.SCOPE_SUBTREE, userquery, ['cn'])

            # User does not exist
            if len(ldap_user) == 0:
                self.userdata = None
                return

            # save values
            self.userdata['dn'] = ldap_user[0][0]
            self.userdata['cn'] = ldap_user[0][1]['cn'][0].decode('utf-8')

            # get the groups
            groupquery = settings.data['auth']['ldap']['groupfilter'] % self.id
            ldap_groups = conn.search_s(settings.data['auth']['ldap']['grouptree'],
                    ldap.SCOPE_SUBTREE, groupquery, ['cn'])

            # Filter the relevant stuff
            self.userdata['groups'] = []
            for g in ldap_groups:
                self.userdata['groups'].append(g[1]['cn'][0].decode('utf-8'))

        # Save data in cache
        self.__setCache()

    # get dn of a user
    def __getDn(self):
        if self.userdata == None:
            self.__getLdapInfo()

        if self.userdata == None:
            return False

        return self.userdata['dn']
