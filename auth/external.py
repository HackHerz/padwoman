import auth.auth
import settings
from flask_login import login_user
from flask import request, redirect, url_for, make_response
from base64 import b64encode


def normalize_header(header):
    return header.encode("iso-8859-1").decode("utf-8")


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login(User, userprefix=""):
        hdr_uid = settings.data['auth']['external']['uid']
        if hdr_uid in request.headers:
            user = User(normalize_header(request.headers[hdr_uid]))
            user.updateIdWithPrefix(userprefix)
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        elif request.method == 'GET':
            return auth.auth.render_login()
        else:
            if 'login-url' in settings.data['auth']['external']:
                login_url = settings.data['auth']['external']['login-url']
                redirect_url = str(b64encode(request.url.encode("utf-8")), "utf-8")
                return redirect(login_url.replace('<redirect>', redirect_url))
            else:
                return auth.auth.render_login(loginFailed=True)

    @staticmethod
    def logout():
        if 'logout-url' in settings.data['auth']['external']:
            logout_url = settings.data['auth']['external']['logout-url']
            redirect_url = str(b64encode(url_for("login", _external=True).encode("utf-8")), "utf-8")
            resp = make_response(redirect(logout_url.replace('<redirect>', redirect_url)))
            for c in settings.data['auth']['external'].get('logout-cookies-delete', []):
                resp.set_cookie(c, '', expires=0)
            return resp
        else:
            return super(AuthMechanism, AuthMechanism).logout()


class User(auth.auth.User):
    def exists(self):
        hdr_uid = settings.data['auth']['external']['uid']
        return hdr_uid in request.headers and normalize_header(request.headers[hdr_uid]) == self.id

    def populate(self):
        if 'cn' in settings.data['auth']['external']:
            self.cn = normalize_header(request.headers.get(settings.data['auth']['external']['cn'], self.id))
        else:
            self.cn = self.id

        if 'groups' in settings.data['auth']['external']:
            group_str = normalize_header(request.headers.get(settings.data['auth']['external']['groups'], ""))
            self.groups = [x.strip() for x in group_str.split(';')]
        else:
            self.groups = []
