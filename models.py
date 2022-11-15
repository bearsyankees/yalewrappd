from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):

        user = User(
            id_=0, name="bla", email="bla", profile_pic="bla"
        )
        return user
