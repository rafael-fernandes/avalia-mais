from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

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

# Configuração do banco de dados
def init_db():
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS enquetes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Chave primária com auto incremento
      titulo TEXT NOT NULL,                           -- Coluna 'titulo' para armazenar o título da enquete
      perguntas TEXT,                                 -- Coluna 'perguntas' para armazenar os IDs das perguntas como string
      criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Coluna 'criado_em' com timestamp de criação
    );
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Chave primária com auto incremento
      nome TEXT NOT NULL,                             -- Coluna 'nome' para armazenar o nome do usuário
      email TEXT NOT NULL UNIQUE,                     -- Coluna 'email', com a restrição UNIQUE para garantir que o email seja único
      senha TEXT NOT NULL,                            -- Coluna 'senha' para armazenar a senha do usuário
      criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Coluna 'criado_em' com timestamp de criação
    );
  ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS respostas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,                               -- Chave primária com auto incremento
      usuario_id INTEGER NOT NULL,                                        -- Chave estrangeira para 'usuarios'
      enquete_id INTEGER NOT NULL,                                        -- Chave estrangeira para 'enquetes'
      numero_pergunta INTEGER NOT NULL,                                   -- Número da pergunta
      resposta INTEGER NOT NULL CHECK(resposta >= 0 AND resposta <= 10),  -- Resposta numérica de 0 a 10
      criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                      -- Coluna 'criado_em' com timestamp de criação
      FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,  -- Chave estrangeira para 'usuario'
      FOREIGN KEY (enquete_id) REFERENCES enquetes(id) ON DELETE CASCADE  -- Chave estrangeira para 'enquetes'
    );
  ''')

  conn.commit()
  conn.close()

init_db()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    senha = request.form['senha']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha))
    usuario = cursor.fetchone()

    conn.close()

    if usuario:
      return redirect(url_for('enquetes'))
    else:
      return redirect(url_for('login'))

  return render_template('login.html')

@app.route('/enquetes')
def enquetes():
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute('SELECT * FROM enquetes')
  enquetes = cursor.fetchall()

  # mapeie enquetes para um objeto com os ids, títulos e perguntas
  enquetes = [{'id': enquete[0],
               'titulo': enquete[1],
               'perguntas': enquete[2],
               'criado_em': datetime.strptime(enquete[3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')}
               for enquete in enquetes]

  conn.close()

  return render_template('enquetes.html', enquetes=enquetes)

@app.route('/nova_enquete', methods=['GET'])
def nova_enquete():
  perguntas = get_perguntas()

  return render_template('nova_enquete.html', perguntas=perguntas)

if __name__ == '__main__':
  app.run(debug=True)