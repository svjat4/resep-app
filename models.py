from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

class Recipe:
    def __init__(self, id, title, content, category, user_id, image=None):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.user_id = user_id
        self.image = image
