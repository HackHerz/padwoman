import auth.auth
from flask_login import login_user
from flask import request, redirect, url_for
from random import choices
from string import ascii_letters, digits


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login(User, userprefix=""):
        if request.method == 'GET':
            return auth.auth.render_login()

        user = User(''.join(choices(ascii_letters + digits, k=8)))
        user.updateIdWithPrefix(userprefix)
        login_user(user)
        return redirect(request.args.get('next') or url_for('index'))


class User(auth.auth.User):
    def exists(self):
        return True

    def populate(self):
        self.cn = self.id
        self.groups = []
