from werkzeug.security import check_password_hash

class User:
    def __init__(self, username, email, password):    ##constructor class
        self.username=username
        self.email=email
        self.password=password

    @staticmethod
    def is_authenticated():
        return True   ## only for users who are actually authenticated

    @staticmethod ## because not using any class parameters
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input) ## take input as text and check from db which has hash pass