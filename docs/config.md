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

padgroups:
  allgemein:
    name: Allgemein

  sitzung:
    name: Sitzung
    content: "<strong>Protokoll der Sitzung vom {{ date }}</strong><br>Beginn: 18 Uhr<br>Ende:&nbsp;<br>Anwesende:<br>Moderation:<br>Protokoll:<br><br><strong>Berichte</strong><br><br><strong>TOP 1</strong><br><br><strong>TOP 2</strong><br><br>"
    padname: "Sitzung_{{ date }}"
    padnameismandatory: true
    contentismandatory: true

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

#### ldap
- **userfilter** expects a username (%s) as argument
- **groupfilter** expects a username (%s) as argument


### padgroups

The groups are listed below an unique identifier, which is only used in the configuration (so the name does not really matter).

- **name** The Name of the group, it has to be unique.
- **padname** the suggested name for new pads
- **content** a simple html template for new pads
- **padnameismandatory** boolean if the suggested name of the pad is enforced or not
- **contentismandatory** boolean if the pad template is enforced or not
- **user** a list of usernames which are allowed to view the padgroup
- **groups** a list of ldap groups which are allowed to view the padgroup


If there are no users or groups specified everyone who can login is allowed to view that padgroup.

**content** and **padname** have the following variables they can use ({{ variablename }}):

- **date** the current date
- **time** the current time
- **datetime** the current date and time
