from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from routes import index, login, logout, enquetes, nova_enquete
from database import Database

app = Flask(__name__)

app.secret_key = 'ppaH4u5LWhP2fVa3eM3ySLzfFiAdrMcs'

db = Database('database.db')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  return db.recuperar_usuario(user_id)

@app.before_request
def inicializa_banco():
  db.inicializa_o_banco()

app.add_url_rule('/', 'index', index)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/enquetes', 'enquetes', enquetes, methods=['GET', 'POST'])
app.add_url_rule('/nova_enquete', 'nova_enquete', nova_enquete)

if __name__ == '__main__':
  app.run(debug=True)