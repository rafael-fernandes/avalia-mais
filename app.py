from flask import Flask, render_template, request, redirect, url_for, flash
from database import Database

app = Flask(__name__)

app.secret_key = 'ppaH4u5LWhP2fVa3eM3ySLzfFiAdrMcs'

db = Database('database.db')

def get_perguntas():
  return {
    '1': 'O professor explicou o conteúdo de forma clara e compreensível?',
    '2': 'O ritmo da aula foi adequado?',
    '3': 'O material utilizado (slides, quadros, etc.) foi útil?',
    '4': 'O professor demonstrou domínio do assunto?',
    '5': 'A carga de trabalho da disciplina é adequada?',
    '6': 'O conteúdo da aula foi relevante para o curso?',
    '7': 'O professor utilizou exemplos práticos para ilustrar o conteúdo?',
    '8': 'O ambiente de aula (físico ou virtual) foi adequado?',
    '9': 'Você recomendaria este professor para outros alunos?',
    '10': 'O professor foi receptivo a dúvidas e questionamentos?'
  }

@app.before_request
def inicializa_banco():
  db.inicializa_o_banco()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['senha']

    usuario = db.autenticar_usuario(email, senha)
    
    if usuario:
      return redirect(url_for('enquetes'))
    else:
      return redirect(url_for('login'))

  return render_template('login.html')

@app.route('/enquetes', methods=['GET', 'POST'])
def enquetes():
  if request.method == 'GET':
    enquetes = db.recuperar_enquetes()

    return render_template('enquetes.html', enquetes=enquetes)
  elif request.method == 'POST':
    titulo = request.form['titulo']
    perguntas = request.form.getlist('perguntas[]')
    perguntas = ','.join(perguntas)

    if db.criar_enquete(titulo, perguntas):
      return redirect(url_for('enquetes'))
    else:
      return redirect(url_for('nova_enquete'))

@app.route('/nova_enquete', methods=['GET'])
def nova_enquete():
  perguntas = get_perguntas()

  return render_template('nova_enquete.html', perguntas=perguntas)

if __name__ == '__main__':
  app.run(debug=True)