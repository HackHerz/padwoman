import flask_login


class AuthMechanism:
    @staticmethod
    def login():
        pass


class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id
        self.groups = []
        self.cn = "Britzel"

    def exists(self):
        pass

    def populate(self):
        pass
