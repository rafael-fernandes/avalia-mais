from flask_login import UserMixin

class User(UserMixin):
  def __init__(self, id, email, nome, perfil):
    self.id = id
    self.email = email
    self.nome = nome
    self.perfil = perfil
