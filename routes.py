from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from database import Database
from services import PerguntasService
from models import User

db = Database('database.db')

# Rota para a página inicial
def index():
  if current_user.is_authenticated:
    return redirect(url_for('professor_enquetes'))
  
  return render_template('login.html')

# Rota para login
def login():
  if current_user.is_authenticated:
    return redirect(url_for(current_user.perfil + '_enquetes'))

  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['password']

    usuario = db.autenticar_usuario(email, senha)

    if usuario:
      user = User(usuario[0], usuario[1], usuario[2], usuario[3])
      login_user(user)

      if user.perfil == 'professor':
        return redirect(url_for('professor_enquetes'))
      elif user.perfil == 'aluno':
        return redirect(url_for('aluno_enquetes'))
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

# Rota para mostrar enquetes disponíveis
@login_required
def aluno_enquetes():
  enquetes = db.recuperar_enquetes_disponiveis(current_user.id)
  return render_template('aluno/enquetes.html', enquetes=enquetes)

# Rota para nova enquete
@login_required
def professor_nova_enquete():
  perguntas = PerguntasService.get_perguntas()
  
  return render_template('professor/nova_enquete.html', perguntas=perguntas)

# Rota para responder enquete
@login_required
def responder_enquete(enquete_id):
  enquete = db.recuperar_enquete(enquete_id)
  enquete['perguntas'] = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]

  perguntas = PerguntasService.get_perguntas()
  
  if request.method == 'POST':
    respostas = request.form.to_dict()

    respostas = [
      {
        "numero_pergunta": int(chave.split('[')[1].split(']')[0]),  # Extrai o número da pergunta
        "resposta": int(valor)  # Converte a resposta para inteiro
      }
      for chave, valor in respostas.items()
    ]

    # itere sobre as respostas e salve no banco de dados
    for resposta in respostas:
      db.salvar_resposta(current_user.id, enquete_id, resposta['numero_pergunta'], resposta['resposta'])

    flash('Enquete respondida com sucesso!', 'success')
    return redirect(url_for('aluno_enquetes'))
  elif request.method == 'GET':
    return render_template('aluno/responder_enquete.html', enquete=enquete, perguntas=perguntas)
