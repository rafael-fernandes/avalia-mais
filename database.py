import sqlite3
from flask import flash
from datetime import datetime
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
  def __init__(self, db_name):
    self.db_name = db_name

  def _connect(self):
    """Conecta ao banco de dados e retorna a conexão"""
    return sqlite3.connect(self.db_name)

  def inicializa_o_banco(self):
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS enquetes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          titulo TEXT NOT NULL,
          perguntas TEXT,
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      ''')

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nome TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          senha TEXT NOT NULL,
          perfil TEXT DEFAULT 'aluno',
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      ''')

      cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          usuario_id INTEGER NOT NULL,
          enquete_id INTEGER NOT NULL,
          numero_pergunta INTEGER NOT NULL,
          resposta INTEGER NOT NULL CHECK(resposta >= 0 AND resposta <= 10),
          criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
          FOREIGN KEY (enquete_id) REFERENCES enquetes(id) ON DELETE CASCADE
        );
      ''')

      conn.close()
    except Exception as e:
      flash('Erro ao inicializar o banco de dados: ' + str(e))

  def criar_usuario(self, nome, email, perfil, senha):
    """Cria um novo usuário no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO usuarios (nome, email, perfil, senha) VALUES (?, ?, ?, ?)', (nome, email, perfil, generate_password_hash(senha)))

      conn.commit()
      conn.close()

      return True
    except Exception as e:
      return False

  def recuperar_usuario(self, id):
    """Recupera um usuário pelo ID"""
    conn = self._connect()
    cursor = conn.cursor()

    cursor.execute('SELECT id, email, nome FROM usuarios WHERE id = ?', (id,))
    usuario = cursor.fetchone()

    conn.close()

    if usuario:
      return User(usuario[0], usuario[1], usuario[2])
    else:
      return None

  def autenticar_usuario(self, email, senha):
    """Autentica um usuário no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
      usuario = cursor.fetchone()

      conn.close()

      if usuario and check_password_hash(usuario[3], senha):
        return usuario
      else:
        return None
    except Exception as e:
      flash('Erro ao autenticar usuário: ' + str(e))
      return None

  def recuperar_enquetes(self):
    """Retorna todas as enquetes do banco de dados"""
    try:
      conn = self._connect()
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

      return enquetes
    except Exception as e:
      flash('Erro ao buscar enquetes: ' + str(e))
      return []

  def criar_enquete(self, titulo, perguntas):
    """Cria uma nova enquete no banco de dados"""
    try:
      conn = self._connect()
      cursor = conn.cursor()

      cursor.execute('INSERT INTO enquetes (titulo, perguntas, criado_em) VALUES (?, ?, ?)', (titulo, ','.join(perguntas), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

      conn.commit()
      conn.close()

      return True
    except Exception as e:
      return False