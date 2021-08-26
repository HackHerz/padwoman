import auth.auth
import settings
import auth.static
from importlib import import_module
from flask import session, request
from urllib.parse import quote_plus

SESSION_KEY_MECHANISM = 'authmulti-mechanism'

# Load authentication modules
methods = {}
for method in settings.data['auth']['multi']['methods']:
    methods[method['method']] = method
    method['AuthMechanism'] = getattr(import_module('auth.' + method['method']), 'AuthMechanism')
    method['User'] = getattr(import_module('auth.' + method['method']), 'User')

# Populate login template context
auth.auth.render_login_context['methods'] = methods.values()


class AuthMechanism(auth.auth.AuthMechanism):
    @staticmethod
    def login(User):
        active_method = methods.get(request.args.get('method', list(methods.keys())[0]))

        # Populate login template context
        auth.auth.render_login_context['active_method'] = active_method
        auth.auth.render_login_context['argstring'] = ''.join([quote_plus(k) + '=' + quote_plus(v) + '&' for k, v in request.args.items() if k != 'method'])

        # Save active method in session
        session[SESSION_KEY_MECHANISM] = active_method['method']
        return active_method['AuthMechanism'].login(User, active_method.get('userprefix', ""))

    @staticmethod
    def logout():
        method = methods.get(session.get(SESSION_KEY_MECHANISM, ""), None)
        if method is not None:
            return method['AuthMechanism'].logout()
        else:
            return super(AuthMechanism, AuthMechanism).logout()


class User(auth.auth.User):
    def __new__(cls, id, *args, **kwargs):
        method = methods.get(session.get(SESSION_KEY_MECHANISM, ""), list(methods.keys())[0])

        user = method['User'](id)
        user._multi_method = method

        return user

    def exists(self):
        origid = self.id
        self.id = self.id[len(self._multi_method.get('userprefix', "")):]
        ret = self._multi_orig_exists()
        self.id = origid

        return ret

    def populate(self):
        origid = self.id
        self.id = self.id[len(self._multi_method.get('userprefix', "")):]
        ret = self._multi_orig_populate()
        self.id = origid

        self.groups = set(self.groups + self._multi_method.get('defaultgroups', []))

        return ret


for method in methods.values():
    userclass = method['User']
    userclass._multi_orig_exists = userclass.exists
    userclass.exists = User.exists
    userclass._multi_orig_populate = userclass.populate
    userclass.populate = User.populate
