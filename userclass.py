# User Configuration
import flask_login

class User(flask_login.UserMixin):
    groups = []

    # Class to collect the ldap groups
    def getGroups(self):
        return self.groups

