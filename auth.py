from flask_login import LoginManager
from database import Database

class Auth:
  def __init__(self, app):
    self.app = app
    self.db = Database('database.db')
    self.login_manager = LoginManager()
    self.login_manager.init_app(app)
    self.login_manager.login_view = "login"

    @self.login_manager.user_loader
    def load_user(user_id):
      return self.db.recuperar_usuario(user_id)
