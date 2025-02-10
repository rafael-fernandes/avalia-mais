from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from database import Database
from services import PerguntasService, EnqueteService
from models import User
from datetime import datetime, timedelta

db = Database('database.db')

# Rota para a página inicial
def index():
  if current_user.is_authenticated:
    return redirect(url_for(f"{current_user.perfil}_enquetes"))
  else:
    return redirect(url_for('login'))

# Rota para login
def login():
  if current_user.is_authenticated:
    return redirect(url_for(f"{current_user.perfil}_enquetes"))

  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['password']

    usuario = db.autenticar_usuario(email, senha)

    if usuario:
      user = User(usuario[0], usuario[1], usuario[2], usuario[3], usuario[4])
      login_user(user)

      return redirect(url_for(f"{user.perfil}_enquetes"))
    else:
      flash('Credenciais inválidas', 'danger')  # Flash de erro
      return redirect(url_for('login'))

  return render_template('login.html')

# Rota para cadastro
def cadastro():
  if request.method == 'POST':
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    perfil = request.form['perfil']

    if db.criar_usuario(nome, email, perfil, senha):
      usuario = db.autenticar_usuario(email, senha)
      user = User(usuario[0], usuario[1], usuario[2], usuario[3], usuario[4])
      login_user(user)

      flash('Cadastro realizado com sucesso!', 'success')
      return redirect(url_for('index'))
    else:
      flash('Erro ao cadastrar. Tente novamente.', 'danger')
      return redirect(url_for('cadastro'))

  return render_template('cadastro.html')

# Rota para logout
@login_required
def logout():
  logout_user()

  flash('Até a próxima!', 'success')
  return redirect(url_for('login'))

# Rota para mostrar enquetes
@login_required
def professor_enquetes():
  # Autorização
  if current_user.perfil != 'professor':
    return redirect(url_for('index'))

  if request.method == 'GET':
    page = request.args.get('page', 1, type=int)
    per_page = 5

    start = (page - 1) * per_page
    end = start + per_page

    enquetes = db.recuperar_enquetes(current_user.id)

    total_paginas = len(enquetes) // per_page
    ultima_pagina = len(enquetes) % per_page

    enquetes = enquetes[start:end]

    has_next = page < total_paginas or len(enquetes) == per_page and ultima_pagina != 0

    return render_template('professor/enquetes.html', enquetes=enquetes, page=page, has_next=has_next)

  elif request.method == 'POST':
    titulo = request.form['titulo']
    perguntas = request.form.getlist('perguntas[]')
    perguntas = ','.join(perguntas)
    prazo = request.form['prazo']

    if db.criar_enquete(titulo, perguntas, current_user.id, prazo):
      flash('Enquete criada com sucesso!', 'success')
      return redirect(url_for('professor_enquetes'))
    else:
      flash('Erro ao criar enquete. Tente novamente.', 'danger')
      return redirect(url_for('professor_nova_enquete'))

# Rota para mostrar enquetes disponíveis
@login_required
def aluno_enquetes():
  # Autorização
  if current_user.perfil != 'aluno':
    return redirect(url_for('index'))

  enquetes = db.recuperar_enquetes_disponiveis(current_user.id)

  for enquete in enquetes:
    enquete['prazo_expirado'] = datetime.strptime(enquete['prazo'], '%d/%m/%Y').date() < datetime.now().date()

  enquetes_respondidas = db.recuperar_enquetes_respondidas(current_user.id)

  return render_template('aluno/enquetes.html', enquetes=enquetes, enquetes_respondidas=enquetes_respondidas)

# Rota para nova enquete
@login_required
def professor_nova_enquete():
  # Autorização
  if current_user.perfil != 'professor':
    return redirect(url_for('index'))

  perguntas = PerguntasService.get_perguntas()
  
  return render_template('professor/nova_enquete.html', perguntas=perguntas)

