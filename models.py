from flask_login import UserMixin

class User(UserMixin):
  def __init__(self, id, email, nome, senha, perfil):
    self.id = id
    self.email = email
    self.nome = nome
    self.senha = senha
    self.perfil = perfil

  def is_authenticated(self):
    return True

  def is_active(self):
    return True
