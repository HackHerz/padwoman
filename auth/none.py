import auth.auth
from flask_login import login_user
from flask import request, redirect, url_for, render_template
from random import choices
from string import ascii_letters, digits


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login():
        if request.method == 'GET':
            return render_template('login.html')

        user = User(''.join(choices(ascii_letters + digits, k=8)))
        login_user(user)
        return redirect(request.args.get('next') or url_for('index'))


class User(auth.auth.User):
    def exists(self):
        return True

    def populate(self):
        self.cn = self.id
        self.groups = []
