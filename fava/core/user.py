"""This module contains Fava's user handling."""
users = {
    'test_user_1': {'password': 'a very secure password'},
    'test_user_2': {'password': 'another very secure password'},
}


class FavaUser:
    def __init__(self, username):
        self.username = username
        self.is_active = True
        self.is_anonymous = False

    @property
    def is_authenticated(self):
        if self.username not in users:
            return False
        if users[self.username].get('authenticated'):
            return True
        else:
            return False

    @is_authenticated.setter
    def is_authenticated(self, v):
        if self.username not in users:
            return
        users[self.username]['authenticated'] = True

    def get_id(self):
        return self.username


def decorate_user(login_manager):
    @login_manager.user_loader
    def load_user(username):
        if username not in users:
            return None
        print(users[username])
        return FavaUser(username)


def try_login_from_post(request):
    username = request.form.get('username')
    if username not in users:
        print('invalid username', username)
        return None

    user = FavaUser(username)

    authed = request.form['password'] == users[username]['password']
    if authed:
        user.is_authenticated = True
        return user
    return None
