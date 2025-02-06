from flask_login import UserMixin

class User(UserMixin):
  def __init__(self, id, email, nome):
    self.id = id
    self.email = email
    self.nome = nome
