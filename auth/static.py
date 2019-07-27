import auth.auth
import settings
from crypt import crypt
from hmac import compare_digest as compare_hash
from flask import request, redirect, url_for
from flask_login import login_user

# make users more accessible
userDict = {}
for user in settings.data['auth']['static']['users']:
    userDict[user['uid']] = user


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login(User, userprefix=""):
        if request.method == 'GET':
            return auth.auth.render_login(showUsername=True, showPassword=True)

        # Check if there is data to login the user
        if 'username' in request.form.keys() and 'password' in request.form.keys():
            username = request.form['username']

            user = User(username)

            # redirect to index if credentials are correct
            if user.verifyPw(request.form['password']):
                user.updateIdWithPrefix(userprefix)
                login_user(user)

                return redirect(request.args.get('next') or url_for('index'))

        return auth.auth.render_login(showUsername=True, showPassword=True, loginFailed=True)


class User(auth.auth.User):
    def exists(self):
        return self.id in userDict.keys()

    def populate(self):
        self.cn = userDict[self.id].get('cn', "Britzel")
        self.groups = userDict[self.id].get('groups', [])

    def verifyPw(self, password):
        if self.id not in userDict.keys() or 'pw' not in userDict[self.id]:
            return False

        pw = userDict[self.id]['pw']

        if pw.startswith('$'):
            return compare_hash(pw, crypt(password, pw))
        else:
            return password == pw
