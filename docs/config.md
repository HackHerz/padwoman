# Configuration

Padwoman uses [YAML](https://yaml.org/) as its configuration style.


## Example Configuration

```yaml
default:
  title: Padserver
  secretkey: changeme

redis:
  host: redis

pad:
  apikey: changethistoyourkeys
  apiurl: http://etherpad:9001/api/
  url: https://pads.tld/p/

auth:
  method: ldap
  ldap:
    server: ldap://ldapserver:389
    usertree: ou=alluser,dc=blub,dc=de
    grouptree: ou=groups,dc=blub,dc=de
    userfilter: (&(uid=%s)(objectClass=posixAccount))
    groupfilter: (&(objectClass=posixGroup)(memberUID=%s))
    binddn: cn=www-data,dc=blub,dc=de
    bindpw: bindpw
  static:
    users:
      - uid: user1
        pw: user1
        cn: User 1
      - uid: admin1
        pw: $6$TChhNwMGF.1sn3yi$iJ2klrOEyGlGxOVImpIAq5Ak8J2iaVsSEFTkNONPv6F78FRD7X8UZP5Y/0BoQkf9v.Z99bjUn3qsi21M4LWZn/ #password
        cn: Admin 1
        groups: [admin]
  external:
    uid: Auth-User
    cn: Auth-Cn
    groups: Auth-Groups
    login-url: https://auth.example.com/?url=<redirect>
    logout-url: https://auth.example.com/?url=<redirect>&logout=1
    logout-cookies-delete: [ext-auth-cookie]
  multi:
    methods:
      - method: ldap
        name: LDAP
        defaultgroups: [admin]
      - method: static
        name: Static
        userprefix: static-
      - method: none
        name: None
        userprefix: none-
      - method: external
        name: SSO

padgroups:
  allgemein:
    name: Allgemein

  sitzung:
    name: Sitzung
    content: "<strong>Protokoll der Sitzung vom {{ date }}</strong><br>Beginn: 18 Uhr<br>Ende:&nbsp;<br>Anwesende:<br>Moderation:<br>Protokoll:<br><br><strong>Berichte</strong><br><br><strong>TOP 1</strong><br><br><strong>TOP 2</strong><br><br>"
    padname: "Sitzung_{{ date }}"
    padnameismandatory: true
    contentismandatory: true
    datetimeadjustable: true
    weekdaydefault: 2
    timedefault: "18:00"

  admins:
    name: Admins
	groups:
	  - admin
	user:
	  - hackherz
```

## Sections

### default

- **title** The title of your Padwoman instance
- **secretkey** Necessary for secure cookies

### redis

- **host** your redis host, mandatory

You can use every argument which is specififed by the python redis library.


### pad

- **apikey** the apikey of your etherpad-lite instance
- **apiurl** the (internal) url where the etherpad api is reachable from the padwoman host
- **url** the public url of your pads


### auth

- **method** must be one of the authentication modules in the auth/ folder

#### static

- **users** is a list of users with the following form:
  - **uid** The user id
  - **pw** The password in either hashed form or in plaintext
  - **cn** The common name (display name)
  - **groups** (optional) A list of groups the is is part of

Do not use plaintext passwords in production use!

You can generate hashed passwords in python with `crypt.crypt(password)`.

#### none

No configuration needed.

#### ldap
- **userfilter** expects a username (%s) as argument
- **groupfilter** expects a username (%s) as argument

#### external

- **uid** The HTTP header field name for the uid
- **cn** (optional) The HTTP header field name for the common name
- **groups** (optional) The HTTP header field name for the groups, which are seperated by a `;`
- **login-url** (optional) The URL where to redirect to for login. `<redirect>` will be replaced with the base64 encoded pad URL
- **logout-url** (optional) The URL where to redirect to for logout. `<redirect>` will be replaced with the base64 encoded pad URL
- **logout-cookies-delete** (optional) A list of cookies that are destroyed at logout

Do not use this method unless you have properly set up a reverse proxy that handles the authentication!

#### multi

- **methods** A list of authentication methods that can be used. The methods are in the following form:
  - **method** must be one of the authentication modules in the auth/ folder
  - **name** The name that gets displayed in the tabs on login
  - **defaultgroups** (optional) A list of groups that every user that authenticates through this method gets
  - **userprefix** (optional) A prefix that every user gets internally to distinguish users from different methods that have the same id. This can be intentionally be the same if you want to merge users from different authentication methods.


### padgroups

The groups are listed below an unique identifier, which is only used in the configuration (so the name does not really matter).

- **name** The Name of the group, it has to be unique.
- **padname** the suggested name for new pads
- **content** a simple html template for new pads
- **padnameismandatory** boolean if the suggested name of the pad is enforced or not
- **contentismandatory** boolean if the pad template is enforced or not
- **user** a list of usernames which are allowed to view the padgroup
- **groups** a list of ldap groups which are allowed to view the padgroup
- **datetimeadjustable** boolean if the date and/or time is a user input
- **weekdaydefault** (optional) the default weekday (iso number) from which the default date is calculated
- **timedefault** (optional) the default time


If there are no users or groups specified everyone who can login is allowed to view that padgroup.

**content** and **padname** have the following variables they can use ({{ variablename }}):

- **date** either the current date or user supplied (see datetimeadjustable)
- **time** either the current time or user supplied
- **datetime** either the current date and time or user supplied
