import flask_login
from flask import render_template, redirect, url_for


class AuthMechanism:
    @staticmethod
    def login():
        pass

    @staticmethod
    def logout():
        return redirect(url_for("login"))


class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id
        self.groups = []
        self.cn = "Britzel"

    def exists(self):
        pass

    def populate(self):
        pass
