from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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

if __name__ == '__main__':
  app.run(debug=True)