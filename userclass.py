# User Configuration
import flask_login

class User(flask_login.UserMixin):
    # Class to collect the ldap groups
    def getGroups():
        print(self.uid)

        fake_groups = [
                { 'name' : 'Allgemein', 'id' : 'allgemein' },
                { 'name' : 'Sitzung', 'id' : 'sitzung' },
                { 'name' : 'Redaktion', 'id' : 'redaktion' },
                { 'name' : 'Admins', 'id' : 'admins' },
                ]

        return fake_groups

    def groupAllowed(groupName):
        return True # FIXME

"""
    - Wenn User Attribute nicht im Redis sind dann schaue im LDAP nach
    - Passwort verifizieren macht LDAP_Handler
    - Wie config integrieren? -> eigene instanz der Config Klasse
"""
