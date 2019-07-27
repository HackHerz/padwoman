import flask_login
from flask import render_template, redirect, url_for


render_login_context = {}


def render_login(**context):
    return render_template('login.html', **context, **render_login_context)


class AuthMechanism:
    @staticmethod
    def login(User, userprefix=""):
        pass

    @staticmethod
    def logout():
        return redirect(url_for("login"))


class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id
        self.groups = []
        self.cn = "Britzel"

    def updateIdWithPrefix(self, prefix):
        self.id = prefix + self.id

    def exists(self):
        pass

    def populate(self):
        pass
