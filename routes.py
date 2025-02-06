from flask import render_template, request, redirect, url_for, flash
from database import Database
from services import PerguntasService

db = Database('database.db')

# Rota para a página inicial
def index():
  return render_template('index.html')

# Rota para login
def login():
  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['senha']

    usuario = db.autenticar_usuario(email, senha)

    if usuario:
      return redirect(url_for('enquetes'))
    else:
      flash('Credenciais inválidas', 'error')  # Flash de erro
      return redirect(url_for('login'))

  return render_template('login.html')

# Rota para mostrar enquetes
def enquetes():
  if request.method == 'GET':
    enquetes = db.recuperar_enquetes()
    return render_template('enquetes.html', enquetes=enquetes)

  elif request.method == 'POST':
    titulo = request.form['titulo']
    perguntas = request.form.getlist('perguntas[]')
    perguntas = ','.join(perguntas)

    if db.criar_enquete(titulo, perguntas):
      flash('Enquete criada com sucesso!', 'success')
      return redirect(url_for('enquetes'))
    else:
      flash('Erro ao criar enquete. Tente novamente.', 'error')
      return redirect(url_for('nova_enquete'))

# Rota para nova enquete
def nova_enquete():
  perguntas = PerguntasService.get_perguntas()
  
  return render_template('nova_enquete.html', perguntas=perguntas)