# Rota para responder enquete
@login_required
def responder_enquete(enquete_id):
  # Autorização
  if current_user.perfil != 'aluno':
    return redirect(url_for('index'))

  enquete = db.recuperar_enquete(enquete_id)
  enquete['perguntas'] = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]
  enquete['professor'] = db.recuperar_usuario(enquete['usuario_id'])

  # Checa se a enquete já está expirada
  if datetime.strptime(enquete['prazo'], '%d/%m/%Y').date() < datetime.now().date():
    flash('Esta enquete já expirou!', 'danger')
    return redirect(url_for('aluno_enquetes'))

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

# Rota para ver resultados da enquete
@login_required
def professor_ver_resultados(enquete_id):
  # Autorização
  if current_user.perfil != 'professor':
    return redirect(url_for('index'))

  enquete = db.recuperar_enquete(enquete_id)
  enquete['perguntas'] = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]
  perguntas = PerguntasService.get_perguntas()

  respostas = db.recuperar_respostas(enquete_id)

  service = EnqueteService(respostas)

  perguntas_validas = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]

  # Filtra as médias e perguntas de acordo com as perguntas válidas
  medias = { key: service.media_respostas(int(key)) for key in perguntas.keys() if str(key) in perguntas_validas }
  perguntas_texto = { key: perguntas[key] for key in perguntas.keys() if str(key) in perguntas_validas }

  return render_template('professor/resultados.html', enquete=enquete,
                                                      perguntas=perguntas,
                                                      respostas=respostas,
                                                      medias=medias,
                                                      perguntas_texto=perguntas_texto)

# Rota para ver todas as enquetes
@login_required
def instituicao_enquetes():
  # Autorização
  if current_user.perfil != 'instituicao':
    return redirect(url_for('index'))
  
  enquetes = db.recuperar_enquetes()

  for enquete in enquetes:
    user = db.recuperar_usuario(enquete['usuario_id'])
    enquete['professor'] = user

  professores = db.recuperar_professores()

  # pluck 0 and 2 for each in professores
  professores = [ (professor[0], professor[2]) for professor in professores ]

  usuario_id = request.args.get('usuario_id')

  if usuario_id:
    enquetes = [ enquete for enquete in enquetes if enquete['usuario_id'] == int(usuario_id) ]

  return render_template('instituicao/enquetes.html', enquetes=enquetes, professores=professores, usuario_id=usuario_id)

# Rota para ver resultados da enquete
@login_required
def instituicao_ver_resultados(enquete_id):
  # Autorização
  if current_user.perfil != 'instituicao':
    return redirect(url_for('index'))
  
  enquete = db.recuperar_enquete(enquete_id)
  enquete['perguntas'] = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]
  enquete['professor'] = db.recuperar_usuario(enquete['usuario_id'])
  
  perguntas = PerguntasService.get_perguntas()

  respostas = db.recuperar_respostas(enquete_id)

  service = EnqueteService(respostas)

  perguntas_validas = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]

  # Filtra as médias e perguntas de acordo com as perguntas válidas
  medias = { key: service.media_respostas(int(key)) for key in perguntas.keys() if str(key) in perguntas_validas }
  perguntas_texto = { key: perguntas[key] for key in perguntas.keys() if str(key) in perguntas_validas }

  return render_template('instituicao/resultados.html', enquete=enquete,
                                                        perguntas=perguntas,
                                                        respostas=respostas,
                                                        medias=medias,
                                                        perguntas_texto=perguntas_texto)  

# Rota para ver respostas da enquete
@login_required
def aluno_ver_respostas(enquete_id):
  # Autorização
  if current_user.perfil != 'aluno':
    return redirect(url_for('index'))

  enquete = db.recuperar_enquete(enquete_id)
  enquete['perguntas'] = [pergunta.strip() for pergunta in enquete['perguntas'] if pergunta.strip()]
  enquete['professor'] = db.recuperar_usuario(enquete['usuario_id'])

  perguntas = PerguntasService.get_perguntas()

  respostas = db.recuperar_respostas(enquete_id, current_user.id)
  respostas = { resposta[0]: resposta[1] for resposta in respostas }
  
  return render_template('aluno/ver_respostas.html', enquete=enquete, perguntas=perguntas, respostas=respostas)
