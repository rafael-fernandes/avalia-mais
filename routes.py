from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from database import Database
from services import PerguntasService
from models import User

db = Database('database.db')

# Rota para a página inicial
def index():
  # get current_user name from flask_login
  return render_template('index.html')

# Rota para login
def login():
  if current_user.is_authenticated:
    return redirect(url_for('enquetes'))

  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['password']

    usuario = db.autenticar_usuario(email, senha)

    if usuario:
      user = User(usuario[0], usuario[1], usuario[2])
      login_user(user)

      return redirect(url_for('professor_enquetes'))
    else:
      flash('Credenciais inválidas', 'danger')  # Flash de erro
      return redirect(url_for('login'))

  return render_template('login.html')

# Rota para logout
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

# Rota para mostrar enquetes
@login_required
def professor_enquetes():
  if request.method == 'GET':
    enquetes = db.recuperar_enquetes()
    return render_template('professor/enquetes.html', enquetes=enquetes)

  elif request.method == 'POST':
    titulo = request.form['titulo']
    perguntas = request.form.getlist('perguntas[]')
    perguntas = ','.join(perguntas)

    if db.criar_enquete(titulo, perguntas):
      flash('Enquete criada com sucesso!', 'success')
      return redirect(url_for('professor_enquetes'))
    else:
      flash('Erro ao criar enquete. Tente novamente.', 'error')
      return redirect(url_for('professor_nova_enquete'))

# Rota para nova enquete
@login_required
def professor_nova_enquete():
  perguntas = PerguntasService.get_perguntas()
  
  return render_template('professor/nova_enquete.html', perguntas=perguntas)
